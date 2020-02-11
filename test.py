from selenium import webdriver
import requests
import datetime
import io
import re
import os
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import json
from sqlalchemy import desc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
def remove_word(text):


    if re.search('[0-9]{2}ГРН',text):
        text=text[0:text.find('ГРН')-2]
        return text

    elif re.search('Страница',text):
        text=text[0:text.find('Страница')]
        return text

    else:
       return text
def check():
    print('Check')
def extract_text_from_pdf(file_inn):
    file = os.listdir('D:\\Data\\send\\')
    files_name = ''
    for item in file:
        if re.search(str(file_inn) , item):
            files_name ='D:\\Data\\send\\'+ item
            break
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager , fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager , converter)
    count=0
    with open(files_name , 'rb') as fh:
        for page in PDFPage.get_pages(fh ,
                                      caching=True ,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            count+=1
            if count==3:
                break

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        print(text)
        return text

def get_director(file_inn):
    text=extract_text_from_pdf(file_inn)
    MAIN_TEXT='Сведения о лице, имеющем право без доверенности действовать от имени юридическоголица'
    if re.search(MAIN_TEXT, text):
        start = text.find(MAIN_TEXT) + len(MAIN_TEXT)
        max_end = text.find('Сведения об учредителях (участниках) юридического лица')
        if max_end==-1:
            max_end = text.find('Сведения о видах экономической деятельности по Общероссийскому классификатору')
        director_text=text[start:max_end]
        position_start=director_text.find('Должность')
        position_end=director_text.find('ГРН и дата внесения в ЕГРЮЛ записи')
        position=director_text[position_start:position_end]
        try:
            temp=re.search('[А-Я]{8}' , position)
            if re.search('[A-Я]{11}\s[А-Я]{8}',position):
                position=re.search('[A-Я]{11}\s[А-Я]{8}',position).group(0)
                director_name={}

                start=director_text.find('Фамилия')
                end=director_text.find('Имя')
                director_name['surnames']=director_text[start+len('Фамилия'):end-2]
                start = director_text.find('Имя')
                end = director_text.find('Отчество')
                director_name['name']=director_text[start+len('Имя'):end-2]
                start = director_text.find('Отчество')
                end = director_text.find('ИНН')
                director_name [ 'second_name' ] = director_text [ start + len('Отчество'):end-2 ]
                director_name [ 'position' ] = 'Генеральный Директор'
                return director_name
            elif re.search('[А-Я]{8}',position):
                    position = re.search('[А-Я]{8}', position).group(0)
                    director_name = {}

                    start = director_text.find('Фамилия')
                    end = director_text.find('Имя')
                    director_name [ 'surnames' ] = director_text [ start + len('Фамилия'):end-2 ]
                    start = director_text.find('Имя')
                    end = director_text.find('Отчество')
                    director_name [ 'name' ] = director_text [ start + len('Имя'):end-2 ]
                    start = director_text.find('Отчество')
                    end = director_text.find('ИНН')
                    director_name [ 'second_name' ] = director_text [ start + len('Отчество'):end-2]
                    director_name['position']='Директор'
                    return director_name
            elif re.search('Руководитель', director_text):

                director_name = {}

                start = director_text.find('Фамилия')
                end = director_text.find('Имя')
                director_name [ 'surnames' ] = director_text [ start + len('Фамилия'):end - 2 ]
                start = director_text.find('Имя')
                end = director_text.find('Отчество')
                director_name [ 'name' ] = director_text [ start + len('Имя'):end - 2 ]
                start = director_text.find('Отчество')
                end = director_text.find('ИНН')
                director_name [ 'second_name' ] =remove_word(director_text [ start + len('Отчество'):end - 2 ])
                director_name['position']='Руководитель юридического лица'
                return director_name
            else:
                director_name = {}

                start = director_text.find('Фамилия')
                end = director_text.find('Имя')
                director_name [ 'surnames' ] = director_text [ start + len('Фамилия'):end - 2 ]
                start = director_text.find('Имя')
                end = director_text.find('Отчество')
                director_name [ 'name' ] = director_text [ start + len('Имя'):end - 2 ]
                start = director_text.find('Отчество')
                end = director_text.find('ИНН')
                director_name [ 'second_name' ] = remove_word(director_text [ start + len('Отчество'):end - 2 ])

                start=director_text.find('Должность')
                end=director_text.find('ГРН ',start,len(director_text))
                director_name [ 'position' ] = director_text[start+len('Должность'):end-2]
                return director_name


        except Exception as e:
            print(e.args)
            return -1
        print(position)
def rename_file(inn):
    files = os.listdir('D:\\Data\\pdf\\')
    # files_name = os.path.basename(files [ 0 ])
    for item in files:
        if re.search(inn,item):
            file_name=item
            break
    try:
        os.rename('D:\\Data\\pdf\\' + file_name, 'D:\\Data\\send\\' + str(inn) + '.pdf')
    except:
        print('уже существует')
    # os.remove('D:\\Data\\pdf\\' + file_name)
    return 'D:\\Data\\send\\' + str(inn) + '.pdf'
def download_pdf(inn):
    fp = webdriver.FirefoxProfile()
    mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", "D:\\Data\\pdf\\")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    fp.set_preference("pdfjs.disabled", True)


   # url_main='https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    url='https://pb.nalog.ru/search.html#quick-result?query={}&mode=quick&page=1&pageSize=10'.format(inn)

    driver = webdriver.Firefox(firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe', firefox_profile=fp)


    driver.get(url)

    try:
        editor = WebDriverWait(driver , 10).until(EC.visibility_of_element_located((By.CLASS_NAME , 'result-group')))
    except:
        try:
            editor=driver.find_element_by_class_name('search-result-group')
            if editor!=None:
                driver.close()
                return -2
        except:
            driver.close()
            return -1
    # link=driver.find_element_by_class_name('lnk company-info')
    link = editor.get_attribute('data-href')
    if link != None:
        link = url + link
        driver.get(link)

        list_data = driver.find_elements_by_class_name('field')
        vipiska = WebDriverWait(driver , 10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/a[1]'))).click()
        rename_file(inn)
        result={}
        for item in list_data:
            try:
                temp_item=item.text.split('\n')
                result[temp_item[0]]=temp_item[1]
            except:
                continue
        print_result=''
        for k,i in result.items():
            print_result+=k+' '+i+'\n'
        driver.close()
        return print_result
def get_inn():
    driver = webdriver.Firefox()
    driver.get('https://egrul.nalog.ru/index.html')
    check_element = driver.find_element_by_id("unichk_0")
    check_element.click()
    editor = driver.find_element_by_id('query')
    editor.send_keys('ООО Домашний интерьер')
    driver.find_element_by_id('btnSearch').click()

    header = WebDriverWait(driver , 10).until(
        EC.visibility_of_element_located((By.XPATH , '/html/body/div[1]/div[3]/div/div[1]/div[4]/div/div[2]/a')))
    inn = WebDriverWait(driver , 10).until(
        EC.visibility_of_element_located((By.XPATH , '/html/body/div[1]/div[3]/div/div[1]/div[4]/div/div[3]')))
    result_inn = dict(
        header=header.text ,
        text=inn.text,
    )
    data=re.search('ИНН: [0-9]{10}', result_inn['text']).group().replace('ИНН: ','')

    return data

get_director('1655407381')