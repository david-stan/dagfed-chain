import json
import pathlib

from dag_model.transaction import MainchainTransaction

class DAG:
    def __init__(self, data_address = './cache/server/pools/',
                       alpha = 3,
                       freshness = 60,
                       genesis_name = "genesis") -> None:
        self.data_address = data_address
        self.alpha = alpha
        self.freshness = freshness
        self.active_nodes_pool = dict()
        self.tip_nodes_pool = dict()
        self.genesis_name = genesis_name

    def tx_publish(self, tx: MainchainTransaction) -> None:
        if len(self.active_nodes_pool) == 0:
            self.genesis_name = tx.tx_name

        self.active_nodes_pool[tx.tx_name] = tx.timestamp
        self.tip_nodes_pool[tx.tx_name] = tx.timestamp
        
        if (len(tx.approved_tips) + self.alpha) < len(self.tip_nodes_pool):
            for tip in tx.approved_tips:
                self.tip_nodes_pool.pop(tip, None)
        if self.genesis_name in tx.approved_tips:
            self.tip_nodes_pool.pop(self.genesis_name, None)

        with open(pathlib.Path(self.data_address) / 'active_pool.json', 'w') as f:
            json.dump(self.active_nodes_pool, f)
        with open(pathlib.Path(self.data_address) / 'tip_pool.json', 'w') as f:
            json.dump(self.tip_nodes_pool, f)

    def remove_genesis(self):
        self.tip_nodes_pool.pop('genesis', None)
        with open(pathlib.Path(self.data_address) / 'tip_pool.json', 'w') as f:
            json.dump(self.tip_nodes_pool, f)
