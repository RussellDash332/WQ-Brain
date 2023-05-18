from main import WQSession
import time
import pandas as pd

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
r = wq.get(get_link(OFFSET)).json()
ret = []
try:
    while True:
        for result in r['results']:
            alpha = result['regular']['code']
            settings = result['settings']
            aid = result['id']
            passed = sum(check['result'] == 'PASS' for check in result['is']['checks'])
            failed = sum(check['result'] in ['FAIL', 'ERROR'] for check in result['is']['checks'])
            if failed != 0: continue
            while True:
                compare_r = wq.get(f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{aid}/before-and-after-performance')
                if compare_r.content: break
                time.sleep(2.5)
            score = compare_r.json()['score']
            if score['after'] <= score['before']: continue
            ret.append(score)
            while True:
                corr_r = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/correlations/self')
                if corr_r.content: break
                time.sleep(2.5)
            try:
                max_corr = max(record[5] for record in corr_r.json()['records'])
                if max_corr >= 0.8: ret.oop(); continue
                ret[-1]['max_corr'] = max_corr
            except:
                ret[-1]['max_corr'] = 'THROTTLED'
            ret[-1] |= settings
            ret[-1]['passed'], ret[-1]['alpha'], ret[-1]['link'] = passed, alpha, f'https://platform.worldquantbrain.com/alpha/{aid}'
            print(ret[-1], flush=True)
        OFFSET += LIMIT
        if not r['next']: break
        r = wq.get(get_link(OFFSET)).json()
except Exception as e:
    print(f'{type(e).__name__}: {e}')
pd.DataFrame(ret).sort_values(by='after', ascending=False).to_csv(f'alpha_scrape_result_{int(time.time())}.csv', index=False)