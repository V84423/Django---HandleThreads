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
chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--ignore-certificate-errors-spki-list')
# chrome_options.add_argument('--ignore-ssl-errors')
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
# driver.quit()
# driver = None


mobile_emulation = {

    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },

    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
    

    }

mobile_options = Options()
# mobile_options.add_argument('--headless')
mobile_options.add_argument('--disable-gpu')
mobile_options.add_experimental_option("mobileEmulation", mobile_emulation)
prefs = {"profile.managed_default_content_settings.images": 2}
mobile_options.add_experimental_option("prefs", prefs)
mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)

import requests
headers = {
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

def mobile_pass_agreement(mobile_driver, link):
    
    while True:

        current_url = mobile_driver.current_url
        # try:
        #     current_url = mobile_driver.current_url
        # except NoSuchElementException:
        #     mobile_driver.refresh()
        #     current_url = mobile_driver.current_url

        if current_url == link or current_url == (link + "&device=pc"):
            # print("Just Accepted!")
            break
        else:

            delay = 10 # seconds
            try:
                mobile_driver.maximize_window()

                content = WebDriverWait(mobile_driver, delay).until(EC.presence_of_element_located((By.XPATH, '//button')))
                # print("Page is ready!")

                # icon = driver.find_element(By.XPATH, "//img[@id='gn_interstitial_close_icon']")
                # icon.click()
                # # print("Clicked Screen icon")            
                # driver.get(link)

                button = mobile_driver.find_elements(By.XPATH, '//button')
                try:
                    button[1].click()
                except NoSuchElementException:
                    mobile_driver.get(link)
                    mobile_pass_agreement(mobile_driver, link)

                # print("Clicked Accept_BTN")

                mobile_driver.minimize_window()

            except TimeoutException:
                print("Loading took too much time!")
                print(link)
                mobile_driver.refresh()
                mobile_driver.get(link)

            
def getMobileMachines(mobile_driver, link):
    
    # mobile_driver.set_page_load_timeout(5)
    # try:
    #     mobile_driver.get(link)
    # except NoSuchElementException:

    #     print('stop')
    #     time.sleep(5)
    #     mobile_driver.refresh()
        # getMobileMachines(mobile_driver, link)
        # mobile_driver.get(link)
    
    try:
        mobile_driver.get(link)

    except TimeoutException:
        print("Loading took to get link too much time!")
        print(link)
        mobile_driver.refresh()
        getMobileMachines(mobile_driver, link)


    delay = 5 # seconds
    try:
        content = WebDriverWait(mobile_driver, delay).until(EC.presence_of_element_located((By.XPATH, '//section')))
        # print("Page is ready!")
    except TimeoutException:
        print("Loading took to get content too much time!")
        print(link)
        mobile_driver.refresh()
        getMobileMachines(mobile_driver, link)

    mobile_pass_agreement(mobile_driver,link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

    nextListBtn = soup.find(id="nextListBtn")

    machines = []

    if nextListBtn == None:
        section = soup.find('section')
        ul = section.find('ul')
        lis = ul.findAll('li')
        
        for li in lis:
            machine = li.find('a').find('h2').getText()
            url = li.find('a').attrs['href']
            machines.append({'machine':machine, 'url':url})
    else:

        yesterday = datetime.now() - timedelta(1)
        targetDate = datetime.strftime(yesterday, '%Y-%m-%d')
        data_totaldata = nextListBtn.attrs["data-totaldata"]

        link = link.replace("https://daidata.goraggio.com","https://daidata.goraggio.com/api/store/more_list")
        link = link.replace("/list?mode=psModelNameSearch&bt","?targetDate="+targetDate+"&ballPrice")
        link = link + "&totaldata=" + data_totaldata

        while True:
            
            mobile_driver.get(link)
            soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

            pre = soup.find('pre').getText()
            result = json.loads(pre)
            hasNext = result['hasNext']
            html = result['html']
            page = result['page']

            soup = BeautifulSoup(html, 'html.parser')
            lis = soup.findAll('li')
            for li in lis:
                machine = li.find('a').find('h2').getText()
                url = li.find('a').attrs['href']
                machines.append({'machine':machine, 'url':url})

            if hasNext:
                link = link + "&page=" + str(page)
            else:
                break

    return machines


def getMobileData(mobile_driver, link, ps):
    
    try:
        mobile_driver.get(link)
    except:
        getMobileData(mobile_driver, link, ps)
            
    mobile_pass_agreement(mobile_driver,link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')
    shopholiday = soup.find(class_="shopholiday")
    if shopholiday != None:
        print(shopholiday.getText())
        return {'most_bonus':'',
            'cumulative_start':'',
            'probability':'',
            'yesterday_start':'',
            'BB_probability':'',
            'RB_probability':'',
            'last_value':'',
            'table':'',
            'graph':''}

    timeout = 30
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "#today_graph svg#graph"))
        WebDriverWait(mobile_driver, timeout).until(element_present)
    except TimeoutException:
        print("Loading took to get link too much time!")
        print(link)
        getMobileData(mobile_driver, link, ps)


    ##############################################################

    # soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

    div_flipsnap = soup.find(class_="flipsnap")
    table_flipsnap = div_flipsnap.findAll(class_="overviewTable3")[0]    
    tbody = table_flipsnap.find('tbody')
    trs = tbody.findAll('tr')
    first_row_tds = trs[0].findAll('td')
    sechond_row_tds = trs[1].findAll('td')
    third_row_tds = []

    if ps == "S":
        third_row_tds = trs[2].findAll('td')

    most_bonus = first_row_tds[0].getText()
    most_bonus = most_bonus.strip()
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
    
    i = 0    
    table_data = []

    div_jackport = soup.find(class_="jackpot-flipsnap")

    if div_jackport != None:
        table_jackport = div_jackport.find(id="dedama_log_0")
        trs = table_jackport.findAll('tr')

        for tr in trs:
            if i == 0:
                i += 1
                continue        
            else:
                tds = tr.findAll('td')
                table_data.append([tds[0].getText(),tds[1].getText(),tds[2].getText(),tds[3].getText(),tds[4].getText()])


    #################################
    div = soup.find(id="today_graph")
    svg = div.find('svg')
    
    try:
        path = svg.find('path')
    except NoSuchElementException:
        print("SVG Tag None Error.")
        print(link)
        # mobile_driver.refresh()
        getMobileData(mobile_driver, link, ps)

    if path.findPrevious('circle') == None:
        tspan = path.findPrevious('text').find('tspan').getText()    
    else:
        tspan = path.findPrevious('circle').findPrevious('text').find('tspan').getText()

    line = path.attrs['d']
    points = line.split(",")

    mobile_graph_values = list()
    for i in range(0, len(points)):
        if (i+1) % 2 == 0:
            mobile_graph_values.append(points[i])

    first_hit_bottom = 200
    for i in range(1, len(mobile_graph_values)-1):
        if mobile_graph_values[i] > mobile_graph_values[i-1] and mobile_graph_values[i] > mobile_graph_values[i+1]:
            first_hit_bottom = mobile_graph_values[i]
            break

    last_value = mobile_graph_values[len(mobile_graph_values)-1]
    inc_y = int(tspan) / 170
    val_first_hit = 200 - int(first_hit_bottom)
    val_last_time = 200 - int(last_value)

    real_first_hit_value = val_first_hit * inc_y
    real_last_value = val_last_time * inc_y

    return {'most_bonus':most_bonus,
            'cumulative_start':cumulative_start,
            'probability':probability,
            'yesterday_start':yesterday_start,
            'BB_probability':BB_probability,
            'RB_probability':RB_probability,
            'last_value':real_last_value,
            'table':table_data,
            'graph':real_first_hit_value}

# link = "https://daidata.goraggio.com/100930/list?mode=psModelNameSearch&bt=4.00&ps=P"

# for machine in getMobileMachines(mobile_driver,link):
#     print(machine)

link = "https://daidata.goraggio.com/100692/detail?unit=599&target_date=2022-02-23&gd=0"

res = getMobileData(mobile_driver, link, "P")
print(res)





