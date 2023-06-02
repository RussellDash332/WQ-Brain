from main import WQSession
import time
import logging
import sys
import pandas as pd

wq = WQSession()
logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')

def submit(aid):
    wq.post(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
    logging.info(f'Attempting to submit https://platform.worldquantbrain.com/alpha/{aid}')
    while True:
        submit_r = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
        if submit_r.status_code == 404:
            logging.info('Skipping due to status code 404, alpha is probably already submitted!')
            return False
        if submit_r.content:
            for check in submit_r.json()['is']['checks']:
                if check['name'] == 'SELF_CORRELATION':
                    logging.info(f'Done! -- {check}')
                    return check['result'] == 'PASS'
            break
        time.sleep(5)
    logging.info(submit_r.json())

if len(sys.argv) > 1:
    df = pd.read_csv(sys.argv[1]).sort_values(by='after', ascending=False)
    for (idx, row) in df.iterrows():
        success = submit(row.link.split('/')[-1])
        if success: break
