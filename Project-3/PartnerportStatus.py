import socket as sock
from netmiko import ConnectHandler
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>  Fuctions section  <<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


###############      Portchecking Fuctions     ############### 
 
# function takes service ip and port and return the satus of each ip
def portchecking( ip,port):
    create_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    destination = (ip,port)
    result = create_socket.connect_ex(destination)
    if result == 0:
        status="up"
    else:
        status="down"
    create_socket.close()
    return(status)
    
    
###############         Email  Fuctions        ############### 
def SendingEmail(finalOutput):
  # Forming Email Message
  msg = MIMEMultipart()

  #Authentication part
  username = "user@xxx-company.com"
  password = "pass"
  smtphost = "mail-server.xxx-company.com"
  
  msg['From'] = 'user@xxx-company.com'
  recipients = ['network@xxx-company.com','network@patiner.com']"
  msg['To'] = ", ".join(recipients)
  msg['Subject']  = "Partner VPN Down!"
  
  # Prepare actual message
  message = "{}".format(finalOutput)
  msg.attach(MIMEText(message, 'plain'))
  
  # Send the mail
  server = smtplib.SMTP(smtphost)
  server.starttls()
  server.login(username, password)
  server.sendmail(msg['From'], recipients, msg.as_string())
  server.quit()
  #print("Successfully sent email message to %s:" % (msg['To']))

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>  Veriables section  <<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   
resultdic = {} #dictionary to save the result as service name and it status 
res = True  #to track if all service are down and changed to False when one of them ia up 
partner_Services={
        "A":["172.16.16.16",8080],
      	"B" :["172.17.17.17",8081],
        "C" :["172.18.18.18" ,8082],
}


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>  Here we go  <<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#to chek the status of the sarvices
for x,y in partner_Services.items():
    #print(x,y)   >>> output like this :    A ['172.16.16.16', 8080]  
    #print(y[0],y[1]) >>>  output like this:   172.16.16.16 8080
    #call portchecking fuction and save the result in resultdic dictionary
    resultdic[x] = portchecking(y[0],y[1])
    
#print(resultdic)  # outputlook like {'A': 'down', 'B': 'up', 'C': 'down'}

#to identify all the servs down or not and set res flag accordingly
for portstat in resultdic:
    if resultdic[portstat] != 'down' :
        res = False
        print('res',res,'{} is {}'.format(portstat,resultdic[portstat]))
        break
     
if res == True:
    print('Partner VPN Tunnel down')
    #Device Credential
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


    '''Restart VPN tunnles'''
    commands = ['diagnose vpn ike restart', 'diagnose vpn ike gateway clear']
    output = net_connect.send_config_set(commands)
    print(output)
    
    SendingEmail(resultdic)
    