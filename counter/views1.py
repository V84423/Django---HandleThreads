from threading import Thread, Timer
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.crypto import get_random_string
from .models import User, Shop, Machine, Unit, Pachinko, Slot, Data
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

# driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
# driver.quit()
# driver = None


mobile_emulation = {

    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },

    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
    

    }

mobile_options = Options()
# mobile_options.add_argument('--headless')

# mobile_options.add_argument("--disable-infobars")
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




def pass_agreement(driver, link):
    
    while True:

        current_url = driver.current_url
        # try:
        #     current_url = driver.current_url
        # except NoSuchElementException:
        #     driver.refresh()
        #     current_url = driver.current_url

        if current_url == link or current_url == (link + "&device=pc"):
            # print("Just Accepted!")
            break
        else:
            # icon = driver.find_element(By.XPATH, "//img[@id='gn_interstitial_close_icon']")
            # icon.click()
            # # print("Clicked Screen icon")            
            # driver.get(link)

            button = driver.find_elements(By.CSS_SELECTOR, "button")
            button[1].click()
            # print("Clicked Accept_BTN")
            
def getMachines(driver, link):

    # driver.set_page_load_timeout(5)
    # try:
    #     driver.get(link)
    # except NoSuchElementException:

    #     print('stop')
    #     time.sleep(5)
    #     driver.refresh()
        # getMachines(driver, link)
        # driver.get(link)


    

    try:
        driver.get(link)

    except TimeoutException:
        print("Loading took to get link too much time!")
        print(link)
        driver.refresh()
        getMachines(driver, link)

    delay = 5 # seconds
    try:
        content = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'Main-Contents')))
        # print("Page is ready!")
    except TimeoutException:
        print("Loading took to get content too much time!")
        print(link)
        driver.refresh()
        getMachines(driver, link)

    pass_agreement(driver, link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    section = soup.find('section')
    uls = section.findAll('ul')

    machines = []
    for ul in uls:

        machine = ul.find('li').find('a').find('h2').getText()
        url = ul.find('li').find('a').attrs['href']

        machines.append({'machine':machine, 'url':url})

    return machines

def getUnits(driver, link):

    # driver.set_page_load_timeout(5)
    # try:
    #     driver.get(link)
    # except NoSuchElementException:

    #     print('stop')
    #     time.sleep(5)
    #     driver.refresh()
        # getUnits(driver, link)
        # driver.get(link)

    driver.minimize_window()

    try:
        driver.get(link)

    except TimeoutException:
        print("Loading took to get link too much time!")
        print(link)
        driver.refresh()
        getUnits(driver, link)

    delay = 5 # seconds
    try:
        content = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'Main-Contents')))
        # print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
        print(link)
        driver.refresh()
        getUnits(driver, link)

    pass_agreement(driver, link)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tbody = soup.find('tbody')
    
    if tbody == None:
        time.sleep(5)
        driver.refresh()
        getUnits(driver,link)

    try:
        trs = tbody.findAll('tr')
    except:
        time.sleep(5)
        driver.refresh()
        getUnits(driver,link)        

    units = []
    for tr in trs:

        tds = tr.findAll('td')

        unit = tds[1].find('a').getText()
        url = tds[1].find('a').attrs['href']
        # cumulative_start = tds[2].getText()
        # total_jackpot = tds[3].getText()
        # first_hit = tds[4].getText()
        # probability_change = tds[5].getText()
        # jackpot_probability = tds[6].getText()
        # probability = tds[7].getText()
        # most_bonus = tds[8].getText()
        # yesterday_start = tds[9].getText()

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

def arr_mobile_js(scripts): ###################### funtion to extract array from javascript on web page scripts

    for script in scripts:
        data = re.findall(r'var usageData.*?=\s*(.*?);', script.getText(), re.DOTALL | re.MULTILINE)
        if data == []:
            continue
        else:
            data = eval(data[0])
            return data
            break

