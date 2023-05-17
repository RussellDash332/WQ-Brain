import csv, json
import logging
import requests
import json
import time
from parameters import DATA

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')

class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        with open(json_fn, 'r') as f:
            creds = json.loads(f.read())
            r = self.post('https://api.worldquantbrain.com/authentication', headers=creds['headers'])
        if 'user' not in r.json():
            print(f'WARNING! {r.json()}')
            input('Press enter to quit...')
        logging.info('Logged in to WQBrain!')

        old_get, old_post = self.get, self.post
        def new_get(*args, **kwargs):
            try:    return old_get(*args, **kwargs)
            except: return new_get(*args, **kwargs)
        def new_post(*args, **kwargs):
            try:    return old_post(*args, **kwargs)
            except: return new_post(*args, **kwargs)
        self.get, self.post = new_get, new_post

    def simulate(self, data):
        universe_top = 500
        try:
            neutralizations = data['neutralizations']
            decays = data['decays']
            truncations = data['truncations']
            delay = data['delay']
            alphas = data['alphas']

            logging.info('Creating CSV file')
            csv_file = f'api_D{delay}_{int(time.time())}_TOP{universe_top}.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                header = [
                    'command', 'passed', 'neutralization', 'decay', 'truncation',
                    'sharpe', 'fitness', 'turnover', 'weight',
                    'subsharpe', 'correlation'
                ]
                writer.writerow(header)
                f.flush()

                for neutralization in neutralizations:
                    for decay in decays:
                        for truncation in truncations:
                            for alpha in alphas:
                                logging.info(f'Simulating alpha: {alpha}')
                                logging.info('Waiting for simulation to end (0%)')
                                while True:
                                    # keep sending a post request until the simulation link is found
                                    try:
                                        r = self.post('https://api.worldquantbrain.com/simulations', json={
                                            'regular': alpha,
                                            'type': 'REGULAR',
                                            'settings': {
                                                "nanHandling":"OFF",
                                                "instrumentType":"EQUITY",
                                                "delay":delay,
                                                "universe":f"TOP{universe_top}",
                                                "truncation":truncation,
                                                "unitHandling":"VERIFY",
                                                "pasteurization":"ON",
                                                "region":"USA",
                                                "language":"FASTEXPR",
                                                "decay":decay,
                                                "neutralization":neutralization.upper(),
                                                "visualization":False
                                            }
                                        })
                                        nxt = r.headers['Location']
                                        break
                                    except:
                                        pass
                                logging.info(f'Obtained simulation link: {nxt}')
                                ok = True
                                while True:
                                    time.sleep(2.5)
                                    r = self.get(nxt).json()
                                    if 'alpha' in r:
                                        alpha_link = r['alpha']
                                        break
                                    try:    logging.info(f"Waiting for simulation to end ({int(100*r['progress'])}%)")
                                    except: ok = False; break
                                if not ok:
                                    row = [
                                        alpha, 0,
                                        neutralization, decay, truncation,
                                        0, 0, 0, 'FAIL', 0, -1
                                    ]
                                else:
                                    r = self.get(f'https://api.worldquantbrain.com/alphas/{alpha_link}').json()
                                    passed = 0
                                    for check in r['is']['checks']:
                                        passed += check['result'] == 'PASS'
                                        if check['name'] == 'CONCENTRATED_WEIGHT':
                                            weight_check = check['result']
                                        if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE':
                                            subsharpe = check['value']
                                    row = [
                                        alpha, passed,
                                        neutralization, decay, truncation,
                                        r['is']['sharpe'],
                                        r['is']['fitness'],
                                        round(100*r['is']['turnover'],2),
                                        weight_check,
                                        subsharpe,
                                        -1
                                    ]
                                    logging.info(f"{passed}/7 test cases passed!")
                                writer.writerow(row)
                                f.flush()
                                logging.info('Result added to CSV!')
        except Exception as e:
            print(e)
            input('Press enter to quit...')

if __name__ == '__main__':
    WQSession().simulate(DATA)