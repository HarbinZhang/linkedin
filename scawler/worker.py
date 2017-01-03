from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
from threading import Thread
from socket import *
from time import sleep
import pymongo
import os
import random


class Worker:
	def __init__(self, worker_id, port_number, master_port, user, pwd):
		self.worker_id = worker_id
		self.port_number = port_number
		self.master_port = master_port

		self.username = user
		self.password = pwd
		self.fault_cnt = 0
		self.index = 0

		client = pymongo.MongoClient("localhost", 27017)
		self.db = client.mydb

		phantomjsdriver = "../lib/phantomjs"
		os.environ["webdriver.phantomjs.driver"] = phantomjsdriver
		self.driver = webdriver.PhantomJS(phantomjsdriver)
		self.login()



		worker_tcp = socket(AF_INET, SOCK_STREAM)
		worker_tcp.bind(('127.0.0.1', port_number))
		worker_tcp.listen(20)
		worker_setup = Thread(target = self.do_setup_thread, args=())
		worker_setup.start()
		max_data = 1024
		while True:
			conn, addr = worker_tcp.accept()
			print('worker connected')
			new_job = ""
			while True:
				message = conn.recv(max_data)
				new_job += message.decode("utf-8")
				if len(message)!= max_data:
					break
			self.handle_msg(new_job)

	def handle_msg(self,new_job):
		job = json.loads(new_job)
		if not job.get('message_type'):
			return
		if job['message_type'] == 'new_job':
			t = 6.0 + random.randint(1,1000)/200.0
			print "sleep : "+ str(t) + " s"			
			url = job['url']
			self.index = job['index']
			if self.preLoad(url):
				if self.loadPage():
					self.send_status_message('ready')
				else:
					self.send_status_message('bad')
		elif job['message_type'] == 'shutdown':
			self.driver.close()
			print "driver has been closed : " + str(self.worker_id)
			self.send_status_message('shutdown')
		elif job['message_type'] == 'done':
			self.driver.close()



	def do_setup_thread(self):
		# self.create_heartbeat_thread(master_heartbeat_port)
		self.send_status_message("ready")


	def send_status_message(self,status):
		status_msg = { 
			"message_type": "status", 
			"worker_number": self.worker_id,
			"status": status
		}
		t=0
		message = json.dumps(status_msg)
		while True:
			# time.sleep(t)
			# t+=1			
			try:
				worker_ready = socket(AF_INET, SOCK_STREAM)
				worker_ready.connect(('127.0.0.1', self.master_port))
				worker_ready.sendall(str.encode(message))
				worker_ready.close()
				break
			except error as e:
				print(str(e))
				print("Failed to send job to master.")




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
			self.fault_cnt += 1
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
			self.fault_cnt += 1            


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
			self.fault_cnt += 1
		# locality
		try:
			locality = soup.find("span",{"class":"locality"}).getText()
		except:
			locality = None
			self.fault_cnt += 1
		# title
		try:
			title = soup.find("p",{"class":"title"}).getText()
		except:
			title = None
			self.fault_cnt += 1
		# industry
		try:
			industry = soup.find("a",{"name":"industry"}).getText()
		except:
			industry = None
			self.fault_cnt += 1
		# curt_company
		try:
			curt_company = soup.find("a",{"name":"company"}).getText()
		except:
			curt_company = None
			self.fault_cnt += 1
		# edu
		try:
			edu = soup.find("a",{"title":"More details for this school"}).getText()
		except:
			edu = None
			self.fault_cnt += 1

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


		if self.fault_cnt >=6:
			#bad
			print "Oh, it's bad.."
			return False
		# print ans
		# save it
		try:
			self.db.linkedin.insert(ans)
		except:
			f = open('siton','ab')
			f.write(str(ans))
			f.write('\n')
			f.close()


		self.db.linkedinDedual.insert({"url_id":url_id})
		return True

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
		return self.saveProfile(soup)



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
			print "already dealed : " + str(self.index)
			return False
		else:
			print "new one, be going to do it : " + str(self.index)
			return True