def val_time_pachinko(times, types, values): ########################### function to extract value by timestamp and graph

    # # print("--------------------------------- real point ---------------------------------------")

    point = []


    new_times = []
    new_types = []

    l = len(types)-1

    for i in range(0,l):
      if types[l-i] == '確変' and types[l-i-1] == '確変':
        continue
      else:
        new_types.append(types[l-i])
        new_times.append(times[l-i])

    new_types.append(types[0])
    new_times.append(times[0])

    # # print(new_times)
    # # print(new_types)

    # # print("--------------------------------- temp points ---------------------------------------")

    temp_points = []
    l = len(new_times)

    for i in range(0,l):
      
      if new_types[i] == '通常':

        temp_points.append(['bottom', new_times[i], 'unknown'])
        if i < l-1 and new_types[i+1] == '通常':
          temp_points.append(['top', new_times[i], 'unknown'])      
        
      else:
        temp_points.append(['top', new_times[i], 'unknown'])


    # for point in temp_points:
    #   # print(point)
      

    # # print("--------------------------------- turning points ---------------------------------------")

    truning_points = []
    for i in range(1, len(values)-1):

      if values[i-1][1] > values[i][1] and values[i][1] < values[i+1][1]:
        truning_points.append(['bottom',values[i][0],values[i][1]])
        values[i].append('checked')
      elif values[i-1][1] < values[i][1] and values[i][1] > values[i+1][1]:
        truning_points.append(['top',values[i][0],values[i][1]])
        values[i].append('checked')
      
      else:
        continue

    # for point in truning_points:
    #   # print(point)


    # # print("--------------------------------- similar turning to temp points ---------------------------------------")

    day = values[0][0].split(" ")
    day = day[0]

    for temp_point in temp_points:
      obj = datetime.fromisoformat(day + ' ' + temp_point[1] + ":00")
      timestamp = obj.timestamp()

      diff = 3600
      for truning_point in truning_points:

        if temp_point[0] == truning_point[0] and len(truning_point) == 3:
          
          obj = datetime.fromisoformat(truning_point[1])
          
          if abs(timestamp - obj.timestamp()) < diff:

            diff = abs(timestamp - obj.timestamp())
            temp_point[2] = truning_point[2]
            truning_point.append('checked')
            continue


    # for point in temp_points:
    #   # print(point)


    # # print("--------------------------------- similar values to temp points ---------------------------------------")

    # day = values[0][0].split(" ")
    # day = day[0]

    for temp_point in temp_points:
      
      if temp_point[2] != 'unknown':
        continue

      obj = datetime.fromisoformat(day + ' ' + temp_point[1] + ":00")
      timestamp = obj.timestamp()

      diff = 3600
      for value in values:

        if value == values[len(values)-1]:
          break
        elif len(value) == 2:
          
          obj = datetime.fromisoformat(value[0])
          
          if abs(timestamp - obj.timestamp()) < diff:

            diff = abs(timestamp - obj.timestamp())
            temp_point[2] = value[1]
            value.append('checked')
            continue

    return temp_points
    # for point in temp_points:
    #   # print(point)
    
def val_time_slot(times, types, values): ########################### function to extract value by timestamp and graph

    data = []
    day = values[0][0].split(" ")
    day = day[0]

    for time in times:

        # # print(time)

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


        # # print(time_prev)
        # # print(time_next)
        # # print(inteval_prev)
        # # print(inteval_next)

      ####################### increase per second ###########################

        increase = (time_next[1] - time_prev[1])/(inteval_next - inteval_prev)
        # # print(time_next[1] - time_prev[1])
        # # print(inteval_next - inteval_prev)
        # # print(increase)
        time_value = time_prev[1] + increase * abs(inteval_prev)
        # # print(time_value)      
        data.append(['bottom', time, time_value])

    return data

def getPachinko(driver, link):

    driver.get(link)
    pass_agreement(driver, link)

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
            
def getSlot(driver, link):

    driver.get(link)
    pass_agreement(driver, link)

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


################################   Main Page    ############################################



