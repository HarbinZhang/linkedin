from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import sys

singleproxy = "88.157.149.250:8080"
proxytype = "http"

user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")

phan_args = ['--proxy=88.157.149.250:8080', 'proxy-type=http']
print "step 1"
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent
print "step 2"
driver = webdriver.PhantomJS(service_args=phan_args, desired_capabilities=dcap)
driver.get("https://www.whatismyip.com/")
print "step 3"
print driver.current_url

htmlpage = driver.page_source
print htmlpage.encode(sys.stdout.encoding, errors='replace')