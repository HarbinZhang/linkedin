from multiprocessing import Process
import master


url = 'https://www.linkedin.com/in/haibinzhang'

DEFAULT_PORT_NUM = 6000


def main(port_number=DEFAULT_PORT_NUM):
	master_ = master.Master(port_number)


if __name__ == '__main__':
	main()
	# scawler = Scawler(user1,pwd1)
	# scawler.deal(1)
	# scawler.dealNew(url)

	# ceshi"url_id" : "haibinzhang"
	# soup = scawler.preLoad(url)
	# print scawler.getSkills(soup)
