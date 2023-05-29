import os
import shutil
import sys
import pathlib
import torch
import time
import uuid
import json
import random
import copy
import subprocess
import threading

import client
import fabric_api

sys.path.append('./ml')
sys.path.append('../')
# sys.path.append('../../commonComponent')

from ml.utils.settings import BaseSettings
from ml.model_build import model_build
from ml.model_build import model_evaluate
from ml.models.FedAvg import FedAvg

from common.ipfs import ipfsAddFile
from common.ipfs import ipfsGetFile



CACHE_DIR = "./cache/"
CLIENT_DATA_DIR = pathlib.Path(CACHE_DIR) / "client"
TX_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "txs"
TIPS_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "pools"
PARAMS_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "params"
LOCAL_DATA_DIR = pathlib.Path(CLIENT_DATA_DIR) / "local"

def main():
    
    if os.path.exists(CACHE_DIR) == False:
        os.mkdir(CACHE_DIR)

    if os.path.exists(CLIENT_DATA_DIR):
        shutil.rmtree(CLIENT_DATA_DIR)
    os.mkdir(CLIENT_DATA_DIR)

    if os.path.exists(TX_DATA_DIR):
        shutil.rmtree(TX_DATA_DIR)
    os.mkdir(TX_DATA_DIR)

    if os.path.exists(TIPS_DATA_DIR):
        shutil.rmtree(TIPS_DATA_DIR)
    os.mkdir(TIPS_DATA_DIR)

    if os.path.exists(PARAMS_DATA_DIR):
        shutil.rmtree(PARAMS_DATA_DIR)
    os.mkdir(PARAMS_DATA_DIR)

    if os.path.exists(LOCAL_DATA_DIR):
        shutil.rmtree(LOCAL_DATA_DIR)
    os.mkdir(LOCAL_DATA_DIR)

    ## setup

    alpha = 3

    # client.require_tx_from_server("localhost", "genesis")
    # client.require_tips_from_server("localhost")

    net, settings, _, test_dataset, data_user_mapping = model_build(BaseSettings())
    net_weight = net.state_dict()
    net_accuracy, _ = model_evaluate(net, net_weight, test_dataset, settings)

    genesisFile = './cache/client/genesis.pkl'
    torch.save(net_weight, genesisFile)

    while 1:
        genesisHash, statusCode = ipfsAddFile(genesisFile)
        if statusCode == 0:
            print('\nThe base mode parasfile ' + genesisFile + ' has been uploaded!')
            print('And the fileHash is ' + genesisHash + '\n')
            break
        else:
            print('Error: ' + genesisHash)
            print('\nFailed to upload the aggregated parasfile ' + genesisFile + ' !\n')

    genesisTxInfo = {"approved_tips": [], "model_accuracy": float(net_accuracy), "param_hash": genesisHash, "shard_id": 0, "timestamp": time.time()}
    client.upload_tx_to_server("localhost", genesisTxInfo)

    time.sleep(1)

    iteration = 0
    while 1:
        print(f"********************* Iteration {iteration} ***************************")

        taskID = str(uuid.uuid4())[:8]

        apv_tx_cands = []
        client.require_tips_from_server("localhost") 
        # implement promise later
        time.sleep(2)
        with open("./cache/client/pools/tip_pool.json", 'r') as f:
            tips_dict = json.load(f)
        
        if len(tips_dict) <= alpha:
            apv_tx_cands = list(tips_dict.keys())
        else:
            apv_tx_cands = random.sample(tips_dict.keys(), alpha)

        print(f"The candidates tips are {apv_tx_cands}")

        apv_tx_cands_dict = {}
        for apv_tx in apv_tx_cands:
            apv_tx_file = f"./cache/client/txs/{apv_tx}.json"
            client.require_tx_from_server("localhost", apv_tx)
            with open(apv_tx_file) as f:
                tx_info = json.load(f)

            print(tx_info)

            apv_tx_file = f"./cache/client/params/iter-{iteration}-{apv_tx}.pkl"

            while 1:
                status, code = ipfsGetFile(tx_info['param_hash'], apv_tx_file)
                print('The filehash of this approved trans is ' + tx_info['param_hash'] + ', and the file is ' + apv_tx_file + '!')
                if code == 0:
                    print(status.strip())
                    print('The apv parasfile ' + apv_tx_file + ' has been downloaded!\n')
                    break
                else:
                    print(status)
                    print('\nFailed to download the apv parasfile ' + apv_tx_file + ' !\n')
            apv_tx_cands_dict[apv_tx] = float(tx_info['model_accuracy'])

        apv_trans_final = []
        if len(apv_tx_cands_dict) == alpha:
            sort_dict = sorted(apv_tx_cands_dict.items(),key=lambda x:x[1],reverse=True)
            for i in range(alpha - 1):
                apv_trans_final.append(sort_dict[i][0])
        else:
            apv_trans_final = apv_tx_cands

        print(f"***************************************************")
        print(f"The candidates tips are {apv_tx_cands}")
        print(f"***************************************************")

        # aggregating approver parameters
        w_apv_agg = []
        for apv_tx in apv_trans_final:
            apv_param_file = f"./cache/client/params/iter-{iteration}-{apv_tx}.pkl"
            net.load_state_dict(torch.load(apv_param_file))
            w_tmp_iter = net.state_dict()
            w_apv_agg.append(copy.deepcopy(w_tmp_iter))
        
        if len(w_apv_agg) == 1:
            w_glob = w_apv_agg[0]
        else:
            w_glob = FedAvg(w_apv_agg)

        iteration_base_param_file = f"./cache/client/params/base-iter-{iteration}.pkl"
        torch.save(w_glob, iteration_base_param_file)

        base_model_acc, base_model_loss = model_evaluate(net, w_glob, test_dataset, settings)

        print(base_model_acc)

        while 1:
            basefileHash, baseSttCode = ipfsAddFile(iteration_base_param_file)
            if baseSttCode == 0:
                print('\nThe base mode parasfile ' + iteration_base_param_file + ' has been uploaded!')
                print('And the fileHash is ' + basefileHash + '\n')
                break
            else:
                print('Error: ' + basefileHash)
                print('\nFailed to uploaded the aggregated parasfile ' + iteration_base_param_file + ' !\n')

        taskEpochs = settings.epochs
        taskInitStatus = "start"

        ## initiate task release
        while 1:
            taskRelease = subprocess.Popen([f"./hyperledger_invoke.sh release {taskID} {taskEpochs}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            trOuts, trErrs = taskRelease.communicate(timeout=10)
            if taskRelease.poll() == 0:
                print('*** ' + taskID + ' has been released! ***')
                print('*** And the detail of this task is ' + trOuts.strip() + '! ***\n')
                break
            else:
                print(trErrs)
                print('*** Failed to release ' + taskID + ' ! ***\n')
                time.sleep(2)

        ## initiate task with base parameter hash
        while 1:
            spcAggModelPublish = subprocess.Popen(args=[f"./hyperledger_invoke.sh aggregated {taskID} 0 training {basefileHash}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            aggPubOuts, aggPubErrs = spcAggModelPublish.communicate(timeout=10)
            if spcAggModelPublish.poll() == 0:
                print('*** The init aggModel of ' + taskID + ' has been published! ***')
                print('*** And the detail of the init aggModel is ' + aggPubOuts.strip() + ' ! ***\n')
                break
            else:
                print(aggPubErrs)
                print('*** Failed to publish the init aggModel of ' + taskID + ' ! ***\n')
        
        # ## wait the local train
        time.sleep(10)
        selectedDevices = [0, 1, 2, 3, 4]
        currentEpoch = 1
        aggModelAcc = 50.0
        while (currentEpoch <= settings.epochs):
            flagList = set(copy.deepcopy(selectedDevices))
            w_locals = []
            while (len(flagList) != 0):
                flagSet = set()
                ts = []
                lock = threading.Lock()
                for deviceID in flagList:
                    localFileName = f"./cache/client/local/{taskID}-{deviceID}-epoch-{str(currentEpoch)}.pkl"
                    t = threading.Thread(target=fabric_api.query_local,args=(lock,taskID,deviceID,currentEpoch,flagSet,localFileName,))
                    t.start()
                    ts.append(t)
                for t in ts:
                    t.join()
                time.sleep(2)
                flagList = flagList - flagSet
            for deviceID in selectedDevices:
                localFileName = f"./cache/client/local/{taskID}-{deviceID}-epoch-{str(currentEpoch)}.pkl"
                
                ## check the acc of the models trained by selected device & drop the low quality model
                canddts_dev_pas = torch.load(localFileName,map_location=torch.device('cpu'))
                acc_canddts_dev, loss_canddts_dev = model_evaluate(net, canddts_dev_pas, test_dataset, settings)
                acc_canddts_dev = acc_canddts_dev.cpu().numpy().tolist()
                print("Test acc of the model trained by "+str(deviceID)+" is " + str(acc_canddts_dev))
                if (acc_canddts_dev - aggModelAcc) < -10:
                    print(str(deviceID)+" is a malicious device!")
                else:
                    w_locals.append(copy.deepcopy(canddts_dev_pas))

            w_glob = FedAvg(w_locals)
            aggEchoParasFile = './cache/client/params/aggModel-iter-'+str(iteration)+'-epoch-'+str(currentEpoch)+'.pkl'
            torch.save(w_glob, aggEchoParasFile)

            # evalute the acc of datatest
            aggModelAcc, aggModelLoss = model_evaluate(net, w_glob, test_dataset, settings)
            aggModelAcc = aggModelAcc.cpu().numpy().tolist()

            print("\n************************************")
            print("Acc of the agg model of Round "+str(currentEpoch)+" in iteration "+str(iteration)+" is "+str(aggModelAcc))
            print("************************************")

            while 1:
                aggEchoFileHash, sttCodeAdd = ipfsAddFile(aggEchoParasFile)
                if sttCodeAdd == 0:
                    print('\n*************************')
                    print('The aggregated parasfile ' + aggEchoParasFile + ' has been uploaded!')
                    print('And the fileHash is ' + aggEchoFileHash + '!')
                    print('*************************\n')
                    break
                else:
                    print('Error: ' + aggEchoFileHash)
                    print('\nFailed to uploaded the aggregated parasfile ' + aggEchoParasFile + ' !\n')

            taskStatus = 'training'
            if currentEpoch == settings.epochs:
                taskStatus = 'done'
            while 1:
                epochAggModelPublish = subprocess.Popen(args=[f"./hyperledger_invoke.sh aggregated {taskID} {str(currentEpoch)} {taskStatus} {aggEchoFileHash}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                aggPubOuts, aggPubErrs = epochAggModelPublish.communicate(timeout=10)
                if epochAggModelPublish.poll() == 0:
                    print('\n******************')
                    print('The info of task ' + taskID + ' is ' + aggPubOuts.strip())
                    print('The model aggregated in epoch ' + str(currentEpoch) + ' for ' + taskID + ' has been published!')
                    print('******************\n')
                    break
                else:
                    print(aggPubErrs)
                    print('*** Failed to publish the Model aggregated in epoch ' + str(currentEpoch) + ' for ' + taskID + ' ! ***\n')
            currentEpoch += 1

        new_tx = {"approved_tips": apv_trans_final, "model_accuracy": aggModelAcc, "param_hash": aggEchoFileHash, "shard_id": 1, "timestamp": time.time()}
        # upload the trans to DAG network
        client.upload_tx_to_server("localhost", new_tx)
        print('\n******************************* Transaction upload *******************************')
        print('The details of this trans are', new_tx)
        print('The trans generated in the iteration #%d had been uploaded!'%iteration)
        print('*************************************************************************************\n')
        iteration += 1
        time.sleep(2)
    # new_tx_01 = {"approved_tips": [], "model_accuracy": 34.0, "param_hash": "jyjtyjftyj", "shard_id": 1, "timestamp": 1683119166.5689557}
    # new_tx_02 = {"approved_tips": [], "model_accuracy": 2.0, "param_hash": "asefasef", "shard_id": 0, "timestamp": 2345234525.5689557}

    # new_tx_01 = MainchainTransaction(**new_tx_01)
    # new_tx_02 = MainchainTransaction(**new_tx_02)

    # client.upload_tx_to_server("localhost", new_tx_01)
    # client.upload_tx_to_server("localhost", new_tx_02)

if __name__ == "__main__":
    main()