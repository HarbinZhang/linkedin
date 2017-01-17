from multiprocessing import Processfrom socket import *import jsonfrom threading import Threadimport workerimport randomfrom time import sleep# users = {'haibin610@yeah.net':'coolman','xichengmurong@gmail.com':'zhang518','binyuea@gmail.com':'coolman','xichengmu@tutanota.com':'coolman',}url = 'https://www.linkedin.com/in/haibinzhang'class Master:	def __init__(self, port_number):		self.port_number = port_number		#self.accounts = {'longkebofu@tutanota.com':'coolman','haibin610@tutanota.com':'coolman','xicheliu@tutanota.com':'coolman', 'mengkesiji@tutanota.com':'coolman'}		self.accounts = {'melafeida@tutanota.com':'coolman','melala@tutanota.com':'coolman'}		self.worker_process = []		self.num_workers = len(self.accounts)		self.shutflag = False		#workers = {worker_id:{'job':job_id, status = 'busy'}}, containing all workers		self.workers = {}		self.ready_workers = []		self.fault_cnt = 0		self.index = 0		self.urls = []		master_tcp = socket(AF_INET, SOCK_STREAM)		master_tcp.bind(('127.0.0.1',self.port_number))		master_tcp.listen(20)		self.do_setup_thread()		# print "do_setup_thread"+str(len(self.worker_process))		max_data = 1024		# self.deal()		while True:			# if self.shutdown:				# print (" I have been killed!!! i.e. : shutdown (from main process) ")				# time.sleep(10)				# continue			#print('listenning new msg')			conn, addr = master_tcp.accept()			# print('master connected')            			new_job = ""			# if len(self.urls) == 0:			# 	for i in range(self.num_workers):			# 		self.send_msg({'message_type':'done'},i) 			# 	print 'needing new job'			while True:				   				message = conn.recv(max_data)				new_job += message.decode("utf-8")				if len(message)!= max_data:					# print(new_job)					print("master receive msg:" + new_job) 					self.handle_msg(new_job)					# if "shutdown" == self.handle_msg(new_job):					#conn.shutdown()break					break		def handle_msg(self,new_msg):		msg = json.loads(new_msg)		if not msg.get('message_type'):			return		if msg['message_type'] == 'status':			worker_id = msg['worker_number']			if msg['status'] == 'ready':				self.assignJob(worker_id)				self.fault_cnt = 0			elif msg['status'] == 'bad':				self.fault_cnt += 1				if self.fault_cnt >= 6:					print "That's bad, going to shutdown.."					self.shutdown()				else:					self.assignJob(worker_id)								elif msg['status'] == 'shutdown':				self.worker_process[msg['worker_number']].terminate()				print (" shutdown workers' processes which id is ", msg['worker_number'])		elif msg['message_type'] == "shutdown":			self.shutdown()		elif msg['message_type'] == 'new_master_job':			# if self.shutflag == True:			# 	self.do_setup_thread()			# 	self.shutflag = False			self.num = msg['num']			self.urls = self.popUrl(self.num)			self.index = 0			for i in self.ready_workers + []:				if len(self.urls) > 0:					url = self.urls.pop()					self.index += 1					self.send_msg({'message_type':'new_job','url':url,'index':self.index, 'num':self.num},i)					self.ready_workers.remove(i)				else:					break		return        	def shutdown(self):		for i in range(self.num_workers):			self.send_msg({'message_type':'shutdown'},i) 		self.shutflag = True		self.index = 0		if len(self.urls) > 0:			print ("urls backuped.")			open('relatedLinks', 'ab').writelines(self.urls)				return	def assignJob(self, worker_id):		if len(self.urls) > 0:			url = self.urls.pop()			self.index += 1			self.send_msg({'message_type':'new_job','url':url,'index':self.index, 'num':self.num},worker_id)			self.workers[worker_id] = 'busy'		else:			self.workers[worker_id] = 'ready'			self.ready_workers.append(worker_id)		return	def send_msg(self, msg, worker_id):		message = json.dumps(msg)		try:			send_job_to_worker = socket(AF_INET, SOCK_STREAM)			send_job_to_worker.connect(('127.0.0.1', self.port_number+worker_id+1))			send_job_to_worker.sendall(str.encode(message))			send_job_to_worker.close()			#iterately envoke workers, if succeed, change worker status infomation		except error as e:			print(str(e))			print("Failed to send job to master.")   			def do_setup_thread(self):		#initiate the first worker_number, actually it always begin from 0		worker_id = 0		for key in self.accounts.keys():			process = Process(target=self.create_worker_Process, args=(worker_id,key,self.accounts[key],))			process.start()			self.workers[worker_id] = 'created'			self.worker_process.append(process)			worker_id += 1		return        		def create_worker_Process(self, worker_number, user, pwd):		worker_process = worker.Worker(worker_number,self.port_number+worker_number+1,self.port_number,user,pwd)       	def popUrl(self, num):		lines = open('relatedLinks').readlines()		if num >= len(lines):			num = len(lines) - 1 		open('relatedLinks', 'w').writelines(lines[num: -1])		return lines[0:num]	def dealNew(self, url):		# if self.preLoad(url):			# self.loadPage()		worker_id = 0		self.index += 1		job_msg = {"url":url,"index":self.index}		message = json.dumps(job_msg)		# print job_msg		try:			send_job_to_worker = socket(AF_INET, SOCK_STREAM)			send_job_to_worker.connect(('127.0.0.1', self.port_number+worker_id+1))			send_job_to_worker.sendall(str.encode(message))			send_job_to_worker.close()			#iterately envoke workers, if succeed, change worker status infomation		except error as e:			print(str(e))			print("Failed to send job to master.")            