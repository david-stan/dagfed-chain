import json
import pathlib

from transaction import MainchainTransaction

class DAG:
    def __init__(self, data_address = './cache/server/pools/',
                       alpha = 3,
                       freshness = 60) -> None:
        self.data_address = data_address
        self.alpha = alpha
        self.freshness = freshness
        self.active_nodes_pool = dict()
        self.tip_nodes_pool = dict()

    def tx_publish(self, tx: MainchainTransaction) -> None:
        self.active_nodes_pool[tx.tx_name] = tx.timestamp
        self.tip_nodes_pool[tx.tx_name] = tx.timestamp
        if (len(tx.approved_tips) + self.alpha) < len(self.tip_nodes_pool):
            for tip in tx.approved_tips:
                self.tip_nodes_pool.pop(tip, None)
        with open(pathlib.Path(self.data_address) / 'active_pool.json', 'w') as f:
            json.dump(self.active_nodes_pool, f)
        with open(pathlib.Path(self.data_address) / 'tip_pool.json', 'w') as f:
            json.dump(self.tip_nodes_pool, f)

    def remove_genesis(self):
        self.tip_nodes_pool.pop('genesis', None)
        with open(pathlib.Path(self.data_address) / 'tip_pool.json', 'w') as f:
            json.dump(self.tip_nodes_pool, f)