def dashboard(request):
    
    context = {}
    if request.session.keys():

        total_shop = Shop.objects.all().count()
        total_machine = Machine.objects.all().count()
        total_unit = Unit.objects.all().count()
        total_pachinko = Pachinko.objects.all().count()
        total_slot = Slot.objects.all().count()
        total_data = Data.objects.all().count()
        
        context = {'total_shop':total_shop,'total_machine':total_machine,'total_unit':total_unit,'total_data':total_data}
        return render(request, 'dashboard.html', context)

    else:
        return render(request, 'login.html', context)

def login(request, msg):
	context = {'msg':msg}
	return render(request, 'login.html', context)

def register(request):
	context = {}
	return render(request, 'register.html', context)

def shop(request):
    context = {}        
    if request.session.keys():
        return render(request, 'shop.html', context)
    else:
        return render(request, 'login.html', context)

def machine(request):      
    if request.session.keys():
        context = {'shop':[{'id': shop.id,'shop': shop.shop} for shop in Shop.objects.all().order_by("-created_at")]}
        return render(request, 'machine.html', context)
    else:
        return render(request, 'login.html', context)

def unit(request):      
    if request.session.keys():
        context = {'unit':[{'id': unit.id,'shop': unit.shop,'machine': unit.machine,'unit': unit.unit,'ps': unit.ps} for unit in Unit.objects.all().order_by("-created_at")]}
        return render(request, 'unit.html', context)
    else:
        return render(request, 'login.html', context)

def data(request):
    context = {}      
    if request.session.keys():
        return render(request, 'data.html', context)
    else:
        return render(request, 'login.html', context)    



##################################### Action #########################################

#logout
def logout(request):
    context = {}
    request.session.clear()    
    return render(request, 'login.html', context)

#login
def loginUser(request):

    if request.method == "POST":
        
        user = [{'id': user.id, 'name': user.name, 'email': user.email, 'password': user.password, 'state': user.state} for user in User.objects.filter(email=request.POST['email'])]
        
        if len(user) != 0:

            if(user[0]['password'] == request.POST['password']):
                
                # python manage.py migrate sessions

                request.session['id'] = user[0]['id']
                request.session['name'] = user[0]['name']
                request.session['email'] = user[0]['email']

                total_shop = Shop.objects.all().count()
                total_machine = Machine.objects.all().count()
                total_unit = Unit.objects.all().count()
                total_pachinko = Pachinko.objects.all().count()
                total_slot = Slot.objects.all().count()

                context = {'total_shop':total_shop,'total_machine':total_machine,'total_unit':total_unit,'total_pachinko':total_pachinko,'total_slot':total_slot}
                return render(request, 'dashboard.html', context)

            else:
                context = {"msg":"Fail Login - Invalid Password"}
        else:
            context = {"msg":"Fail Login - Nonregistered Email"}
        
        return render(request, 'login.html', context)

#register
def registerUser(request):

    if request.method == "POST":

        if len(User.objects.filter(email=request.POST['email'])) == 0:

            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            secret_key = get_random_string(60, chars)

            user = User.objects.create(name=request.POST['name'], email=request.POST['email'], password=request.POST['password'], token=secret_key)
            user.save()
            saved_id = User.objects.latest('id').id
            context = {"msg":"User was registered"}
        else:
            context = {"msg":"Fail Registration - Duplicated Email"}
        
        return render(request, 'login.html', context)

#addShop
def addShop(request):

    if request.method == "POST":
        
        if len(Shop.objects.filter(shop=request.POST['shop'])) == 0:
                        
            shop = Shop.objects.create(shop=request.POST['shop'],pachinko_rate=request.POST['pachinko_rate'],slot_rate=request.POST['slot_rate'],created_by_id=1,status=request.POST['mobile'])
            shop.save()
            saved_id = Shop.objects.latest('id').id            

            return JsonResponse({'saved_id':saved_id})

        else:
            return HttpResponse("exist")

