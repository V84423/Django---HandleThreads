from distutils.command.build_scripts import first_line_re
from threading import Thread, Timer
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.crypto import get_random_string
# from .models import User, Shop, Machine, Unit, Pachinko, Slot, Data
# from counter.scrap.machines import getMachines, getUnits, getPachinko, getSlot

# -*- coding: utf_8 -*-
import time
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()

# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--user-data-dir=tmp')
# chrome_options.add_argument('--enable-logging')
# chrome_options.add_argument('--dump-dom')
# chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--headless')

chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--log-level=OFF')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-application-cache')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--disable-dev-shm-usage")

chrome_options.add_argument('--disable-browser-side-navigation')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--ignore-certificate-errors-spki-list')
# chrome_options.add_argument('--ignore-ssl-errors')
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
# driver.quit()
# driver = None


mobile_emulation = {

    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },

    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
    

    }

mobile_options = Options()
# mobile_options.add_argument('--headless')

mobile_options.add_argument("--disable-infobars")
mobile_options.add_argument("--disable-extensions")
mobile_options.add_argument('--log-level=OFF')
mobile_options.add_argument('--no-sandbox')
mobile_options.add_argument('--disable-application-cache')
mobile_options.add_argument('--disable-gpu')
mobile_options.add_argument("--disable-dev-shm-usage")

mobile_options.add_experimental_option("mobileEmulation", mobile_emulation)
prefs = {"profile.managed_default_content_settings.images": 2}
mobile_options.add_experimental_option("prefs", prefs)
# mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)


def pass_unit_agreement(driver, link):
    
    while True:

        current_url = ''
        try:
            current_url = driver.current_url
        except TimeoutException:
            print("Loading took too much time!")
            print(link)
            driver.refresh()
            driver.get(link)
            pass_unit_agreement(driver, link)

        if current_url == link or current_url == (link + "&device=pc"):
            # print("Just Accepted!")
            break
        else:
            delay = 10 # seconds
            try:
                driver.maximize_window()

                content = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//button')))
                # print("Page is ready!")

                # icon = driver.find_element(By.XPATH, "//img[@id='gn_interstitial_close_icon']")
                # icon.click()
                # # print("Clicked Screen icon")            
                # driver.get(link)

                button = driver.find_elements(By.XPATH, '//button')
                try:
                    button[1].click()
                except NoSuchElementException:
                    driver.get(link)
                    pass_unit_agreement(driver, link)

                # print("Clicked Accept_BTN")

                driver.minimize_window()

            except TimeoutException:
                print("Loading took too much time!")
                print(link)
                driver.refresh()
                driver.get(link)
            

def arr_script(scripts): ###################### funtion to extract array from javascript on web page scripts
    
    values = []

    for script in scripts:
        data = re.findall(r'var data.*?=\s*(.*?);', script.getText(), re.DOTALL | re.MULTILINE)
        if data == []:
            continue
        else:
            data = eval(data[0])
            values = data[0]
            break
    
    first_hit = 0
    last_value = 0
    l = len(values)-1
    
    for i in range(1, l):
      if values[i-1][1] > values[i][1] and values[i][1] < values[i+1][1]:
        first_hit = values[i][1]
        break

    last_value = values[l][1]

    return {'first_hit':first_hit,'last_value':last_value}


def getUnitData(driver, link, ps):

    driver.get(link)
    pass_unit_agreement(driver, link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    supple = soup.find('div', class_="supple")
    time_tag = supple.find('time').attrs['class']
    if time_tag == 'older':
        return {'most_bonus':'',
            'cumulative_start':'',
            'probability':'',
            'yesterday_start':'',
            'BB_probability':'',
            'RB_probability':'',
            'last_value':'',
            'table':'',
            'graph':''}
        
    tables = soup.findAll('table')


    ##################################### CSV #################################

    # tbody0 = tables[0].find('tbody')
    # trs0 = tbody0.findAll('tr')
    # tds0 = trs0[1].findAll('td')

    # BB = tds0[0].getText()
    # RB = tds0[1].getText()
    # start = tds0[len(tds0)-1].getText()

    tbody1 = tables[1].find('tbody')
    trs1 = tbody1.findAll('tr')
    
    first_row_tds = trs1[0].findAll('td')
    sechond_row_tds = trs1[1].findAll('td')
    third_row_tds = []

    if ps == "S":
        third_row_tds = trs1[2].findAll('td')

    most_bonus = first_row_tds[0].getText()
    most_bonus = most_bonus.strip()
    
    cumulative_start = ''
    if len(first_row_tds) == 2:
        cumulative_start = first_row_tds[1].getText()
        cumulative_start = cumulative_start.strip()

    probability = sechond_row_tds[0].getText()
    probability = probability.strip()

    yesterday_start = ''
    if len(sechond_row_tds) == 2:
        yesterday_start = sechond_row_tds[1].getText()
        yesterday_start = yesterday_start.strip()
    
    BB_probability = ''
    RB_probability = ''
    if ps == "S":
        BB_probability = third_row_tds[0].getText()
        BB_probability = BB_probability.strip()
        RB_probability = third_row_tds[1].getText()
        RB_probability = RB_probability.strip()


    graph_values = dict()
    table_data = []

    scripts = soup.findAll('script')
    graph_values = arr_script(scripts)

    

    if len(tables) > 3:

        tbody2 = tables[2].find('tbody')
        trs2 = tbody2.findAll('tr')
        tds2 = (trs2[0].findAll('th'))

        if len(tds2) > 4:            

            i = 0
            for tr in trs2:        

                if i == 0:
                    i += 1
                    continue
                
                else:
                    tds = tr.findAll('td')
                    table_data.append(
                        [tds[0].getText(),
                        tds[1].getText(),
                        tds[2].getText(),
                        tds[3].getText(),
                        tds[4].getText()]
                    )

    return {'most_bonus':most_bonus,
            'cumulative_start':cumulative_start,
            'probability':probability,
            'yesterday_start':yesterday_start,
            'BB_probability':BB_probability,
            'RB_probability':RB_probability,
            'last_value':graph_values['last_value'],
            'table':table_data,
            'graph':graph_values['first_hit']
            }

link = "https://daidata.goraggio.com/100947/detail?unit=26"
res = getUnitData(driver,link,"P")
print(res)