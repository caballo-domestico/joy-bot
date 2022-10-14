import json
import os

f = open('infrastructure.json')
data = json.load(f)
hosts_text = "ec2-instance ansible_host="+data['Retrieve_ip']['value'][0]+" ansible_user=ec2-user ansible_ssh_private_key_file="+os.getenv('SSH_PATH')+" ansible_become=true"
f.close()
hosts = open('hosts', 'a+')
hosts.write(hosts_text)
hosts.close