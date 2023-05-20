import torch
import copy
from torchvision import datasets, transforms

from models.Nets import CnnNet
from models.test_model import test
from utils.sampling import cifar_noniid
from utils.sampling import cifar_iid
from utils.settings import BaseSettings
from models.train_model import LocalUpdate

def model_build(settings):
    settings.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    trans_cifar = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    dataset_train = datasets.CIFAR10('../data/cifar', train=True, download=True, transform=trans_cifar)
    dataset_test = datasets.CIFAR10('../data/cifar', train=False, download=True, transform=trans_cifar)
    # sample dataset by individual user
    if settings.iid:
        data_user_mapping = cifar_iid(dataset_train, settings.num_users)
    else:
        data_user_mapping = cifar_noniid(dataset_train, settings.num_users)

    net = CnnNet(settings=settings).to(device=settings.device)
    
    return net, settings, dataset_train, dataset_test, data_user_mapping

def model_evaluate(net: torch.nn.Module, params, test_set, settings):
    net.load_state_dict(params)
    acc_test, loss_test = test(net, test_set, settings=settings)
    return acc_test, loss_test

if __name__ == '__main__':
    settings = BaseSettings()
    net, settings, train_dataset, test_dataset, data_user_mapping = model_build(settings)
    net_weights = net.state_dict()
    acc, loss = model_evaluate(net, net_weights, test_dataset, settings)
    print(acc, loss)
    # loss_locals = []
    local = LocalUpdate(settings=settings, dataset=train_dataset, idxs=data_user_mapping[34])
    w, loss = local.train(net=copy.deepcopy(net).to(settings.device))
    acc, loss = model_evaluate(net, w, test_dataset, settings)
    print(acc, loss)