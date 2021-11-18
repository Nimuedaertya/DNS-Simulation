
#config ###################################

if len(sys.argv) < 2:
    print("Add Record File to start")
    exit(1)

rec = sys.argv[1].open()
rec = rec.


#import ####################################

import sys
import socket
import json
import time as t

#init   ####################################


    #access log and records for this server and open filedescriptor
records = "record_" + name
log = "log_" + name
records = open(records, "r")


    #determine IP based on name and set PORT
UDP_IP = "127.0.0." + name
UDP_PORT = 53053

#functions ################################

    ################### LOG ############## 
    # prints time + name + msg to log
    # if a Message was received or send we add the content as second parameter
def put_log(msg, ls: dict = None):
   
    logg = open(log, "a")
    tmp = (time() + "A" + name + "  "+ msg + "\n")
    logg.write(tmp)
    if ls:
        for i in ls:
            tmp = (" "*5 + str(i) +": " + str(ls[i]) + "\n")
            logg.write(tmp)

    #returns timestamp for log file
def time():
    a = t.localtime()
    tmp = str(a.tm_year) + "-" +str( a.tm_mon) + "-" + str(a.tm_mday)
    tmp += "  " + str(a.tm_hour) + ":"+ str(a.tm_min) + ":" + str(a.tm_sec) + "  "
    return tmp

    ########### PACK / UNPACKING MSG ####

    #transforms dictionary into binary string for UDP connection
def pack(msg: dict):
    return json.dumps(msg).encode()

    #transforms binary string into dictionary
def unpack(msg: str):
    return json.loads(msg.decode('utf-8'))


    ############ MSG QUERY ###############

def read_msg(js):
    pass

    #####################################



#start  ####################################

    #starting UDP Server and bind socket to Port of this IP
put_log("SERVER STARTING")
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


    # Server ready to respond to messages
put_log("SERVER LISTENING")

while True:
    data, addr = sock.recvfrom(2000) # buffer size is 1024 bytes
    
        # if data has been send => transfrom back to dictionary (js)
    if data:
        #print(data) 
        msg = unpack(data)
       # print(msg)
        put_log("MSG RECV FROM: " + str(addr[0]) + ":" +str(addr[1]) , msg)
        
        #prepare message
        msg = {"dns.flags.recdesired": 1,
               "dns.qry.name": msg["dns.qry.name"],
               "dns.qry.type": msg["dns.qry.type"],
               }
        #search for requested dns 
      #  dns_request = (msg["dns.qry.name"], msg["dns.qry.type"])
        record_types = {"A": 1, "NS":2, "SOA": 6, "MX": 15}
        recordList = []
        for zeile in records:
           
            recordList = zeile.split(",")    
            
            if(recordList[0] == msg["dns.qry.name"] and record_types[recordList[1]] == msg["dns.qry.type"]): 
                msg["dns.flags.rcode"] = 0
                msg["dns.flags.response"] = 1
                msg["dns.flags.authoritative"] = 1
                msg["dns.count.answers"] = 1
                msg["dns.resp.name"] = recordList[0]
                msg["dns.resp.type"] = recordList[1]
                msg["dns.%d"%msg["dns.qry.type"]] = recordList[3]
                 
                break
            
            else: recordList = []
            
        if(recordList == []):
            print("Leere Zeile")
            msg["dns.flags.rcode"] = 5
            msg["dns.flags.response"] = 0
            msg["dns.flags.authoritative"] = 0
            msg["dns.count.answers"] = 0
       
        msg = pack(msg)
        print(msg)
       
        sock.sendto(msg, (addr[0], addr[1]))
