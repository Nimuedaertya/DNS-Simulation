#!/bin/bash

cd auth_server/


rm ..log

python3 auth_server.py record_. &
python3 ../client/server_stub.py 

sleep 5

pkill -f auth_server

cat ..log