#getShop
def getShop(request):

    if request.method == "GET":
        shop = [{'id': shop.id,'shop': shop.shop,'pachinko_rate': shop.pachinko_rate,'slot_rate': shop.slot_rate,'created_at':shop.created_at} for shop in Shop.objects.all().order_by("-created_at")]
        return JsonResponse({'shop':shop})

#delShop
def delShop(request):

    if request.method == "GET":
        ids = request.GET['ids']
        arr = []
        arr = ids.split(",")

        for id in arr:
            if id != 'ids':
                shop = Shop.objects.filter(id=id)
                shop.delete()

                machine = Machine.objects.filter(shop_id=id)
                machine.delete()

                unit = Unit.objects.filter(shop_id=id)
                unit.delete()

        return HttpResponse('delete')

#getMachine
def getMachine(request):

    if request.method == "GET":
        shop_id = request.GET['shop_id']
        if shop_id == '':
            shop_id = 0
        ps = request.GET['ps']
        machine = [{'id': machine.id,'url': machine.url,'shop': machine.shop,'machine': machine.machine,'created_at':machine.created_at} for machine in Machine.objects.filter(shop_id=shop_id,ps=ps).order_by("-created_at")]
        return JsonResponse({'machine':machine})

#getUnit
def getUnit(request):

    if request.method == "GET":

        shop = request.GET['shop']
        machine = request.GET['machine']
        unit = request.GET['unit']
        page = request.GET['page']
        start = ( int(page) - 1 ) * 100

        total_unit = Unit.objects.filter(shop__contains=shop,machine__contains=machine,unit__contains=unit).count()
        unit = [{'id': unit.id,'url': unit.url,'shop': unit.shop,'machine': unit.machine,'unit': unit.unit,'ps': unit.ps,'created_at':unit.created_at} for unit in Unit.objects.filter(shop__contains=shop,machine__contains=machine,unit__contains=unit).order_by("-created_at")[start:start + 100]]

        return JsonResponse({'unit':unit,'total_unit':total_unit})

#getData
def getData(request):

    if request.method == "GET":
        
        unit = request.GET['unit']
        page = request.GET['page']
        start = ( int(page) - 1 ) * 100

        if unit == '':
            total_data = Data.objects.all().order_by("-created_at").count()
            data = [{'id': data.id,'url': data.url,'shop': data.shop,'machine': data.machine,'unit': data.unit,'ps': data.ps,'most_bonus': data.most_bonus,'probability': data.probability,'BB_probability': data.BB_probability,'RB_probability': data.RB_probability,'cumulative_start': data.cumulative_start,'yesterday_start': data.yesterday_start,'last_value': data.last_value,'table': data.table,'graph': data.graph,'created_at':data.created_at} for data in Data.objects.all().order_by("-created_at")[start:start + 100]]
        else:
            total_data = Data.objects.filter(unit=unit).order_by("-created_at").count()
            data = [{'id': data.id,'url': data.url,'shop': data.shop,'machine': data.machine,'unit': data.unit,'ps': data.ps,'most_bonus': data.most_bonus,'probability': data.probability,'BB_probability': data.BB_probability,'RB_probability': data.RB_probability,'cumulative_start': data.cumulative_start,'yesterday_start': data.yesterday_start,'last_value': data.last_value,'table': data.table,'graph': data.graph,'created_at':data.created_at} for data in Data.objects.filter(unit=unit).order_by("-created_at")[start:start + 100]]
        
        return JsonResponse({'data':data,'total_data':total_data})




















































































##################################### Shop Thread5 ##############################


