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
    return f'https://api.worldquantbrain.com/users/self/alphas?limit={LIMIT}&offset={x}&stage=IS%1fOS&is.sharpe%3E=1.25&is.turnover%3E=0.01&is.fitness%3E=1&status=UNSUBMITTED&dateCreated%3E=2023-05-14T00:00:00-04:00&order=-dateCreated&hidden=false'

wq = WQSession()
r = wq.get('https://api.worldquantbrain.com/users/self/teams', params=team_params).json()
team_id = r['results'][0]['id']
r = wq.get(get_link(OFFSET)).json()
ret = []
try:
    while True:
        for result in r['results']:
            alpha = result['regular']['code']
            aid = result['id']
            passed = sum(check['result'] == 'PASS' for check in result['is']['checks'])
            if passed != 7: continue
            while True:
                compare_r = wq.get(f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{aid}/before-and-after-performance')
                if compare_r.content: break
                time.sleep(2.5)
            ret.append(compare_r.json()['score'])
            ret[-1]['link'], ret[-1]['passed'], ret[-1]['alpha'] = f'https://platform.worldquantbrain.com/alpha/{aid}', passed, alpha
            print(ret[-1], flush=True)
        OFFSET += LIMIT
        if not r['next']: break
        r = wq.get(get_link(OFFSET)).json()
except:
    pass
pd.DataFrame(ret).sort_values(by='after', ascending=False).to_csv(f'alpha_scrape_result_{int(time.time())}.csv', index=False)