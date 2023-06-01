import csv
import base64
import logging
import requests
import json
import time
from parameters import DATA
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')
        self.json_fn = json_fn
        self.login()
        old_get, old_post = self.get, self.post
        def new_get(*args, **kwargs):
            try:    return old_get(*args, **kwargs)
            except: return new_get(*args, **kwargs)
        def new_post(*args, **kwargs):
            try:    return old_post(*args, **kwargs)
            except: return new_post(*args, **kwargs)
        self.get, self.post = new_get, new_post
        self.login_expired = False
        self.rows_processed = 0

    def login(self):
        with open(self.json_fn, 'r') as f:
            creds = json.loads(f.read())
            email, password = creds['email'], creds['password']
            b64_auth = base64.b64encode(f'{email}:{password}'.encode('ascii')).decode('ascii')
            r = self.post('https://api.worldquantbrain.com/authentication', headers={'Authorization': f'Basic {b64_auth}'})
        if 'user' not in r.json():
            print(f'WARNING! {r.json()}')
            input('Press enter to quit...')
        logging.info('Logged in to WQBrain!')

    def simulate(self, data):
        self.rows_processed = 0

        def process_simulation(writer, f, simulation):
            if self.login_expired: return # expired crendentials

            thread = current_thread().name
            alpha = simulation['code'].replace('\n', ';').replace(';;', ';')
            delay = simulation.get('delay', 1)
            universe = simulation.get('universe', 'TOP3000')
            truncation = simulation.get('truncation', 0.1)
            region = simulation.get('region', 'USA')
            decay = simulation.get('decay', 6)
            neutralization = simulation.get('neutralization', 'SUBINDUSTRY').upper()
            pasteurization = simulation.get('pasteurization', 'ON')
            nan = simulation.get('nanHandling', 'OFF')
            logging.info(f"{thread} -- Simulating alpha: {alpha}")
            while True:
                # keep sending a post request until the simulation link is found
                try:
                    r = self.post('https://api.worldquantbrain.com/simulations', json={
                        'regular': alpha,
                        'type': 'REGULAR',
                        'settings': {
                            "nanHandling":nan,
                            "instrumentType":"EQUITY",
                            "delay":delay,
                            "universe":universe,
                            "truncation":truncation,
                            "unitHandling":"VERIFY",
                            "pasteurization":pasteurization,
                            "region":region,
                            "language":"FASTEXPR",
                            "decay":decay,
                            "neutralization":neutralization,
                            "visualization":False
                        }
                    })
                    nxt = r.headers['Location']
                    break
                except:
                    try:
                        if 'credentials' in r.json()['detail']:
                            self.login_expired = True
                            return # debugging WIP
                    except:
                        logging.info(f'{thread} -- {r.content}')
                        break
            logging.info(f'{thread} -- Obtained simulation link: {nxt}')
            ok = True
            while True:
                r = self.get(nxt).json()
                if 'alpha' in r:
                    alpha_link = r['alpha']
                    break
                try:
                    logging.info(f"{thread} -- Waiting for simulation to end ({int(100*r['progress'])}%)")
                except Exception as e:
                    ok = (False, r['message']); break
                time.sleep(10)
            if ok != True:
                logging.info(f'{thread} -- Issue when sending simulation request: {ok[1]}')
                row = [
                    0, delay, region,
                    neutralization, decay, truncation,
                    0, 0, 0, 'FAIL', 0, -1, universe, nxt, alpha
                ]
            else:
                final_link = f'https://api.worldquantbrain.com/alphas/{alpha_link}'
                r = self.get(final_link).json()
                logging.info(f'{thread} -- Obtained alpha link: {final_link}')
                passed = 0
                for check in r['is']['checks']:
                    passed += check['result'] == 'PASS'
                    if check['name'] == 'CONCENTRATED_WEIGHT':
                        weight_check = check['result']
                    if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE':
                        subsharpe = check['value']
                try:    subsharpe
                except: subsharpe = -1
                row = [
                    passed, delay, region,
                    neutralization, decay, truncation,
                    r['is']['sharpe'],
                    r['is']['fitness'],
                    round(100*r['is']['turnover'], 2),
                    weight_check, subsharpe, -1,
                    universe, final_link, alpha
                ]
            writer.writerow(row)
            f.flush()
            self.rows_processed += 1
            logging.info(f'{thread} -- Result added to CSV!')

        try:
            for handler in logging.root.handlers:
                logging.root.removeHandler(handler)
            csv_file = f"api_{str(time.time()).replace('.', '_')}.csv"
            logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s', filename=csv_file.replace('csv', 'log'))
            logging.info('Creating CSV file')
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                header = [
                    'passed', 'delay', 'region', 'neutralization', 'decay', 'truncation',
                    'sharpe', 'fitness', 'turnover', 'weight',
                    'subsharpe', 'correlation', 'universe', 'link', 'code'
                ]
                writer.writerow(header)
                with ThreadPoolExecutor(max_workers=10) as executor: # 10 threads, only 3 can go in concurrently so this is no harm
                    _ = executor.map(lambda sim: process_simulation(writer, f, sim), data)
        except Exception as e:
            logging.info(f'Issue occurred! {type(e).__name__}: {e}')
        return self.rows_processed

if __name__ == '__main__':
    TOTAL_ROWS = len(DATA)
    CURR_ROWS = 0
    while CURR_ROWS < TOTAL_ROWS:
        wq = WQSession()
        print(f'{CURR_ROWS}/{TOTAL_ROWS} alpha simulations...')
        rows = wq.simulate(DATA)
        DATA = DATA[CURR_ROWS:]
        CURR_ROWS += rows