def mobile_pass_agreement(mobile_driver, link):
    
    while True:

        current_url = ''
        try:
            current_url = mobile_driver.current_url
        except TimeoutException:
            print("Loading took too much time!")
            print(link)
            mobile_driver.refresh()
            mobile_driver.get(link)
            mobile_pass_agreement(mobile_driver, link)


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
        getMobileMachines(mobile_driver, link)


    # delay = 5 # seconds
    # try:
    #     content = WebDriverWait(mobile_driver, delay).until(EC.presence_of_element_located((By.XPATH, '//section')))
    #     # print("Page is ready!")
    # except TimeoutException:
    #     print("Loading took to get content too much time!")
    #     print(link)
    #     mobile_driver.refresh()
    #     getMobileMachines(mobile_driver, link)

    mobile_pass_agreement(mobile_driver,link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

    nextListBtn = soup.find(id="nextListBtn")

    machines = []

    if nextListBtn == None:
        section = soup.find('section')
        ul = section.find('ul')

        if ul == None:
            return machines
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
            time.sleep(1)
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


def getMobileUnits(mobile_driver, link):

    # mobile_driver.set_page_load_timeout(5)    
    # try:
    #     mobile_driver.get(link)
    # except NoSuchElementException:

    #     print('stop')
    #     time.sleep(5)
    #     mobile_driver.refresh()
        # getMobileUnits(mobile_driver, link)
        # mobile_driver.get(link)

    
    try:
        mobile_driver.get(link)

    except:
        print("Loading took to get link too much time!")
        print(link)
        getMobileUnits(mobile_driver, link)

    # delay = 5 # seconds
    # try:
    #     content = WebDriverWait(mobile_driver, delay).until(EC.presence_of_element_located((By.XPATH, '//article')))
    #     # print("Page is ready!")
    # except TimeoutException:
    #     print("Loading took too much time!")
    #     print(link)
    #     mobile_driver.refresh()
    #     getMobileUnits(mobile_driver, link)

    mobile_pass_agreement(mobile_driver,link)

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')
    tbody = soup.find('tbody')
    
    if tbody == None:
        time.sleep(5)
        mobile_driver.refresh()
        getMobileUnits(mobile_driver,link)

    trs = []
    try:
        trs = tbody.findAll('tr')
    except:
        time.sleep(5)
        mobile_driver.refresh()
        getMobileUnits(mobile_driver,link)    

    units = []
    for tr in trs:

        tds = tr.findAll('td')

        unit = tds[1].find('a').getText()
        url = tds[1].find('a').attrs['href']
        # cumulative_start = tds[2].getText()
        # total_jackpot = tds[3].getText()
        # first_hit = tds[4].getText()
        # probability_change = tds[5].getText()
        # jackpot_probability = tds[6].getText()
        # probability = tds[7].getText()
        # most_bonus = tds[8].getText()
        # yesterday_start = tds[9].getText()
        units.append({'unit':unit, 'url':url})

    return units


thread_num = 5
startShopList = list()
Flag = False

def threaded_shop(thread_index):    

    global Flag
    Flag = True

    
    global startShopList
    
    mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)

    count = 1
    for shop_id in startShopList:
        Flag = True
        if count%thread_num == thread_index - 1:

            shop = Shop.objects.get(id=shop_id)

            # if shop.status == 931931:
            #     driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
            # else:
            #     mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)

            machine_list = list()
            unit_list = list()

            if shop.pachinko_rate != '':
                pachinko_url = "https://daidata.goraggio.com/" + shop.shop + "/list?mode=psModelNameSearch&bt=" + shop.pachinko_rate + "&ps=P"            
                
                pachinko_machines = getMobileMachines(mobile_driver, pachinko_url)
                # if shop.status == 931931:
                #     pachinko_machines = getMachines(driver, pachinko_url)
                # else:
                #     pachinko_machines = getMobileMachines(mobile_driver, pachinko_url)

                for machine in pachinko_machines:
                    Flag = True
                    # print(machine)
                    # machine_mdl = Machine.objects.create(url=machine['url'],shop=shop.shop,machine=machine['machine'],ps='P',shop_id=shop_id,created_by_id=1)
                    # machine_mdl.save()
                    # saved_machine_id = Machine.objects.latest('id').id
                    machine_list.append(Machine(url=machine['url'],shop=shop.shop,machine=machine['machine'],ps='P',shop_id=shop_id,created_by_id=1))
                    saved_machine_id = 1

                    units = getMobileUnits(mobile_driver, machine['url'])
                    # if shop.status == 931931:
                    #     units = getUnits(driver, machine['url'])
                    # else:
                    #     units = getMobileUnits(mobile_driver, machine['url'])

                    for unit in units:
                        # print(unit)
                        # unit_mdl = Unit.objects.create(url=unit['url'],shop=shop.shop,machine=machine['machine'],unit=unit['unit'],ps='P',shop_id=shop_id,machine_id=saved_machine_id,created_by_id=1,status=shop.status)
                        # unit_mdl.save()
                        unit_list.append(Unit(url=unit['url'],shop=shop.shop,machine=machine['machine'],unit=unit['unit'],ps='P',shop_id=shop_id,machine_id=saved_machine_id,created_by_id=1,status=shop.status))

                    if len(unit_list) > 100:
                        bulk_msj = Unit.objects.bulk_create(unit_list)
                        unit_list = []

                if len(machine_list) > 50:
                    bulk_obj = Machine.objects.bulk_create(machine_list)
                    machine_list = []

                        # if shop.status == 931931:
                        #     driver.quit()
                        #     driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
                        # else:
                        #     mobile_driver.quit()
                        #     mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)


            if shop.slot_rate != '':

                slot_url = "https://daidata.goraggio.com/" + shop.shop + "/list?mode=psModelNameSearch&bt=" + shop.slot_rate + "&ps=S"
                
                slot_machines = getMobileMachines(mobile_driver, slot_url)
                # if shop.status == 931931:
                #     slot_machines = getMachines(driver, slot_url)
                # else:
                #     slot_machines = getMobileMachines(mobile_driver, slot_url)

                for machine in slot_machines:
                    Flag = True
                    # print(machine)
                    # machine_mdl = Machine.objects.create(url=machine['url'],shop=shop.shop,machine=machine['machine'],ps='S',shop_id=shop_id,created_by_id=1)
                    # machine_mdl.save()
                    # saved_machine_id = Machine.objects.latest('id').id  
                    machine_list.append(Machine(url=machine['url'],shop=shop.shop,machine=machine['machine'],ps='S',shop_id=shop_id,created_by_id=1))
                    saved_machine_id = 1   

                    units = getMobileUnits(mobile_driver, machine['url'])
                    # if shop.status == 931931:
                    #     units = getUnits(driver, machine['url'])
                    # else:
                    #     units = getMobileUnits(mobile_driver, machine['url'])
                    for unit in units:
                        # print(unit)
                        # unit_mdl = Unit.objects.create(url=unit['url'],shop=shop.shop,machine=machine['machine'],unit=unit['unit'],ps='S',shop_id=saved_id,machine_id=saved_machine_id,created_by_id=1)
                        # unit_mdl.save()
                        unit_list.append(Unit(url=unit['url'],shop=shop.shop,machine=machine['machine'],unit=unit['unit'],ps='S',shop_id=shop_id,machine_id=saved_machine_id,created_by_id=1,status=shop.status))


                    if len(unit_list) > 100:
                        bulk_msj = Unit.objects.bulk_create(unit_list)
                        unit_list = []

                if len(machine_list) > 50:
                    bulk_obj = Machine.objects.bulk_create(machine_list)
                    machine_list = []

                        # if shop.status == 931931:
                        #     driver.quit()
                        #     driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)
                        # else:
                        #     mobile_driver.quit()
                        #     mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)

            # if shop.status == 931931:
            #     driver.quit()
            # else:
            #     mobile_driver.quit()

            if len(machine_list) > 0:
                bulk_obj = Machine.objects.bulk_create(machine_list)

            if len(unit_list) > 0:
                bulk_msj = Unit.objects.bulk_create(unit_list)


            time.sleep(5)

        count += 1

    mobile_driver.quit()
    Flag = False
    
