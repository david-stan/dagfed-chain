import torch
from torchvision import datasets, transforms

from models.Nets import MLP
from models.test_model import test

def model_build():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    transform_cifar = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )
    train_set = datasets.CIFAR10('../data/cifar', train=True, download=True, transform=transform_cifar)
    test_set = datasets.CIFAR10('../data/cifar', train=False, download=True, transform=transform_cifar)

    img_dim = train_set[0][0].shape

    input_dim = img_dim[-3] * img_dim[-2] * img_dim[-1]

    main_net = MLP(dim_in=input_dim, dim_out=10, num_hidden=200).to(device=device)

    return main_net, train_set, test_set

def model_evaluate(net: torch.nn.Module, params, test_set):
    net.load_state_dict(params)
    acc_test, loss_test = test(net, test_set, batch_size=32)
    return acc_test, loss_test

# if __name__ == '__main__':
#     net, train_dataset, test_dataset = model_build()
#     net_weights = net.state_dict()
#     acc, loss = model_evaluate(net, net_weights, test_dataset)
#     print(acc, loss)