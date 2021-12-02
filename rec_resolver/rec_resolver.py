
import socket
import json
import time as t
import datetime
import random

###### file management ##########

domain = "REC Resolver"

log = "rec_resolver.log"
try:
    x = open(log, "x")
    x.close()
except:
    print("Log already exists")

cache = dict()

###### functions ################

    ################### LOG ############## 
    
    # prints time + name + msg to log
    # if a Message was received or send we add the content as second parameter
def put_log(msg, ls: dict = None):

    logg = open(log, "a")
    tmp = (time() + " A " + domain + "  "+ msg + "\n")
    logg.write(tmp)
    if ls:
        for i in ls:
            tmp = (" "*5 + str(i) +": " + str(ls[i]) + "\n")
            logg.write(tmp)

    #returns timestamp for log file
def time():
    #a = t.localtime()
    #dateTime = f'{a.tm_year}-{a.tm_mon}-{a.tm_mday}'
    #clockTime = f'{a.tm_hour}:{a.tm_min}:{a.tm_sec}'
    #timestamp = f'{dateTime} {clockTime} '
    #return timestamp
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    ########### PACK / UNPACKING MSG ####

    #transforms dictionary into binary string for UDP connection
def pack(msg: dict) -> str:
    return json.dumps(msg).encode()


    #transforms binary string into dictionary
def unpack(msg: str) -> dict:
    return json.loads(msg.decode('utf-8'))

    ########## DELAY ####################    

def timer():
    return t.clock_gettime(t.CLOCK_THREAD_CPUTIME_ID)


    ########## Send MSG #################

def send(ip, port, message):
    put_log(f'MSG SEND TO: {ip}:{port}', message)
    if not (type(message) == dict):
        print("ERROR: NO DICTIONARY")
    
    msg = pack(message)
    #t.sleep(0.1)
    sock.sendto(msg, (ip, port))
def send_with_delay(delay,ip,port,message):
    sleeping_time=(random.randint(delay, delay*10))/1000 
    put_log(f'SENDING DELAY FOR RESOLVER IS ABOUT {sleeping_time} milliseconds')
    t.sleep(sleeping_time)
    send(ip, port, message)

################################

    #connection details for recursive resolver
UDP_IP_SELF = "127.0.0.10"
UDP_PORT_SELF = 53053

    #connection details for root DNS Server
UDP_IP_ROOT = "127.0.0.11"
UDP_PORT = 53053

### start #######################


def start_server():
    try : 
        sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
        sock.bind((UDP_IP_SELF, UDP_PORT_SELF))
        put_log("SERVER STARTING")
        return sock
    except:
        pass
    


def server_start_listening(sock):
    put_log("SERVER LISTENING")
    while True:
        data, addr = sock.recvfrom(1000)
        client_ip = addr[0]
        client_port = addr[1]
            
        if data:                #if data received
            msg = unpack(data)
            put_log(f"MSG RECV FROM: {client_ip}:{client_port}", msg)
            
            if dnsLookup(msg["dns.qry.name"]):
                send_with_delay(100, client_ip, client_port, cache[msg["dns.qry.name"]][0])
            else:
                msg_a, timestamp = resolve_dns(UDP_IP_ROOT, msg)
                updateDnsEntry(msg_a, timestamp)
                send_with_delay(100, client_ip, client_port, msg_a)


def dnsLookup(dns: str) -> str:
    value = None

    if dns in cache:
        msg, timestamp = cache[dns]
        ttl = msg["dns.resp.ttl"]

        if datetime.datetime.now() < timestamp + datetime.timedelta(seconds=int(ttl)):
            put_log('Cache hit')
            value = msg

    return value


def updateDnsEntry(recieved_msg, timestamp):
    cache[recieved_msg["dns.qry.name"]] = (recieved_msg, timestamp)


def resolve_dns(ask_ip_addr, msg):
    data_arriving_timestamp = None
    responsed_msg = None
    while True:
            start_time = datetime.datetime.now()#timer()
            #print(f'Start time: {timer()} + Datetime: {datetime.datetime.now()}')
            send_with_delay(100, ask_ip_addr, UDP_PORT, msg)
                #min_wait time ???
            #while (timer() - start_time) < 1:
            while (datetime.datetime.now() - start_time) < datetime.timedelta(seconds=1):
                #print(f'Current time: {timer()} + Datetime: {datetime.datetime.now()}')
                data_a, addr_a = sock.recvfrom(2000)
                server_ip, server_port = addr_a[0], addr_a[1]
                if data_a:
                    data_arriving_timestamp = datetime.datetime.now()
                    break

                # check if data is there
            if not data_a:
                print("ERROR1")
                #exit(1)
                
                #check if ip adress is the expected one
            if not ask_ip_addr == addr_a[0]:
                print("Error2")
                #exit(1)
            
                #filter message for needed information
            responsed_msg = unpack(data_a)
            put_log(f"MSG RECV FROM: {server_ip}:{server_port}", responsed_msg)
            
                #return msg to client if needed record has been found or error generated
            if responsed_msg["dns.count.answers"] == 0:
                print("Error3")
                break
            if responsed_msg["dns.flags.authoritative"] == 1:
                break
            ask_ip_addr = responsed_msg["dns.ns"]

    return (responsed_msg, data_arriving_timestamp)


try:
    sock = start_server()
    server_start_listening(sock)
except:
    pass