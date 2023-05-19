from main import WQSession
import time
import logging
import csv
import pandas as pd
from concurrent.futures import as_completed, ThreadPoolExecutor

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')

team_params = {
    'status':               'ACTIVE',
    'members.self.status':  'ACCEPTED',
    'order':                '-dateCreated'
}

OFFSET, LIMIT = 0, 30
def get_link(x):
    return f'https://api.worldquantbrain.com/users/self/alphas?limit={LIMIT}&offset={x}&stage=IS%1fOS&is.sharpe%3E=1.25&is.turnover%3E=0.01&is.fitness%3E=1&status=UNSUBMITTED&dateCreated%3E=2023-05-16T00:00:00-04:00&order=-dateCreated&hidden=false'

wq = WQSession()
r = wq.get('https://api.worldquantbrain.com/users/self/teams', params=team_params).json()
team_id = r['results'][0]['id']

def scrape(result):
    alpha = result['regular']['code']
    settings = result['settings']
    aid = result['id']
    passed = sum(check['result'] == 'PASS' for check in result['is']['checks'])
    failed = sum(check['result'] in ['FAIL', 'ERROR'] for check in result['is']['checks'])
    if failed != 0: return -1

    # score check
    while True:
        compare_r = wq.get(f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{aid}/before-and-after-performance')
        if compare_r.content:
            try:    score = compare_r.json()['score']; break
            except: pass
        time.sleep(2.5)
    if score['after'] <= score['before']: return -1

    # correlation check, prone to throttling
    while True:
        corr_r = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/correlations/self')
        if corr_r.content:
            try:
                max_corr = max(record[5] for record in corr_r.json()['records'])
                if max_corr > 0.7:
                    logging.info(f'Skipping alpha due to high correlation of {max_corr}')
                    return -1
                score['max_corr'] = max_corr
                break
            except:
                try:    logging.info(f'Correlation check throttled(?): {corr_r.json()}')
                except: logging.info(f'Issue found when checking correlation: {corr_r.content}')
                score['max_corr'] = -1
                break
        else:
            time.sleep(2.5)

    # merge everything else
    score |= settings
    score['passed'], score['alpha'], score['link'] = passed, alpha, f'https://platform.worldquantbrain.com/alpha/{aid}'
    logging.info(f'Success!\n{score}')
    return score

ret = []
with open(f'alpha_scrape_result_{int(time.time())}_temp.csv', 'w', newline='') as c:
    writer = csv.DictWriter(c, fieldnames='before,after,max_corr,instrumentType,region,universe,delay,decay,neutralization,truncation,pasteurization,unitHandling,nanHandling,language,visualization,passed,alpha,link'.split(','))
    writer.writeheader()
    c.flush()
    with ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while True:
                r = wq.get(get_link(OFFSET)).json()
                logging.info(f'Obtained data of alphas #{OFFSET+1}-#{OFFSET+LIMIT}')
                for f in as_completed([executor.submit(scrape, result) for result in r['results']]):
                    res = f.result()
                    if res != -1:
                        ret.append(res)
                        writer.writerow(res)
                        c.flush()
                OFFSET += LIMIT
                if not r['next']: break
        except Exception as e:
            logging.info(f'{type(e).__name__}: {e}')
            try:    logging.info(r.content)
            except: pass
pd.DataFrame(ret).sort_values(by='after', ascending=False).to_csv(f'alpha_scrape_result_{int(time.time())}.csv', index=False)
