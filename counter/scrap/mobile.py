# -*- coding: utf_8 -*-
import time
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


mobile_emulation = {

    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },

    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" 

    }

mobile_options = Options()
mobile_options.add_argument('--disable-gpu')
mobile_options.add_experimental_option("mobileEmulation", mobile_emulation)
prefs = {"profile.managed_default_content_settings.images": 2}
mobile_options.add_experimental_option("prefs", prefs)
mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)


def pass_agreement(link):
    while True:

        if mobile_driver.current_url == link:
            print("Just Accepted!")
            break
        else:
            # icon = mobile_driver.find_element(By.XPATH, "//img[@id='gn_interstitial_close_icon']")
            # icon.click()
            # print("Clicked Screen icon")
            # mobile_driver.get(link)

            button = mobile_driver.find_elements(By.CSS_SELECTOR, "button")
            button[1].click()
            print("Clicked Accept_BTN")


def arr_mobile_js(scripts): ###################### funtion to extract array from javascript on web page scripts

    for script in scripts:
        data = re.findall(r'var usageData.*?=\s*(.*?);', script.getText(), re.DOTALL | re.MULTILINE)
        if data == []:
            continue
        else:
            data = eval(data[0])
            return data


def getMobileUnits(link):

    mobile_driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')
    tbody = soup.find('tbody')
    
    if tbody == None:
        time.sleep(5)
        getUnits(link)

    trs = tbody.findAll('tr')

    units = []
    for tr in trs:

        tds = tr.findAll('td')

        unit = tds[1].find('a').getText()
        url = tds[1].find('a').attrs['href']
        cumulative_start = tds[2].getText()
        total_jackpot = tds[3].getText()
        first_hit = tds[4].getText()
        probability_change = tds[5].getText()
        jackpot_probability = tds[6].getText()
        probability = tds[7].getText()
        most_bonus = tds[8].getText()
        yesterday_start = tds[9].getText()
        units.append({'unit':unit, 'url':url})

    return units

def getMobileMachines(link):
    
    # mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
    mobile_driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')
    section = soup.find('section')
    ul = section.find('ul')
    lis = ul.findAll('li')

    machines = []
    for li in lis:

        machine = li.find('a').find('h2').getText()
        url = li.find('a').attrs['href']
        machines.append({'machine':machine, 'url':url})

    # mobile_driver.quit()
    return machines


def getMobilePachinko(link):

    mobile_driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

    supple = soup.find('div', class_="supple")
    time_tag = supple.find('time').attrs['class']
    if time_tag == 'older':
        return {'result':'no_data','data':{}}


    tables = soup.findAll('table')


    ##################################### CSV #################################

    tbody1 = tables[1].find('tbody')
    trs1 = tbody1.findAll('tr')

    
    first_row_tds = trs1[0].findAll('td')
    sechond_row_tds = trs1[1].findAll('td')

    most_bonus = first_row_tds[0].getText()
    most_bonus = most_bonus.strip()
    cumulative_start = first_row_tds[1].getText()
    cumulative_start = cumulative_start.strip()
    probability = sechond_row_tds[0].getText()
    probability = probability.strip()
    yesterday_start = sechond_row_tds[1].getText()
    yesterday_start = yesterday_start.strip()
    
    if len(tables) < 14:

        return {'result':'no_table','data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start}}

    else:

        tbody2 = tables[14].find('tbody')
        trs2 = tbody2.findAll('tr')
        tds2 = (trs2[0].findAll('th'))

        if len(tds2) < 5:
            
            return {'result':'no_table','data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start}}

        else:

            ###################################### GRAPH #####################################
            
            table_times = []
            table_types = []
            graph_values = []
            table_values = []
            table_data = []

            i = 0
            for tr in trs2:        

                if i == 0:
                    i += 1
                    continue
                
                else:
                    tds = tr.findAll('td')
                    table_types.append(tds[3].getText())
                    table_times.append(tds[4].getText())
                    table_data.append([tds[0].getText(),tds[1].getText(),tds[2].getText(),tds[3].getText(),tds[4].getText()])


            scripts = soup.findAll('script')
            graph_values = arr_mobile_js(scripts)        

            # table_values = val_time_pachinko(table_times, table_types, graph_values)
            # last_value = graph_values[len(graph_values)-1]

            table_values = graph_values
            last_value = ''
            print({'result':1 ,'data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'last_value':last_value,'table':table_data,'graph':table_values}})
            return {'result':1 ,'data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'last_value':last_value,'table':table_data,'graph':table_values}}
            




link = "https://daidata.goraggio.com/101010/list?mode=psModelNameSearch&bt=4.00&ps=P"  ############# sample url
machines = getMobileMachines(link)
units = []
for machine in machines:
    units = getMobileUnits(machine['url'])
    for unit in units:
        getMobilePachinko(unit['url'])


mobile_driver.quit()