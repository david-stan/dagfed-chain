import torch
import torchvision
import copy
from torchvision import datasets

from models.Nets import CnnNet
from models.test_model import test
from utils.sampling import cifar_noniid
from utils.sampling import cifar_iid
from utils.settings import BaseSettings
from models.train_model import LocalUpdate
from models.FedAvg import FedAvg

import os
import shutil

def model_build(settings):
    settings.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    train_transforms = torchvision.transforms.Compose(
        [
            torchvision.transforms.RandomCrop(32, padding=4),
            torchvision.transforms.RandomHorizontalFlip(),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
        ]
    )
    test_transforms = torchvision.transforms.Compose(
        [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
        ]
    )
    dataset_train = datasets.CIFAR10('../data/cifar10', train=True, download=True, transform=train_transforms)
    dataset_test = datasets.CIFAR10('../data/cifar10', train=False, download=True, transform=test_transforms)
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
    if os.path.exists('../data/local'):
        shutil.rmtree('../data/local')
    os.mkdir('../data/local')
    net, settings, train_dataset, test_dataset, data_user_mapping = model_build(settings)
    # sum(p.numel() for p in net.parameters() if p.requires_grad)
    users = [0, 1, 2, 3, 4]
    local_acc = []
    local_losses = []
    w_glob = net.state_dict()
    weightAggFile = f"../data/local/aggWeightIteration.pkl"
    torch.save(w_glob, weightAggFile)
    for e in range(settings.epochs):
        w_locals = []
        for user in users:
            net.load_state_dict(torch.load(weightAggFile))
            local = LocalUpdate(settings=settings, dataset=train_dataset, idxs=data_user_mapping[user])
            w, loss = local.train(net=copy.deepcopy(net).to(settings.device), user=user)
            acc, loss = model_evaluate(net, w, test_dataset, settings)
            local_acc.append(acc)
            local_losses.append(loss)
            weightLocalFile = f"../data/local/user-{user}--epoch-{e}.pkl"
            torch.save(w, weightLocalFile)
        for user in users:
            weightLocalFile = f"../data/local/user-{user}--epoch-{e}.pkl"
            w_local = torch.load(weightLocalFile)
            w_locals.append(w_local)
        w_glob = FedAvg(w_locals)
        torch.save(w_glob, weightAggFile)
        loss_avg = sum(local_losses) / len(local_losses)
        acc_avg = sum(local_acc) / len(local_acc)
        print('Epoch {:3d}, Average loss {:.3f}'.format(e, loss_avg))
        print('Epoch {:3d}, Average acc {:.3f}'.format(e, acc_avg))


    print(acc, loss)