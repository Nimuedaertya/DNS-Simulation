
import sys
import socket
import json

############ init #############

# set IP and PORT of auth_server/rec_server
#UDP_IP = sys.argv[1]
#UDP_PORT = int(sys.argv[2])
UDP_IP = "127.0.0.11"
UDP_PORT = 53053

###### functions ################

    ########### PACK / UNPACKING MSG ####

    #transforms dictionary into binary string for UDP connection
def pack(msg: dict) -> str:
    return json.dumps(msg).encode()

    #transforms binary string into dictionary
def unpack(msg: str) -> dict:
    return json.loads(msg.decode('utf-8'))


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
print("Record: (A,NS,MX,SOA)")
record = input()


def modify_message():
    msg["dns.flags.response"] = 0
    msg["dns.qry.name"] = name
    msg["dns.qry.type"] = records[record]
    msg["dns.flags.recdesired"] = 1

modify_message()

#transfrom msg into binary String
msg = pack(msg)



print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % msg)

#create socket and send binary string to auth_server/rec_resolver
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(msg, (UDP_IP, UDP_PORT))
