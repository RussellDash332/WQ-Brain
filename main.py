import csv, json
import logging
import numpy as np
import selenium
import os, platform, requests, time
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parameters import NEUTRALIZATIONS, DECAYS, TRUNCATIONS, ALPHAS

logging.basicConfig(encoding='utf-8', level=logging.INFO)

def download_chromedriver():
    version = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text
    try: os.remove('chromedriver.zip')
    except: pass
    print('Downloading "chromedriver.exe"...')
    url = f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip'
    urlretrieve(url, 'chromedriver.zip')
    with ZipFile('chromedriver.zip') as chromezip:
        chromezip.extractall()
    os.remove('chromedriver.zip')

def main(my_neutralizations, my_decays, my_truncations, my_alphas):
    logging.info('Getting webdriver')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.set_page_load_timeout(10)
    driver.get('https://platform.worldquantbrain.com/sign-in')


    logging.info('Accepting cookies')
    while True:
        try:
            Accept = driver.find_element(By.CLASS_NAME, 'button--primary')
            Accept.click()
            break
        except: pass
    logging.info('Cookies accepted')


    logging.info('Logging in')
    email = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    with open('credentials.json', 'r') as f:
        creds = json.loads(f.read())
        my_email, my_password = creds['email'], creds['password']
    email.send_keys(my_email)
    password.send_keys(my_password)
    password.submit()
    logging.info('Logged in')
    time.sleep(10)


    logging.info('Skipping the Welcome to WQBrain popup')
    skip_home = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "introjs-skipbutton"))
    )
    skip_home.click()
    logging.info('Popup closed')
    time.sleep(10)


    logging.info('Clicking the Simulate menu')
    simulate_menu = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "header__img--simulate"))
    )
    simulate_menu.click()
    logging.info('Reached Simulation page')
    time.sleep(10)


    try:
        logging.info('Skipping the Welcome to Simulate popup if any')
        skip_simulate = WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CLASS_NAME, "introjs-skipbutton"))
        )
        skip_simulate.click()
        time.sleep(5)
    except: pass
    finally: logging.info('Popup closed')


    logging.info('Making sure we can see the results')
    checkboxes = driver.find_elements(By.CLASS_NAME, "false.editor__checkbox")
    for checkbox in checkboxes:
        if checkbox.text == 'RESULTS':
            checkbox.click()
            break


    logging.info('Creating CSV file')
    csv_file = f'{int(time.time())}.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        header = [
            'command', 'passed', 'neutralization', 'decay', 'truncation',
            'sharpe', 'fitness', 'turnover', 'weight',
            'subsharpe', 'correlation'
        ]
        writer.writerow(header)

        for my_neutralization in my_neutralizations:
            for my_decay in my_decays:
                for my_truncation in my_truncations:
                    logging.info('Opening simulation settings')
                    settings = driver.find_elements(By.CLASS_NAME, "editor-top-bar-left__settings-btn")[1]
                    settings.click()


                    # the region stays at USA
                    # universe stays at TOP3000
                    # delay stays at 1


                    logging.info('Setting neutralization')
                    neutralization = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "neutralization"))
                    )
                    neutralization.click()
                    neu_types = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "select-portal__item"))
                    )
                    neu_types = driver.find_elements(By.CLASS_NAME, "select-portal__item")
                    for neu_type in neu_types:
                        if neu_type.text == my_neutralization:
                            neu_type.click()
                            break


                    logging.info('Setting decay')
                    decay_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "decay"))
                    )
                    for _ in range(3):
                        decay_element.send_keys(Keys.BACK_SPACE)
                    decay_element.send_keys(f'{my_decay}')


                    logging.info('Setting truncation')
                    trunc_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "truncation"))
                    )
                    for _ in range(5):
                        trunc_element.send_keys(Keys.BACK_SPACE)
                    trunc_element.send_keys(f'{my_truncation}')


                    # pasteurization stays on
                    # nan handling stays on


                    logging.info('Apply changes to simulation settings')
                    apply = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "button--lg"))
                    )
                    apply.click()


                    for my_alpha in my_alphas:
                        logging.info('Inputting the alpha')
                        alpha = driver.find_element(By.CLASS_NAME, "inputarea")
                        alpha.send_keys(my_alpha)


                        logging.info('Simulating')
                        simulate_buttons = driver.find_elements(By.CLASS_NAME, "editor-simulate-button-text--is-code")
                        assert(len(simulate_buttons) == 1)
                        simulate_button = simulate_buttons[0]
                        while True:
                            try:
                                simulate_button.click()
                                break
                            except:
                                continue


                        logging.info('Waiting for simulation to end (0%)')
                        try:
                            progress = WebDriverWait(driver, 60).until(
                               EC.presence_of_element_located((By.CLASS_NAME, 'progress'))
                            )
                            while progress.text != '100%':
                                time.sleep(5)
                                logging.info(f'Waiting for simulation to end ({progress.text})')
                                progress = driver.find_element(By.CLASS_NAME, 'progress')
                        except:
                            time.sleep(3)


                        logging.info('Reverting editor for alpha')
                        for _ in range(len(my_alpha)+10):
                           alpha.send_keys(Keys.BACK_SPACE)
                        time.sleep(max(5, 0.08*len(my_alpha)))


                        logging.info('Getting all passed test cases')
                        try:
                            Pass = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "sumary__testing-checks-PASS-list"))
                            )
                            Pass = driver.find_element(By.CLASS_NAME, "sumary__testing-checks-PASS-list")

                            pass_toggle = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "sumary__testing-checks-icon--PASS-down"))
                            )
                            pass_toggle = driver.find_element(By.CLASS_NAME, 'sumary__testing-checks-icon--PASS-down')
                            
                            pass_toggle.click()
                            pass_lines = []
                            pass_text = Pass.text
                            pass_lines += pass_text.split('\n')
                            logging.info('Success!')
                        except:
                            logging.info('Failed to get all passed test cases')
                        time.sleep(0.1)


                        logging.info('Getting all failed test cases')
                        try:
                            Fail = driver.find_element(By.CLASS_NAME, 'sumary__testing-checks-FAIL-list')
                            fail_toggle = driver.find_element(By.CLASS_NAME, 'sumary__testing-checks-icon--FAIL-down')
                            fail_toggle.click()
                            fail_lines = []
                            fail_text = Fail.text
                            fail_lines += fail_text.split('\n')
                            logging.info('Success!')
                        except:
                            logging.info('Failed to get all failed test cases')


                        for line in pass_lines:
                            elements = line.split(' ')
                            if elements[0] == 'Sharpe':             sharpe = elements[2]
                            if elements[0] == 'Turnover':           turnover = elements[2]
                            if elements[0] == 'Sub-universe':       subsharpe = elements[3]
                            if elements[0] == 'Fitness':            fitness = elements[2]
                            if elements[0] == 'Weight':             weight = 'Weight is well distributed over instruments.'


                        for line in fail_lines:
                            elements = line.split(' ')
                            if elements[0] == 'Sharpe':             sharpe = elements[2]
                            if elements[0] == 'Turnover':           turnover = elements[2]
                            if elements[0] == 'Sub-universe':       subsharpe = elements[3]
                            if elements[0] == 'Fitness':            fitness = elements[2]
                            if elements[0] == 'Weight':             weight = 'Weight is too strongly concentrated or too few instruments are assigned weight.'


                        information = {
                            'passed': len(pass_lines),
                            'sharpe': float(sharpe),
                            'turnover': float(turnover[:-1]),
                            'subsharpe': float(subsharpe),
                            'fitness': float(fitness),
                            'weight': weight,
                            'corr': -1
                        }


                        logging.info('Adding result to CSV')
                        passed    = information['passed']
                        sharpe    = information['sharpe']
                        fitness   = information['fitness']
                        turnover  = information['turnover']
                        weight    = information['weight']
                        subsharpe = information['subsharpe']
                        corr      = information['corr']
                        row = [
                            my_alpha, passed, my_neutralization, my_decay, my_truncation,
                            sharpe, fitness, turnover, weight, subsharpe, corr
                        ]
                        logging.info(row)
                        writer.writerow(row)


                        def debug():
                            print('### PASSED ###')
                            for row in pass_lines: print(row)
                            print('### FAILED ###')
                            for row in fail_lines: print(row)
                        #debug()


if __name__ == '__main__':
    curr_os = platform.platform()
    if curr_os.startswith('Windows'):
        download_chromedriver()
        try:
            main(NEUTRALIZATIONS, DECAYS, TRUNCATIONS, ALPHAS)
        except Exception as e:
            print(f'{type(e).__name__}:', e)
            try: driver.quit()
            except: pass
        input('Press enter to quit...')
