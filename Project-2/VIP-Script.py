from netmiko import ConnectHandler
import socket


#Internal Load balancer get change frequentlly
#the needs come to change its mapping when needed

# >>>>>>>>>>>>>>>>>>>> Get Internal ELB's new IPs  <<<<<<<<<<<<<<<<<<<<<<<

a_records = socket.getaddrinfo("internal.elb.amazonaws.com",0,0,0,0)

ip_list = []
#get new ip address
for result in a_records:
  ip_list.append(result[-1][0])
ip_list = list(set(ip_list))
#print('all list',ip_list)
#print('List[0]',ip_list[0])

#to get first ip in the list
new_aggr_elb=ip_list[0]


# >>>>>>>>>>>>>>>>>>>> Fortigate Remote connection <<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>> Through Netmiko <<<<<<<<<<<<<<<<<<<<<<<
               
FG_details = {
	'device_type': 'fortinet',
	'host': '192.168.10.10',
	'username': 'admin-user',
	'password': 'AdminPass',
}

net_conn = ConnectHandler(**FG_details)
#print('in')
config_commands=["config firewall vip"," edit web-server-vip", "set mappedip {}".format(new_aggr_elb),"next","end"]
output=net_conn.send_config_set(config_commands)
print(output)
