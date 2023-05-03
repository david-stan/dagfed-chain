import os
import shutil
import pathlib

from dag_socket import client

import transaction

CACHE_DIR = "./cache/"
CLIENT_DATA_DIR = pathlib.Path(CACHE_DIR) / "client"
TX_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "txs"
TIPS_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "pools"

def main():
    if os.path.exists(CACHE_DIR) == False:
        os.mkdir(CACHE_DIR)

    if os.path.exists(CLIENT_DATA_DIR):
        shutil.rmtree(CLIENT_DATA_DIR)
    os.mkdir(CLIENT_DATA_DIR)

    if os.path.exists(TX_DATA_DIR):
        shutil.rmtree(TX_DATA_DIR)
    os.mkdir(TX_DATA_DIR)

    if os.path.exists(TIPS_DATA_DIR):
        shutil.rmtree(TIPS_DATA_DIR)
    os.mkdir(TIPS_DATA_DIR)

    client.require_tx_from_server("localhost", "genesis")
    client.require_tips_from_server("localhost")

    new_tx_01 = {"approved_tips": [], "model_accuracy": 34.0, "param_hash": "jyjtyjftyj", "shard_id": 1, "timestamp": 1683119166.5689557}
    new_tx_02 = {"approved_tips": [], "model_accuracy": 2.0, "param_hash": "asefasef", "shard_id": 0, "timestamp": 2345234525.5689557}

    new_tx_01 = transaction.MainchainTransaction(**new_tx_01)
    new_tx_02 = transaction.MainchainTransaction(**new_tx_02)

    client.upload_tx_to_server("localhost", new_tx_01)
    client.upload_tx_to_server("localhost", new_tx_02)

if __name__ == "__main__":
    main()