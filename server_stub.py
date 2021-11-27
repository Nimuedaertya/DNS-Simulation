import time as t
import sys
import socket
import json

############ init #############

# set IP and PORT of rec_resolver
UDP_IP = "127.0.0.10"
UDP_PORT = 53053

###### functions ################

    ########### PACK / UNPACKING MSG ####

    #transforms dictionary into binary string for UDP connection
def pack(msg: dict) -> str:
    return json.dumps(msg).encode()

    #transforms binary string into dictionary
def unpack(msg: str) -> dict:
    return json.loads(msg.decode('utf-8'))

def timer():
    return t.clock_gettime(t.CLOCK_THREAD_CPUTIME_ID)

def modify_message():
    msg["dns.flags.response"] = 0
    msg["dns.qry.name"] = name
    msg["dns.qry.type"] = records[record]
    msg["dns.flags.recdesired"] = 1


############ constants #########

records = {"A": 1, "NS":2, "SOA": 6, "MX": 15}

# example message of client stub to auth_server/rec_server
msg = {"dns.flags.response": 0,
  "dns.flags.recdesired": 1,
  "dns.qry.name": "www.nawrocki.tns.",
  "dns.qry.type": 1
  }

############## start ##############

print("Domain: ")
name = input()
if not name[-1] == ".":
    name += "."

    #if specific record should be requested
#print("Record: (A,NS,MX,SOA)")
#record = input()
record = "A"

modify_message()

#transfrom msg into binary String
msg = pack(msg)



print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % msg)

#create socket and send binary string to auth_server/rec_resolver
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
tx = timer()
sock.sendto(msg, (UDP_IP, UDP_PORT))
t0 = timer()
while (timer() - t0) < 1:
    data, addr = sock.recvfrom(1000)
    if data:
        break
data = unpack(data)

print(" [  ANSWERS  ] ")
print("Time needed: " + str(timer()-tx))

if data["dns.count.answers"] >= 1:
    print("IP-Adress found: ", data["dns.a"])
else:
    print("0 Responses: ERROR")