#Start-Shop.
def startShop(request):

    if request.method == "GET":
        ids = request.GET['ids']
        arr = []
        arr = ids.split(",")

        global startShopList
        startShopList = []

        for id in arr:
            if id != 'ids':
                startShopList.append(id)   

        global Flag
        if Flag:
            return HttpResponse('yet')

        global UnitFlag
        if UnitFlag:
            return HttpResponse('yet')

        threads = []
        for thread_index in range(1, thread_num + 1):
            Shopthread = Thread(target=threaded_shop,args=(thread_index,))
            Shopthread.start()

        return HttpResponse('started')

#################################### UNIT #########################################

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


def getMobileData(mobile_driver, link, ps):
    
    try:
        mobile_driver.get(link)
    except:
        getMobileData(mobile_driver, link, ps)
            
    mobile_pass_agreement(mobile_driver,link)
    
    timeout = 30
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "#today_graph svg#graph"))
        WebDriverWait(mobile_driver, timeout).until(element_present)
    except TimeoutException:
        return {'most_bonus':'',
            'cumulative_start':'',
            'probability':'',
            'yesterday_start':'',
            'BB_probability':'',
            'RB_probability':'',
            'last_value':'',
            'table':[],
            'graph':''}

        print("Loading took to get link too much time!")
        print(link)
        getMobileData(mobile_driver, link, ps)


    ##############################################################

    soup = BeautifulSoup(mobile_driver.page_source, 'html.parser')

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
        if (int(mobile_graph_values[i]) > int(mobile_graph_values[i-1])) and (int(mobile_graph_values[i]) > int(mobile_graph_values[i+1])):
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

