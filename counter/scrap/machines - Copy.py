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


chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--user-data-dir=tmp')
# chrome_options.add_argument('--enable-logging')
# chrome_options.add_argument('--dump-dom')
# chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--ignore-certificate-errors-spki-list')
# chrome_options.add_argument('--ignore-ssl-errors')
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
# driver = None

def pass_agreement(link):
    while True:

        if driver.current_url == link:
            print("Just Accepted!")
            break
        else:
            icon = driver.find_element(By.XPATH, "//img[@id='gn_interstitial_close_icon']")
            icon.click()
            print("Clicked Screen icon")            

            driver.get(link)
            button = driver.find_elements(By.CSS_SELECTOR, "button")
            button[1].click()
            print("Clicked Accept_BTN")
            


def getMachines(link):
    
    # link = "https://daidata.goraggio.com/100930/list?mode=psModelNameSearch&bt=4.00&ps=P"  ############# sample url
    # link = "https://daidata.goraggio.com/100860/list?mode=psModelNameSearch&bt=21.70&ps=S" ################ slot page
    # driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)

    driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    section = soup.find('section')
    uls = section.findAll('ul')

    machines = []
    for ul in uls:

        machine = ul.find('li').find('a').find('h2').getText()
        url = ul.find('li').find('a').attrs['href']

        machines.append({'machine':machine, 'url':url})

    return machines

    
def getUnits(link):

    # link = https://daidata.goraggio.com/100930/unit_list?model=P%E7%BE%A9%E9%A2%A8%E5%A0%82%E3%80%85%E5%85%BC%E7%B6%9A%E3%81%A8%E6%85%B6%E6%AC%A12N-X&ballPrice=4.00&f=1

    driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tbody = soup.find('tbody')
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
        
        




    

def arr_js(scripts): ###################### funtion to extract array from javascript on web page scripts

    for script in scripts:
        data = re.findall(r'var data.*?=\s*(.*?);', script.getText(), re.DOTALL | re.MULTILINE)
        if data == []:
            continue
        else:
            data = eval(data[0])
            return data[0]
            break



def val_time_pachinko(times, types, values): ########################### function to extract value by timestamp and graph

    points = []

    for i in range(1, len(values)-1):

      if values[i-1][1] > values[i][1] and values[i][1] < values[i+1][1]:
        points.append(['bottom',values[i][0],values[i][1]])
      elif values[i-1][1] < values[i][1] and values[i][1] > values[i+1][1]:
        points.append(['top',values[i][0],values[i][1]])
      else:
        continue

    # for point in points:
    #   print(point)
    # times = ['18:34', '18:27', '18:23', '15:23', '15:14', '13:45', '13:37', '12:26', '12:01', '11:58', '11:52', '11:30', '10:55', '10:50']
    # types = ['確変', '確変', '通常', '確変', '通常', '確変', '通常', '通常', '確変', '確変', '通常', '通常', '確変', '通常']

    final_result = []
    l = len(types)
    k = len(points)

    for i in range(0, l):
      cur_type = types[l-1-i]
      next_type = types[l-1-i-1]

      if cur_type == '通常' and next_type == '通常':
    
        flag = True
        for j in range(0,k):
          if points[j][0] == 'bottom':
            if j+1 == k:
              final_result.append([times[l-1-i], points[j][2],'unknown'])
            else:
              final_result.append([times[l-1-i], points[j][2], points[j+1][2]])
              points[j+1][0] = 'cross' ############################## 通常 -> 通常 : skip top in points

            points[j][0] = 'cross'
            flag = False
            break
        
        if flag:
          final_result.append([times[l-1-i], 'unknown','unknown'])



      elif cur_type == '通常' and next_type == '確変':

        flag = True
        for j in range(0,k):
          if points[j][0] == 'bottom':
            final_result.append([times[l-1-i], points[j][2]])
            points[j][0] = 'cross'
            flag = False
            break
        
        if flag:
          final_result.append([times[l-1-i], 'unknown'])


      elif cur_type == '確変' and next_type == '確変':

        final_result.append([times[l-1-i],'-']) ############################## 確変 -> 確変 : skip one in types    


      elif cur_type == '確変' and next_type == '通常':  

        flag = True
        for j in range(0,k):
          if points[j][0] == 'top':
            final_result.append([times[l-1-i], points[j][2]])
            points[j][0] = 'cross'
            flag = False
            break
        
        if flag:
          final_result.append([times[l-1-i], 'unknown'])

    return final_result

    
