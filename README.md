# dagfed-chain
Multihierarchical sharded blockchain solution for federated learning

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
