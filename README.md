# dagfed-chain
Scalable multihierarchical sharded blockchain solution for federated learning

Blockchain platform consists of two layers:

* Mainchain layer - based on DAG (Tangle) consensus protocol, for maximum throughput [link](https://assets.ctfassets.net/r1dr6vzfxhev/4i3OM9JTleiE8M6Y04Ii28/d58bc5bb71cebe4adc18fadea1a79037/Tangle_White_Paper_v1.4.2.pdf)
* Subchain layer -  blockchain layer consisted of multiple sharded hyperledger fabric networks. Each shard does federated learning task (FedAvg) independently of other shards and uploads its global model to the mainchain

  

# Solution discussion

## Systems heterogeneity 

Be able to handle various client hardware, especially resource-constrained edge devices

* Find appropriate model architecture, fit for resource-constrained devices
  *  MobileViT (https://arxiv.org/pdf/2110.02178.pdf)
  *  MobileNet (https://arxiv.org/pdf/1704.04861.pdf)
  *  DeIT (https://arxiv.org/pdf/2012.12877.pdf)

* Find alternate algorithm for federated learning, other than FedAvg, that takes into account the systems heterogeneity - MetaFed(https://arxiv.org/pdf/2206.08516v3.pdf)

## Data heterogeneity

Be able to handle non-I.I.D. datasets, across all valid clients, in order not to lose generality

* Find appropriate model architecture that takes into account non-IID data - Transformer (https://arxiv.org/pdf/2106.06047.pdf)
* Find algorithm other than FedAvg, which takes into account unbalanced datasets - https://arxiv.org/pdf/2105.10056v2.pdf

## Privacy preservation

TODO