def val_time_slot(times, types, values): ########################### function to extract value by timestamp and graph

    data = []
    day = values[0][0].split(" ")
    day = day[0]

    for time in times:

        # print(time)

        time_day = day + ' ' +time
        time_obj = datetime.fromisoformat(time_day)
        time_timestamp = time_obj.timestamp() #### timestamp - seconds

        l = len(values)
        time_prev = values[0]
        time_next = values[l-1]
        inteval_prev = 0
        inteval_next = 0

        for value in values: ############ prev and next point

            value_t_obj = datetime.fromisoformat(value[0])
            value_timestamp = value_t_obj.timestamp()

            interval_timestamp = value_timestamp - time_timestamp

            if interval_timestamp < 0:
                time_prev = value
                inteval_prev = interval_timestamp
            else:
                time_next = value
                inteval_next = interval_timestamp
                break


        # print(time_prev)
        # print(time_next)
        # print(inteval_prev)
        # print(inteval_next)

      ####################### increase per second ###########################

        increase = (time_next[1] - time_prev[1])/(inteval_next - inteval_prev)
        # print(time_next[1] - time_prev[1])
        # print(inteval_next - inteval_prev)
        # print(increase)
        time_value = time_prev[1] + increase * abs(inteval_prev)
        # print(time_value)      
        data.append([time, time_value])

    return data


def getPachinko(link):

    driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    h1 = soup.find('h1')

    supple = soup.find('div', class_="supple")
    time_tag = supple.find('time').attrs['class']
    if time_tag == 'older':
        return {'result':'no_data','data':{}}


    tables = soup.findAll('table')


    ##################################### CSV #################################

    unit_name = h1.find('strong').getText()
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
    
    if len(tables) < 3:

        return {'result':'no_table','data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start}}

    else:

        tbody2 = tables[2].find('tbody')
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
            graph_values = arr_js(scripts)        

            table_values = val_time_pachinko(table_times, table_types, graph_values)
            last_value = graph_values[len(graph_values)-1]

            return {'result':1 ,'data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'last_value':last_value,'table':table_data,'graph':table_values}}
            



def getSlot(link):

    driver.get(link)
    pass_agreement(link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    h1 = soup.find('h1')

    supple = soup.find('div', class_="supple")
    time_tag = supple.find('time').attrs['class']
    if time_tag == 'older':
        return {'result':'no_data','data':{}}

        
    tables = soup.findAll('table')


    ##################################### CSV #################################

    unit_name = h1.find('strong').getText()
    tbody0 = tables[0].find('tbody')
    trs0 = tbody0.findAll('tr')
    tds0 = trs0[1].findAll('td')

    BB = tds0[0].getText()
    RB = tds0[1].getText()
    start = tds0[len(tds0)-1].getText()

    tbody1 = tables[1].find('tbody')
    trs1 = tbody1.findAll('tr')
    
    first_row_tds = trs1[0].findAll('td')
    sechond_row_tds = trs1[1].findAll('td')
    third_row_tds = trs1[2].findAll('td')

    most_bonus = first_row_tds[0].getText()
    most_bonus = most_bonus.strip()
    cumulative_start = first_row_tds[1].getText()
    cumulative_start = cumulative_start.strip()
    probability = sechond_row_tds[0].getText()
    probability = probability.strip()
    yesterday_start = sechond_row_tds[1].getText()
    yesterday_start = yesterday_start.strip()
    BB_probability = third_row_tds[0].getText()
    BB_probability = BB_probability.strip()
    RB_probability = third_row_tds[1].getText()
    RB_probability = RB_probability.strip()




    if len(tables) < 3:

        return {'result':'no_table','data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'BB_probability':BB_probability,'RB_probability':RB_probability}}

    else:

        tbody2 = tables[2].find('tbody')
        trs2 = tbody2.findAll('tr')
        tds2 = (trs2[0].findAll('th'))

        if len(tds2) < 5:

            return {'result':'no_table','data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'BB_probability':BB_probability,'RB_probability':RB_probability}}

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
            graph_values = arr_js(scripts)        

            table_values = val_time_slot(table_times, table_types, graph_values)
            last_value = graph_values[len(graph_values)-1]

            return {'result':1 ,'data':{'most_bonus':most_bonus,'cumulative_start':cumulative_start,'probability':probability,'yesterday_start':yesterday_start,'BB_probability':BB_probability,'RB_probability':RB_probability,'last_value':last_value,'table':table_data,'graph':table_values}}