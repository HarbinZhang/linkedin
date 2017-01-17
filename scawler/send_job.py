import click, json
from socket import *

# Configure command line options
DEFAULT_PORT_NUM = 6000
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
DEFAULT_NUM = 1

@click.command(context_settings=CONTEXT_SETTINGS)

@click.option("--port_number", "-p", "port_number",
    default=DEFAULT_PORT_NUM,
    help="The port the master is listening on, default " + str(DEFAULT_PORT_NUM))

@click.option("--num", "-n", "num",
    default=DEFAULT_NUM,
    help="The num of urls is listening on, default " + str(DEFAULT_NUM))

def main(port_number=DEFAULT_PORT_NUM, num=DEFAULT_NUM):
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

if __name__ == "__main__":
  main()
