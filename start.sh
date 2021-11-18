#!/bin/bash

cd auth_server/

rm log_11
touch log_11

python3 auth_server.py &
python3 ../client/server_stub.py 

sleep 5

pkill -f auth_server


