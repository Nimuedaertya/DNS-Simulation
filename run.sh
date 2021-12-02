#!/bin/bash

pkill -f auth_server
#pkill -f rec_resolver

cd auth_server/

rm ./auth_server/*.log
rm ./auth_server/..log

python3 ../rec_resolver/rec_resolver.py &
python3 auth_server.py record_. &
python3 auth_server.py record_telematik. &
python3 auth_server.py record_fuberlin. &
python3 auth_server.py record_switch.telematik. &
python3 auth_server.py record_pcpools.fuberlin. &
python3 auth_server.py record_homework.fuberlin. &
python3 auth_server.py record_router.telematik. &
python3 ../client/server_stub.py

sleep 3

pkill -f auth_server
#pkill -f rec_resolver


