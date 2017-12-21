python3 collect_server/run_server.py &
python3 collect_server/run_listener.py &
python3 collect_client/run_client.py &
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8100
