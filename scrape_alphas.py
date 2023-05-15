from main import WQSession
import time
import pandas as pd

team_params = {
    'status':               'ACTIVE',
    'members.self.status':  'ACCEPTED',
    'order':                '-dateCreated'
}

alpha_params = {
    'limit':            30,
    'offset':           0,
    'stage':            'ISOS',
    'is.sharpe>':       1.25,
    'is.turnover>':     0.01,
    'is.turnover<':     0.7,
    'is.fitness<':      1,
    'dateCreated>':     '2023-05-14T00:00:00-04:00',
    'order':            '-dateCreated',
    'hidden':           'false'
}

wq = WQSession()
r = wq.get('https://api.worldquantbrain.com/users/self/teams', params=team_params).json()
team_id = r['results'][0]['id']
r = wq.get('https://api.worldquantbrain.com/users/self/alphas', params=alpha_params).json()
ret = []
while True:
    if not r['next']: break
    for result in r['results']:
        aid = result['id']
        passed = sum(check['result'] == 'PASS' for check in result['is']['checks'])
        if passed != 7: continue
        while True:
            compare_r = wq.get(f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{aid}/before-and-after-performance')
            if compare_r.content: break
            time.sleep(2.5)
        ret.append(compare_r.json()['score'])
        ret[-1]['link'] = f'https://platform.worldquantbrain.com/alpha/{aid}'
        print(ret[-1], flush=True)
    alpha_params['offset'] += alpha_params['limit']
    r = wq.get('https://api.worldquantbrain.com/users/self/alphas', params=alpha_params).json()
pd.DataFrame(ret).to_csv(f'alpha_scrape_result_{time.time()}.csv', index=False)