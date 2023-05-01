import time
import json
import hashlib
import pathlib

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
        self.tx_name = f"shard_{self.shard_id}_{str(self.timestamp)}"

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


# tx fs storage functions


def tx_read(tx_file_path: pathlib.Path) -> MainchainTransaction:
    with open(tx_file_path, 'r') as f:
        object_params = json.load(f)
    return MainchainTransaction(**object_params)


def tx_save(tx: MainchainTransaction,
            tx_path_root: pathlib.Path
           ) -> None:
    tx_file_path = tx_path_root / f"{tx.tx_name}.json"
    try:
        with open(tx_file_path, 'w') as f:
            f.write(
                json.dumps(
                    tx.json_output(),
                    default=lambda obj: obj.__dict__,
                    sort_keys=True,
                )
            )
    except Exception as e:
        print(e)
