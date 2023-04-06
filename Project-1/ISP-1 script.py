#Needed Libarary
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from netmiko import ConnectHandler


# >>>>>>>>>>>>>>>>>>>>  Email Function <<<<<<<<<<<<<<<<<<<<<<<
def SendingEmail(status):
  # Forming Email Message
  msg = MIMEMultipart()
  
  #Authentication part
  username = "user@xxx-company.com"
  password = "pass"
  smtphost = "mail-server.xxx-company.com"
  
  msg['From'] = 'user@xxx-company.com'
  recipients = ['network@xxx-company.com','network@patiner.com']
  msg['To'] = ", ".join(recipients)
  msg['Subject']  = "ISP-2 is Down!"
  
  # Prepare actual message
  message = "%s " %(status)
  msg.attach(MIMEText(message, 'plain'))
  
  # Send the mail
  server = smtplib.SMTP(smtphost)
  server.starttls()
  server.login(username, password)
  server.sendmail(msg['From'], recipients, msg.as_string())
  server.quit()
  #print("Successfully sent email message to %s:" % (msg['To']))


# >>>>>>>>>>>>>>>>>>>> Get VPN-Tunnel info Function <<<<<<<<<<<<<<<<<<<<<<
def FortigateGetVPNInfo():
  '''Get VPN tunnel Configuration '''
  output = net_connect.send_command('show vpn ipsec phase1-interface Partner-VPN')
  #print(output)
  result = re.findall(r'[0-9]+(?:\.[0-9]+){3}',output)
  return(result)
  
  
# >>>>>>>>>>>>>>>>>>>> Update VPN-Tunnel info Function <<<<<<<<<<<<<<<<<<<
def FortigateSetVNInfo():
  '''Set VPN tunnel Configuration '''
  commands = ['config vpn ipsec phase1-interface' , 'edit Partner-VPN' , 'set remote-gw 1.1.1.1' , 'end']
  output = net_connect.send_config_set(commands)
  #print(output)


# >>>>>>>>>>>>>>>>>>>> Fortigate Remote connection <<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>> Through Netmiko <<<<<<<<<<<<<<<<<<<<<<<

'''Device Credential'''
FG_details = {
	'device_type': 'fortinet',
	'host': '192.168.10.10',
	'username': 'admin-user',
	'password': 'AdminPass',
}

'''Connection to the device  '''
#print( f"{'#'*20} Connecting to Device {'#'*20}")
net_connect = ConnectHandler(**FG_details)
#print( f"{'#'*20} Connect to Device {'#'*20}")

hostname = '1.1.1.1' #example
response = os.system("ping " + hostname)
#and then check the response...
if response == 0:
  #print('{},is up!'.format(hostname))
  FortigateSetVNInfo()
  CurrrentIP = FortigateGetVPNInfo()
  if CurrrentIP[0] == '1.1.1.1':
     ISPname = 'ISP-1 Name'
  else:
     ISPname = 'ISP-2 Name'
  
  changed = '''
  Dears,
  
  ISP-2 is down now, and the script changed the configuration to ISP-1.
  
  The VPN is working through {} ISP.
  The Current ip: {} '''.format(ISPname,CurrrentIP[0])
  SendingEmail(changed)
  
else:
  #print('{} ,is down!'.format(hostname))
  CurrrentIP = FortigateGetVPNInfo()
  if CurrrentIP[0] == '2.2.2.2':
     ISPname = 'ISP-2 Name'
  else:
     ISPname = 'ISP-1 Name'
  changed = '''
  Dears,
  
  ISP-1 is down now, and ISP-2 also down. Nothing is modified!.
  
  The VPN is working through {} ISP.
  The Current ip: {}'''.format(ISPname,CurrrentIP[0])
  
  SendingEmail(changed)

