class BaseSettings:
    epochs = 3
    num_users = 5
    client_frac = 0.5
    non_iid_frac = 0.95
    epochs_local = 3
    batch_size_local = 20
    batch_size = 32
    learning_rate = 1e-3
    momentum = 0.9
    weight_decay = 5e-4
    split = 'user'
    device = -1

    iid = False
    num_channels = 3
    num_classes = 10
    kernel_size = 5