#!/bin/sh
import cookielib
import os
import re
import string
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pymongo
from time import sleep
import random


proxy = '70.248.28.23:800'
service_args = [
    '--proxy='+proxy,
    '--proxy-type=https',
    # '--proxy-auth=username:password',
    ]

phantomjsdriver = "../lib/phantomjs"
os.environ["webdriver.phantomjs.driver"] = phantomjsdriver
driver = webdriver.PhantomJS(phantomjsdriver,service_args=service_args)
driver2 = webdriver.PhantomJS(phantomjsdriver)



driver.set_page_load_timeout(7)
driver.get('https://www.linkedin.com')
html = driver.page_source
print html
# soup = BeautifulSoup(html,'html.parser')
# print soup


# driver2.set_page_load_timeout(7)
# driver2.get('https://www.linkedin.com/')
# html2 = driver2.page_source
# soup2 = BeautifulSoup(html2,'html.parser')
# print soup2