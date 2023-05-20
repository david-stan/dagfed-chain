import numpy as np

def cifar_iid(dataset, num_users):
    """
    Sample I.I.D. client data from MNIST dataset
    :param dataset:
    :param num_users:
    :return: dict of image index
    """
    num_items = int(len(dataset)/num_users)
    data_user_mapping, all_idxs = {}, [i for i in range(len(dataset))]
    for i in range(num_users):
        data_user_mapping[i] = set(np.random.choice(all_idxs, num_items, replace=False))
        all_idxs = list(set(all_idxs) - data_user_mapping[i])
    return data_user_mapping


def cifar_noniid(dataset, num_users):
    """
    Sample non-I.I.D client data from MNIST dataset
    :param dataset:
    :param num_users:
    :return:
    """
    num_shards, num_imgs = 100, 500
    idx_shard = [i for i in range(num_shards)]
    data_user_mapping = {i: np.array([], dtype='int64') for i in range(num_users)}
    idxs = np.arange(num_shards*num_imgs)
    labels = np.array(dataset.targets)

    # sort labels
    idxs_labels = np.vstack((idxs, labels))
    print(idxs_labels)
    idxs_labels = idxs_labels[:,idxs_labels[1,:].argsort()]
    idxs = idxs_labels[0,:]

    # divide and assign
    for i in range(num_users):
        rand_set = set(np.random.choice(idx_shard, 2, replace=False))
        idx_shard = list(set(idx_shard) - rand_set)
        for rand in rand_set:
            data_user_mapping[i] = np.concatenate((data_user_mapping[i], idxs[rand*num_imgs:(rand+1)*num_imgs]), axis=0)

    return data_user_mapping
