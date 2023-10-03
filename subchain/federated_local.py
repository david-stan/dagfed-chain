import os
import shutil
import sys
import json
import time
import torch
import copy
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.append('./ml')
sys.path.append('../')

from common.ipfs import ipfsAddFile
from common.ipfs import ipfsGetFile

from ml.utils.settings import BaseSettings
from ml.model_build import model_build
from ml.model_build import model_evaluate
from ml.models.FedAvg import FedAvg
from ml.models.train_model import LocalUpdate

import fabric_api

if __name__ == '__main__':

    if os.path.exists('./cache/local'):
        shutil.rmtree('./cache/local')
    os.mkdir('./cache/local')

    if os.path.exists('./cache/local/agg'):
        shutil.rmtree('./cache/local/agg')
    os.mkdir('./cache/local/agg')

    if os.path.exists('./cache/local/paras'):
        shutil.rmtree('./cache/local/paras')
    os.mkdir('./cache/local/paras')

    # build network
    net_glob, settings, dataset_train, dataset_test, dict_users = model_build(BaseSettings())
    net_glob.train()

    # with open('../commonComponent/dict_users.pkl', 'rb') as f:
    #     dict_users = pickle.load(f)

    checkTaskID = ''
    iteration = 0
    while 1:
        taskRelInfo = {}
        # taskRelease info template {"taskID":"task1994","epoch":10,"status":"start","usersFrac":0.1}
        while 1:
            taskRelQue, taskRelQueStt = fabric_api.query_release()
            if taskRelQueStt == 0:
                taskRelInfo = json.loads(taskRelQue)
                print('\n*************************************************************************************')
                print('Latest task release status is %s!'%taskRelQue.strip())
                break
        
        taskID = taskRelInfo['TaskID']
        totalEpochs = taskRelInfo['Epochs']

        print(f"Current task is {taskID}")

        taskInfo = {}
        while 1:
            taskInQue, taskInQueStt = fabric_api.query_task(taskID)
            if taskInQueStt == 0:
                taskInfo = json.loads(taskInQue)
                print('Latest task info is %s!'%taskInQue.strip())
                print('*************************************************************************************\n')
                break
        if taskInfo['TaskStatus'] == 'done' or checkTaskID == taskID:
            print('*** %s has been completed! ***\n'%taskID)
            time.sleep(5)
        else:
            print('\n******************************* Iteration #%d starting ********************************'%iteration+'\n')
            print('Iteration %d starting!'%iteration)
            print('\n*************************************************************************************\n')
            currentEpoch = int(taskInfo['TaskEpochs']) + 1
            loss_train = []
            acc_train = []
            while currentEpoch <= totalEpochs:
                
                while 1:
                    taskInQueEpoch, taskInQueEpochStt = fabric_api.query_task(taskID)
                    if taskInQueEpochStt == 0:
                        taskInfoEpoch = json.loads(taskInQueEpoch)
                        if int(taskInfoEpoch['TaskEpochs']) == (currentEpoch-1):
                            print('\n****************************** Latest status of %s ******************************'%taskID)
                            print('(In loop) Latest task info is \n %s!'%taskInQueEpoch)
                            print('*************************************************************************************\n')
                            break
                        else:
                            print('\n*************************** %s has not been updated ***************************'%taskID)
                            print('(In loop) Latest task info is \n %s!'%taskInQueEpoch)
                            print('*************************************************************************************\n')
                            time.sleep(10)
                # download aggregated model in current epoch from ipfs
                aggBaseModelFile = f"./cache/local/agg/aggModel-iter-{str(iteration)}-epoch-{str(currentEpoch-1)}.pkl"
                while 1:
                    aggBasMod, aggBasModStt = ipfsGetFile(taskInfoEpoch['ParamHash'], aggBaseModelFile)
                    if aggBasModStt == 0:
                        print('\nThe paras file of aggregated model for epoch %d training has been downloaded!\n'%(int(taskInfoEpoch['TaskEpochs'])+1))
                        break
                    else:
                        print('\nFailed to download the paras file of aggregated model for epoch %d training!\n'%(int(taskInfoEpoch['TaskEpochs'])+1))

                w_glob = net_glob.state_dict()
                net_glob.load_state_dict(torch.load(aggBaseModelFile))

                selectedDevices = [0, 1, 2, 3, 4]
                loss_locals = []
                acc_locals = []

                for idx_user in selectedDevices:
                    local = LocalUpdate(settings, dataset_train, dict_users[idx_user])
                    w_local, loss_local = local.train(net=copy.deepcopy(net_glob).to(settings.device), user=idx_user)
                    net_accuracy, _ = model_evaluate(net_glob, w_local, dataset_test, settings)
                    loss_locals.append(copy.deepcopy(loss_local))
                    acc_locals.append(copy.deepcopy(net_accuracy))
                    localParamFile = f"./cache/local/paras/{taskID}-{selectedDevices[idx_user]}-epoch-{str(currentEpoch)}.pkl"
                    torch.save(w_local, localParamFile)
                    while 1:
                        localParamHash, localAddStt = ipfsAddFile(localParamFile)
                        if localAddStt == 0:
                            print('%s has been added to the IPFS network!'%localParamFile)
                            print('And the hash value of this file is %s'%localParamHash)
                            break
                        else:
                            print('Failed to add %s to the IPFS network!'%localParamFile)

                    while 1:
                        localRelease = subprocess.Popen(args=[f"./hyperledger_invoke.sh local {selectedDevices[idx_user]} {taskID} {localParamHash} {str(currentEpoch)}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                        localOuts, localErrs = localRelease.communicate(timeout=10)
                        if localRelease.poll() == 0:
                            print('*** Local model train in epoch ' + str(currentEpoch) + ' of ' + str(selectedDevices[idx_user]) + ' has been uploaded! ***\n')
                            break
                        else:
                            print(localErrs.strip())
                            print('*** Failed to release Local model train in epoch ' + str(currentEpoch) + ' of ' + str(selectedDevices[idx_user]) + '! ***\n')
                            time.sleep(2)
                
                loss_avg = sum(loss_locals) / len(loss_locals)
                acc_avg = sum(acc_locals) / len(acc_locals)
                print('Epoch {:3d}, Average loss {:.3f}'.format(currentEpoch, loss_avg))
                print('Epoch {:3d}, Average acc {:.3f}'.format(currentEpoch, acc_avg))
                loss_train.append(loss_avg)
                acc_train.append(acc_avg)
                currentEpoch += 1

            checkTaskID = taskID
            # plt.figure()
            # plt.plot(range(len(loss_train)), loss_train, 'b')
            # plt.ylabel('Training Loss')
            # plt.xlabel('# of Global Epochs')
            # plt.title('Mini-Batch size = 20, Local Epochs = 5')
            # plt.savefig('./fed_loss.png')

            # plt.figure()
            # plt.plot(range(len(acc_train)), acc_train, 'g')
            # plt.ylabel('Testing Accuracy')
            # plt.xlabel('# of Global Epochs')
            # plt.title('Mini-Batch size = 20, Local Epochs = 5')
            # plt.savefig('./fed_acc.png')

            iteration += 1
