import time
import json
import hashlib

"""
Mainchain transaction as described in Fig. 5
Also referred as Mainchain Regular Block

tx_hash          - hash of the block (transation)
shard_id         - id of the node (shard) invoking the transaction
approved_tips    - approve tips set (list of rank)
timestamp        - timestamp of the block
model_accuracy   - accuracy of the aggregated model
param_hash       - hash of the parameters file

"""
class MainchainTransaction:
    def __init__(self,
                 param_hash,
                 timestamp = time.time(),
                 shard_id = 0,
                 approved_tips = [],
                 model_accuracy = 0.0,
                ) -> None:
        self.param_hash = param_hash
        self.timestamp = timestamp
        self.shard_id = shard_id
        self.approved_tips = approved_tips
        self.model_accuracy = model_accuracy
        self.tx_hash = self.hash()

    def hash(self):
        header = {
            'shard_id': self.shard_id,
            'approved_tips': self.approved_tips,
            'timestamp': self.timestamp,
        }

        data_to_hash = json.dumps(header,
                                  default=lambda obj: obj.__dict__,
                                  sort_keys=True)
        
        data_encoded = data_to_hash.encode()
        return hashlib.sha256(data_encoded).hexdigest()
    
    def json_output(self):
        return {
            'param_hash': self.param_hash,
            'timestamp': self.timestamp,
            'shard_id': self.shard_id,
            'approved_tips': self.approved_tips,
            'model_accuracy': self.model_accuracy,
        }
