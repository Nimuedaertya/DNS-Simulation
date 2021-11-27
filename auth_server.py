
#import ####################################

import sys
import socket
import json
import time as t

#init   ####################################

    #Check if record file was set as parameter for starting
if len(sys.argv) < 2:
    print("Add Record File to start")
    exit(1)

    # rec is filedescriptor for record file
rec = open(sys.argv[1],"r")
tmp = rec.readlines()
rec.close()

    #set UDP_IP based on record_file
records = tmp[0].split(",")
UDP_IP = records[3].replace("\n","")

    #set domain (namespace) based on record_file
domain = records[0]

    #global variable to keep track of if Server got requested record or is sending a NS record back
is_responsible_server_for_requested_record = True

    #create and open log file for this server
log = domain + ".log"
try:
    x = open(log,"x")
    x.close()
except:
    print("File Already there")

    #set Port
UDP_PORT = 53053

#functions ################################

    ################### LOG ############## 
    # prints time + name + msg to log
    # if a Message was received or send we add the content as second parameter
def put_log(msg, ls: dict = None):
   
    logg = open(log, "a")
    tmp = (time() + "A" + domain + "  "+ msg + "\n")
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

    #reads all entries in records_NAME file and puts them in record_list
def read_records():
    rec = open(sys.argv[1],"r")
    record_list = []
    data = rec.readlines()
    for zeile in data[1:]:
        record_list.append(zeile.replace("\n", "").split(","))
    return record_list

    #return the string, that should be in this record_list if exists
def suffix(dns_name) -> str:
    if not domain == ".":
        tmp = (dns_name[:-len(domain)].split("."))[-2] + "." + domain
        print(tmp)
        return tmp
    
    tmp = (dns_name[:-len(domain)].split("."))[-1]  +domain
    print(tmp)
    return tmp

    #finds the needed record of a domain name or return NS server that should know the answer
def find_record(dns_type, dns_name):

    global is_responsible_server_for_requested_record
    is_responsible_server_for_requested_record = True

        #checks if the exact requested record exists
        # structure:
        # 0      1      2     3       
        #Addr   Record TTL   IP/Addr for NS
    for record in record_list:
        if (record[0] == dns_name) and (record_types[record[1]] == dns_type):
            return record

        #find the server, that is responsible for this request (NS Server)
    name = suffix(dns_name)
    for i in record_list:
        if i[0] == name:
            if not (dns_name == name and dns_type == record_types[i[1]]):
                is_responsible_server_for_requested_record = False
            if (dns_name == name) and not (dns_type == 1):
                return i
            name = i[3]
            break

    for i in record_list:
        if i[0] == name:
            return i
    return None

    #returns a dictionary if no answer can be found for the request
def give_error(msg) -> dict:
    print("ERROR")
    msg["dns.flags.response"] = 1
    msg["dns.count.answers"] = 0
    msg["dns.flags.rcode"] = 5
    return msg


record_types = {"A": 1, "NS":2, "SOA": 6, "MX": 15}
def create_answer(msg) -> dict:
    
        #am I the right server for this request?
    if not msg["dns.qry.name"][(len(msg["dns.qry.name"]))-len(domain):] == domain:
        return give_error(msg)
    
        #find correct record if exists
    requested_record = find_record(msg["dns.qry.type"], msg["dns.qry.name"])
    
        #if correct record does not exist
    if requested_record == None:
        return give_error(msg)

    print(requested_record)

        #set message parameters
    msg["dns.flags.rcode"] = 0
    msg["dns.flags.response"] = 1

        #if is_NS is set this means, that this server is responsible for the needed record
        #if not, we send the IP of the NS Server which could know the answer back
    msg["dns.count.answers"] = 1
    msg["dns.resp.type"] = record_types[requested_record[1]]
    msg["dns.resp.ttl"] = requested_record[2]

        #if this server knows the IP for the requsted domain:
    if is_responsible_server_for_requested_record:
        msg["dns.flags.authoritative"] = 1
        msg["dns.resp.name"] = requested_record[0]
        msg["dns.a"] = requested_record[3]
    
    else:
        #if this server does not know the IP for the requested record, but knows which NS Server could help 
        msg["dns.flags.authoritative"] = 0
        msg["dns.resp.name"] = suffix(msg["dns.qry.name"])
        msg["dns.ns"] = requested_record[3]
    return msg

    #####################################



#start  ####################################

record_list = read_records()

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
        msg = unpack(data)
        put_log("MSG RECV FROM: " + str(addr[0]) + ":" +str(addr[1]) , msg)
        
        msg = create_answer(msg)
        
        put_log("MSG SEND TO: " + str(addr[0]) + ":" + str(addr[1]), msg)
        msg = pack(msg)
        t.sleep(2)
        sock.sendto(msg, addr)
