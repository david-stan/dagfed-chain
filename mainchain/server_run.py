import os
import shutil
import pathlib

import dag_model.transaction as transaction
from dag_model.dag import DAG
from  dag_socket import server

CACHE_DIR = "./cache/"
SERVER_DATA_DIR = pathlib.Path(CACHE_DIR) / "server"
TX_DATA_DIR = pathlib.Path(SERVER_DATA_DIR) / "txs"
DAG_DATA_DIR = pathlib.Path(SERVER_DATA_DIR) / "pools"

def main():
    if os.path.exists(CACHE_DIR) == False:
        os.mkdir(CACHE_DIR)

    if os.path.exists(SERVER_DATA_DIR):
        shutil.rmtree(SERVER_DATA_DIR)
    os.mkdir(SERVER_DATA_DIR)

    if os.path.exists(TX_DATA_DIR):
        shutil.rmtree(TX_DATA_DIR)
    os.mkdir(TX_DATA_DIR)

    if os.path.exists(DAG_DATA_DIR):
        shutil.rmtree(DAG_DATA_DIR)
    os.mkdir(DAG_DATA_DIR)

    server_dag = DAG()

    while True:
        server.create_server_socket(server_dag)


if __name__ == "__main__":
    main()