UnitThread_num = 10
startUnitList = list()
UnitFlag = False

def threaded_unit(thread_index):

    global UnitFlag
    UnitFlag = True

    today = datetime.today().strftime('%Y-%m-%d')
    # today = '2022-02-23'
    # global UnitInterval

    data_list = list()
    mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)
    
    global startUnitList
    total_unit = len(startUnitList)
    inteval = total_unit/UnitThread_num
    count = 1

    for unit in startUnitList:
        
        if (thread_index - 1)*inteval < count and count <= thread_index*inteval:            

            UnitFlag = True
            link = unit.url + '&target_date=' + today + '&gd=0'

            # print(link)
            data = getMobileData(mobile_driver, link, unit.ps)

            data_list.append(
                Data(url=link,shop=unit.shop,machine=unit.machine,unit=unit.unit,ps=unit.ps,
                        most_bonus=data['most_bonus'],
                        probability=data['probability'],
                        BB_probability=data['BB_probability'],
                        RB_probability=data['RB_probability'],
                        cumulative_start=data['cumulative_start'],
                        yesterday_start=data['yesterday_start'],
                        last_value=data['last_value'],
                        table=str(data['table']),
                        graph=data['graph'],
                        shop_id=unit.shop_id,machine_id=unit.machine_id,unit_id=unit.id,created_at=today,created_by_id=1)
                )

            if len(data_list) > 100:
                bulk_obj = Data.objects.bulk_create(data_list)
                data_list = []
                UnitFlag = True
                mobile_driver.quit()
                mobile_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = mobile_options)

        count += 1
    
    if len(data_list) > 0:
        bulk_obj = Data.objects.bulk_create(data_list)

    mobile_driver.quit()
    UnitFlag = False            

#Start-Unit.
def startScrap(request):
    
    if request.method == "GET":  

        global Flag
        if Flag:
            return HttpResponse('yet')

        global UnitFlag
        if UnitFlag:
            return HttpResponse('yet')


        global startUnitList
        startUnitList = Unit.objects.all()
        time.sleep(10)
        threads = []
        for thread_index in range(1, UnitThread_num + 1):
            UnitThread = Thread(target=threaded_unit,args=(thread_index,))
            UnitThread.start()
            time.sleep(10)

        return HttpResponse('started')



def checkScrap(request):

    if request.method == "GET":

        mode = request.GET['mode']

        global Flag
        if Flag:
            return HttpResponse('yet')

        global UnitFlag
        if UnitFlag:
            return HttpResponse('yet')
        
        
        return HttpResponse('yes')

        

