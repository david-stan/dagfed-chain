import json

from transaction import MainchainTransaction

class DAG:
    def __init__(self, active_nodes_pool_addr = './pools/active_pool.json',
                       tip_nodes_pool_addr = './pools/tip_pool.json',
                       alpha = 3,
                       freshness = 60) -> None:
        self.active_nodes_pool_addr = active_nodes_pool_addr
        self.tip_nodes_pool_addr = tip_nodes_pool_addr
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
        with open(self.active_nodes_pool_addr, 'w') as f:
            json.dump(self.active_nodes_pool, f)
        with open(self.tip_nodes_pool_addr, 'w') as f:
            json.dump(self.tip_nodes_pool, f)

    def remove_genesis(self):
        self.tip_nodes_pool.pop('genesis', None)
        with open(self.tip_nodes_pool_addr, 'w') as f:
            json.dump(self.tip_nodes_pool, f)
