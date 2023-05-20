class BaseSettings:
    epochs = 15
    num_users = 50
    client_frac = 0.1
    epochs_local = 15
    batch_size_local = 10
    batch_size = 32
    learning_rate = 0.001
    momentum = 0.9
    split = 'user'
    device = -1

    iid = True
    num_channels = 3
    num_classes = 10
    kernel_size = 5