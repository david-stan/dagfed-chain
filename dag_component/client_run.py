import os
import shutil
import pathlib

from dag_socket import client

CACHE_DIR = "./cache/"
CLIENT_DATA_DIR = pathlib.Path(CACHE_DIR) / "client"
TX_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "txs"

def main():
    if os.path.exists(CACHE_DIR) == False:
        os.mkdir(CACHE_DIR)

    if os.path.exists(CLIENT_DATA_DIR):
        shutil.rmtree(CLIENT_DATA_DIR)
    os.mkdir(CLIENT_DATA_DIR)

    if os.path.exists(TX_DATA_DIR):
        shutil.rmtree(TX_DATA_DIR)
    os.mkdir(TX_DATA_DIR)

    client.client_trans_require("localhost", "genesis")

if __name__ == "__main__":
    main()