import numpy as np

def cifar_iid(dataset, num_users):
    """
    Sample I.I.D. client data from CIFAR10 dataset
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

def mnist_iid(dataset, num_users):
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


def mnist_noniid(dataset, settings):
    """
    Sample non-I.I.D client data from MNIST dataset
    :param dataset:
    :param num_users:
    :return:
    """
    dataset_length = len(dataset)
    dataset_class_length = int(dataset_length / 10)
    data_user_mapping = {i: np.array([], dtype='int64') for i in range(settings.num_users)}
    idxs = np.arange(dataset_length)
    labels = np.array(dataset.targets)

    # sort labels
    idxs_labels = np.vstack((idxs, labels))
    idxs_labels = idxs_labels[:,idxs_labels[1,:].argsort()]
    idxs = idxs_labels[0,:]

    for user in range(settings.num_users):
        preffered_class = np.random.choice(np.arange(10), 1, replace=False).item()
        start = preffered_class * dataset_class_length
        pref_indexes = idxs_labels[0, np.arange(start, start + dataset_class_length)]
        pref_indexes_chosen = np.random.choice(
            pref_indexes,
            int(dataset_class_length * settings.non_iid_frac),
            replace=False
        )
        data_user_mapping[user] = np.concatenate((data_user_mapping[user], pref_indexes_chosen), axis=0)
        import copy
        idxs_labels_del = copy.deepcopy(idxs_labels)
        idxs_labels_del = np.delete(idxs_labels_del, slice(start, start + dataset_class_length), axis=1)
        non_preffered_class = np.random.choice(idxs_labels_del[0,:], int(dataset_class_length * (1 - settings.non_iid_frac)))
        data_user_mapping[user] = np.concatenate((data_user_mapping[user], non_preffered_class), axis=0)
        np.random.shuffle(data_user_mapping[user])

    return data_user_mapping