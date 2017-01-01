import cookielib
import os
import re
import string
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pymongo
from time import sleep
import random

class Scawler(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cnt = 0
        self.broken = False

        client = pymongo.MongoClient("localhost", 27017)
        self.db = client.mydb

        phantomjsdriver = "/Users/Harbin/Desktop/mine/vagrant/temp/linkedin/phantomjs"
        os.environ["webdriver.phantomjs.driver"] = phantomjsdriver
        self.driver = webdriver.PhantomJS(phantomjsdriver)
        self.login()


    def login(self):
        self.driver.set_page_load_timeout(7)
        baseurl = "https://www.linkedin.com/"

        self.driver.get(baseurl)
        elem = self.driver.find_element_by_id("login-email")
        elem.clear()
        elem.send_keys(self.username)
        elem = self.driver.find_element_by_id("login-password")
        elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)


    def getBackground(self, soup):
        try:
            backinfo = soup.find(id = "background-experience")
            backgrounds = []
            res = backinfo.find("div",{"class":"editable-item section-item current-position"})
            background = []
            for _ in res.findAll('a'):
                if _.getText() == "":
                    continue
                background.append(_.getText())

            for item in backinfo.findAll("div",{"class":"editable-item section-item past-position"}):
                background = []
                for _ in item.findAll('a'):
                    if _.getText() == "":
                        continue
                    background.append(_.getText())
                try:
                    background.append(item.find("p",{"class":[u"description", u"summary-field-show-more"]}).getText())
                except:
                    # print ("No description on background")
                    pass
                backgrounds.append(background + [])
            return backgrounds
        except:
            return None

    def getSkills(self, soup):
        try:
            res = soup.find(id="profile-skills")
            num = res.findAll("span", {"class": "num-endorsements"})
            skills = res.findAll("span", {"class": "endorse-item-name"})
            topskills = {}
            for i in range(len(skills)):
                tmp = str(skills[i].getText()).split('.')[0]
                try:
                    topskills[tmp] = int(num[i].getText())
                except:
                    topskills[tmp] = 0
            return topskills
        except:
            f = open('siton','ab')
            f.write(self.driver.current_url)
            f.write('\n')
            f.close()
            self.broken = True
            print "Oh, That's bad.."


        # I don't know why it cannot work
        # try: 
        #     res = soup.find(id="profile-skills").getText()
        #     num = res.findAll("span", {"class": "num-endorsements"})
        #     skills = res.findAll("span", {"class": "endorse-item-name"})
        #     topskills = {}
        #     for i in range(len(num)):
        #         tmp = str(skills[i].getText()).split('.')[0]
        #         # tmp = tmp.split('$')[0]
        #         print tmp
        #         topskills[tmp] = int(num[i].getText())
        #     return topskills
        # except:
        #     return None

    def saveProfile(self, soup):
        # url_id
        curtUrls = self.driver.current_url.split('/')[4]
        url_id = curtUrls.split('?')[0]
        # name
        try:
            name = soup.find(id="name").getText()
        except:
            name = None
        # locality
        try:
            locality = soup.find("span",{"class":"locality"}).getText()
        except:
            locality = None
        # title
        try:
            title = soup.find("p",{"class":"title"}).getText()
        except:
            title = None
        # industry
        try:
            industry = soup.find("a",{"name":"industry"}).getText()
        except:
            industry = None
        # curt_company
        try:
            curt_company = soup.find("a",{"name":"company"}).getText()
        except:
            curt_company = None
        # edu
        try:
            edu = soup.find("a",{"title":"More details for this school"}).getText()
        except:
            edu = None

        backgrounds = self.getBackground(soup)

        topskills = self.getSkills(soup)

        ans = {
            "url_id":url_id,
            "name":name,
            "locality":locality,
            "title":title,
            "industry":industry,
            "curt_company":curt_company,
            "edu":edu,
            "backgrouds":backgrounds,
            "topskills":topskills
        }

        # print ans
        # save it
        try:
            self.db.linkedin.insert(ans)
        except:
            f = open('siton','ab')
            f.write(str(ans))
            f.write('\n')
            f.close()

        if not self.broken:
            self.db.linkedinDedual.insert({"url_id":url_id})


    def loadPage(self):
        # self.driver.get(url)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # save related users
        res = soup.find_all("a", {"class": "browse-map-photo"})
        links = open('relatedLinks','ab')
        for item in res:
            links.write(str(item['href']))
            links.write('\n')
        links.close()

        # save Profile
        self.saveProfile(soup)


    def preLoad(self, url):
        self.driver.get(url)

        # for debug
        # html = self.driver.page_source
        # soup = BeautifulSoup(html)
        # return soup

        curtUrls = self.driver.current_url.split('/')[4]
        url_id = curtUrls.split('?')[0]
        self.cnt += 1
        if self.db.linkedinDedual.find({"url_id":url_id}).count() != 0:
            print "already dealed : "+str(self.cnt)+" / "+str(self.num)
            return False
        else:
            print "new one, be going to do it : "+str(self.cnt)+" / "+str(self.num)
            return True

    def popUrl(self, num):
        lines = open('relatedLinks').readlines()
        if num >= len(lines):
            num = len(lines) - 1 
        open('relatedLinks', 'w').writelines(lines[num: -1])
        return lines[0:num]

    def deal(self, num = 1):
        self.num = num
        urls = self.popUrl(num)
        while len(urls) > 0:
            url = urls.pop()
            t = 1+ random.randint(1,1000)/1000.0
            print "sleep : "+ str(t) + " s"
            sleep(1+ random.randint(1,1000)/1000.0)
            if self.preLoad(url):
                self.loadPage()

        self.driver.close()


    def dealNew(self, url):
        if self.preLoad(url):
            self.loadPage()









