# Dns

For starting DNS test:

1. run "bash start.sh" in dns directory
2. change directory to client in second console with "cd client/"
3. run python3 server_stub.py

Messaging Protocol:

# example message of client stub to auth_server/rec_server
msg = {"dns.flags.response": 0,
  "dns.flags.recdesired": 1,
  "dns.qry.name": "www.nawrocki.tns.",
  "dns.qry.type": 1
  }



# example of response message of auth_server to rec_resolver or client_stub
x = {
        "dns.flags.response": 0, #0 = ist keine Antwort; 1 = ist eine Antwort
        "dns.flags.recdesired":1,
        "dns.qry.name":2,
        "dns.qry.type":3,
        "dns.flags.rcode":4,
        "dns.count.answers":5,
        "dns.flags.authoritative":6,
        "dns.a":7,
        "dns.ns":8,
        "dns.resp.ttl":9
        }


DNS Record type information:
https://docs.google.com/document/d/1q2gzjt7D4LNAf4FEHRPRwA7XdVkzGpxrIhje4u7M4HQ/edit?usp=sharing



