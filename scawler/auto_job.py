import click, json
from socket import *
from time import sleep

DEFAULT_PORT_NUM = 6000
DEFAULT_NUM = 400

def send(port_number=DEFAULT_PORT_NUM, num=DEFAULT_NUM):
	# Temp job to send to master (values can be changed)
	job_dict = {
		"message_type": "new_master_job",
		"num":num
	}


	message = json.dumps(job_dict)

	# Send the data to the port that master is on
	try:
		sock = socket(AF_INET, SOCK_STREAM)
		sock.connect(("localhost", port_number))
		sock.sendall(str.encode(message))
		sock.close()
	except error:
		print("Failed to send job to master.")
	return

if __name__ == "__main__":
	index = 0
	while True:
		index += 1
		print ("send jobs, index : " + str(index))
		send()
		print ("sleeping")
		sleep(2400)	


