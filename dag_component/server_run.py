import os
import shutil
import pathlib

import transaction
from dag import DAG
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

    genesis_info = "QmaBYCmzPQ2emuXpVykLDHra7t8tPiU8reFMkbHpN1rRoo"
    genesis_block = transaction.MainchainTransaction(genesis_info)
    genesis_block.tx_name = 'genesis'
    transaction.tx_save(genesis_block)

    server_dag.tx_publish(genesis_block)
    server_dag.remove_genesis()

    while True:
        server.create_server_socket(server_dag)


if __name__ == "__main__":
    main()