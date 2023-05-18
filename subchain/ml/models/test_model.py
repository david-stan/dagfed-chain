import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

def test(net: nn.Module, data, batch_size):
    net.eval()
    test_loss = 0
    correct = 0
    loader = DataLoader(dataset=data, batch_size=batch_size)
    for _, (data, target) in enumerate(loader):
        data, target = data.cuda(), target.cuda()
        logits = net(data)
        test_loss += F.cross_entropy(logits, target=target, reduction='sum').item()
        y_pred = logits.data.max(1, keepdim=True)[1]
        correct += y_pred.eq(target.data.view_as(y_pred)).long().cpu().sum()

    test_loss /= len(loader.dataset)
    accuracy = 100.00 * correct / len(loader.dataset)
    print('\nTest set: Average loss: {:.4f} \nAccuracy: {}/{} ({:.2f}%)\n'.format(
            test_loss, correct, len(loader.dataset), accuracy))
    return accuracy, test_loss