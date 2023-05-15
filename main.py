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

    def simulate(self, data):
        neutralizations = data['neutralizations']
        decays = data['decays']
        truncations = data['truncations']
        delay = data['delay']
        alphas = data['alphas']

        logging.info('Creating CSV file')
        csv_file = f'api_D{delay}_{int(time.time())}.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            header = [
                'command', 'passed', 'neutralization', 'decay', 'truncation',
                'sharpe', 'fitness', 'turnover', 'weight',
                'subsharpe', 'correlation'
            ]
            writer.writerow(header)

            for neutralization in neutralizations:
                for decay in decays:
                    for truncation in truncations:
                        for alpha in alphas:
                            logging.info(f'Simulating alpha: {alpha}')
                            logging.info('Waiting for simulation to end (0%)')
                            r = self.post('https://api.worldquantbrain.com/simulations', json={
                                'regular': alpha,
                                'type': 'REGULAR',
                                'settings': {
                                    "nanHandling":"OFF",
                                    "instrumentType":"EQUITY",
                                    "delay":delay,
                                    "universe":"TOP3000",
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
                            while True:
                                time.sleep(1)
                                r = self.get(nxt).json()
                                if 'alpha' in r:
                                    alpha_link = r['alpha']
                                    break
                                logging.info(f"Waiting for simulation to end ({int(100*r['progress'])}%)")
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
                                100*r['is']['turnover'],
                                weight_check,
                                subsharpe,
                                -1
                            ]
                            logging.info(f"{passed}/7 test cases passed!")
                            writer.writerow(row)

if __name__ == '__main__':
    WQSession().simulate(DATA)