import torch
from torchvision import datasets, transforms

def get_dataset(type):
    if type == 'cifar':
        train_transform = transforms.Compose(
            [
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
            ]
        )
        test_transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
            ]
        )
        dataset_train = datasets.CIFAR10('../data/cifar10', train=True, download=True, transform=train_transform)
        dataset_test = datasets.CIFAR10('../data/cifar10', train=False, download=True, transform=test_transform)
        return dataset_train, dataset_test
    else:
        transform = transforms.Compose(
            [
                transforms.ToTensor(), 
                transforms.Normalize((0.1307,), (0.3081,)),
            ]
        )
        dataset_train = datasets.MNIST('../data/mnist', train=True, download=True, transform=transform)
        dataset_test = datasets.MNIST('../data/mnist', train=False, download=True, transform=transform)
        return dataset_train, dataset_test