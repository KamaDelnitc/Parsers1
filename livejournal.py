from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import requests
import asyncio
import io
from DB import DBWork

from bs4 import BeautifulSoup
import json
from sqlalchemy import desc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
# prox = Proxy()
# prox.proxy_type = ProxyType.MANUAL
# prox.http_proxy = "1.0.0.40:80"
# # prox.socks_proxy = "ip_addr:port"
# prox.ssl_proxy = "163.172.147.94:8811"

# capabilities = webdriver.DesiredCapabilities.FIREFOX
# prox.add_to_capabilities(capabilities)

# driver = webdriver.Chrome(desired_capabilities=capabilities)


proxy = {
    'http': '181.30.28.14:31',
    'https': '157.245.224.29:31'
}


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Livejournal():
    driver=None
    con=None
    def __init__(self):
        self.con=DBWork()
        # fp = webdriver.FirefoxProfile()
        # fp.set_preference("network.proxy.type", 1)
        # fp.set_preference("network.proxy.http",'142.93.57.37')
        # fp.set_preference("network.proxy.http_port",int('80'))
        # fp.set_preference("general.useragent.override","whater_useragent")
        # fp.update_preferences()
        self.driver = webdriver.Firefox()

    async def find(self, text):
        for j in range (1, 10):
            self.driver.get('https://www.livejournal.com/rsearch?page={}&q={}&searchArea=post'.format(str(j), text))
            ul=self.driver.find_element_by_class_name('rsearch-result')
            await asyncio.sleep(3)
            for i in range (1,5):
                li = ul.find_element_by_xpath('//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[{}]'.format(str(i)))
                time.sleep(3)
                author=li.find_element_by_xpath('//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[{}]/div/div/span[1]/a[2]'
                                    .format(str(i))).get_attribute('href')

                title=li.find_element_by_xpath('//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[{}]/div/a'.format(str(i)))
                titletext=title.text
                urltitle=title.get_attribute('href')
                try:
                    dttm=li.find_element_by_xpath('//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[{}]/div/div/span[3]'.format(str(i))).text
                except:
                    dttm = li.find_element_by_xpath(
                '//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[{}]/div/div/span[2]'.format(
                    str(i))).text
                articleurl=requests.get(urltitle)
                data=BeautifulSoup(articleurl.text, 'html.parser')
                try:
                    article=data.find('article').contents[5].text
                except:
                    try:
                        article=data.find('div',{'class':'asset-body'}).text
                    except:
                        try:
                            article=data.find('div',{'class':'entry-content'}).text
                        except:
                            continue
                dicttemp={
                    'article':article,
                    'title':titletext,
                    'dttm':dttm,
                    'author': author
                    }
                self.con.Add(dicttemp)
        self.con.End()
# data=driver.find_element_by_xpath('//*[@id="js"]/body/div[2]/div[5]/div[1]/div/section/div/div[2]/ul/li[3]/div/p/span').text
# driver.get('https://www.reverso.net/text_translation.aspx?lang=RU')