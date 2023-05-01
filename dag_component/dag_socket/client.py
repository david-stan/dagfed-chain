import socket
import sys
import pathlib

def client_trans_require(aim_addr, tx_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((aim_addr, 65432))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024).decode())
    data = 'requireTx'.encode()
    s.send(data)
    response = s.recv(1024)
    print("Got response from server", response)
    data = tx_name.encode()
    s.send(data)
    rev_file(s, pathlib.Path('./cache/client/txs') / f"{tx_name}.json")
    print("do ovdje")
    s.close()

def rev_file(conn, tx_file_path):
    with open(tx_file_path, 'wb') as f:
        while 1:
            buff = conn.recv(1024)
            print("jjs", buff)
            if not buff:
                break
            print("dosao")
            f.write(buff)
            f.close()
            break
        

