
import socket
import json
import time as t


###### file management ##########

domain = "REC Resolver"

log = "rec_resolver.log"
try:
    x = open(log, "x")
    x.close()
except:
    print("Log already exists")

###### functions ################

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
    put_log("MSG SEND TO: " + str(ip) + ":" +str(port), message)
    if not (type(message) == dict):
        print("ERROR: NO DICTIONARY")
    
    msg = pack(message)
    t.sleep(0.1)
    sock.sendto(msg, (ip, port))

################################

    #connection details for recursive resolver
UDP_IP_SELF = "127.0.0.10"
UDP_PORT_SELF = 53053

    #connection details for root DNS Server
UDP_IP_ROOT = "127.0.0.11"
UDP_PORT = 53053

### start #######################

    #start server
put_log("SERVER STARTING")
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
sock.bind((UDP_IP_SELF, UDP_PORT_SELF))

put_log("SERVER LISTENING")
while True:
    data, addr = sock.recvfrom(1000)

        #if data received
    if data:
        msg = unpack(data)
        put_log("MSG RECV FROM: " + str(addr[0]) + ":" +str(addr[1]) , msg)
        
        ask_ip_addr = UDP_IP_ROOT
            # loop for requesting auth_servers for the domain as long as the auth_flag is set
        while True:
            t0 = timer()

            send(ask_ip_addr, UDP_PORT, msg)
                #min_wait time
            while (timer() - t0) < 1:
                data_a, addr_a = sock.recvfrom(2000)
                if data_a:
                    break

                # check if data is there
            if not data_a:
                print("ERROR1")
                exit(1)
                
                #check if ip adress is the expected one
            if not ask_ip_addr == addr_a[0]:
                print("Error2")
                exit(1)
            
                #filter message for needed information
            msg_a = unpack(data_a)
            put_log("MSG RECV FROM: " + str(addr[0]) + ":" +str(addr[1]) , msg_a)
            
                #return msg to client if needed record has been found or error generated
            if msg_a["dns.count.answers"] == 0:
                print("Error3")
                break
            if msg_a["dns.flags.authoritative"] == 1:
                break
            ask_ip_addr = msg_a["dns.ns"]
        
        send(addr[0], addr[1], msg_a)
            

