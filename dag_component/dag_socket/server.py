import socket
import threading
import sys
import os

from dag import DAG

def create_server_socket(dag_obj, num_shards = 5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", 65432))
        s.listen(num_shards)
        print("DAG server created, awaiting connections...")
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_conn, args=(conn, addr, dag_obj))
        t.start()

def file_send(conn: socket, file_addr):
    try:
        with open(file_addr, 'rb') as f:
            while True:
                data = f.read(1024)
                print(data)
                if not data:
                    break
                conn.send(data)
    except Exception as e:
        print(e)

def handle_conn(conn: socket, addr, dag_obj: DAG):
    print(f"Accept new connection from {addr}")
    conn.send((f"Connection accepted on server.").encode())
    while 1:
        msg = conn.recv(1024).decode()
        if msg == 'requireTx':
            conn.send('ok'.encode())
            recv_data = conn.recv(1024).decode()
            tx_file_addr = f"./cache/server/txs/{recv_data}.json"
            file_send(conn, tx_file_addr)
    conn.close()