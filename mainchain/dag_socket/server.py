import socket
import threading
import sys
import struct
import os
import json
import pathlib

from dag_model.dag import DAG
import dag_model.transaction as transaction

BUFFER_SIZE = 1024

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
        file_header = struct.pack('64si', os.path.basename(file_addr).encode(),
                                          os.stat(file_addr).st_size)
        conn.send(file_header) # send header
        conn.recv(BUFFER_SIZE) # header response
        with open(file_addr, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
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
            recv_data_file = conn.recv(BUFFER_SIZE).decode() # which tx is needed
            tx_file_addr = f"./cache/server/txs/{recv_data_file}.json"
            file_send(conn, tx_file_addr)
        elif msg == 'requireTips':
            tips_file_addr = "./cache/server/pools/tip_pool.json"
            file_send(conn, tips_file_addr)
        elif msg == 'uploadTx':
            conn.send('ok'.encode())
            recv_data = conn.recv(BUFFER_SIZE).decode()
            json_tx_data = json.loads(recv_data)
            new_tx = transaction.MainchainTransaction(**json_tx_data)
            transaction.tx_save(new_tx)
            dag_obj.tx_publish(new_tx)
            print(f"The new block {new_tx.tx_name} has been published!")

    conn.close()