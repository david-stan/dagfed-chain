import torch
from torch import nn
import torch.nn.functional as F

class MLP(nn.Module):
    def __init__(self, dim_in, dim_out, num_hidden) -> None:
        super(MLP, self).__init__()
        self.input_layer = nn.Linear(dim_in, num_hidden)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout()
        self.hidden_layer = nn.Linear(num_hidden, dim_out)

    def forward(self, x):
        x = x.view(-1, x.shape[-3] * x.shape[-2] * x.shape[-1])
        x = self.input_layer(x)
        x = self.dropout(x)
        x = self.relu(x)
        x = self.hidden_layer(x)
        return x