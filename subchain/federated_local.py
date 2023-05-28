import os
import shutil
import sys
import json

sys.path.append('./ml')
sys.path.append('../')

from ml.utils.settings import BaseSettings
from ml.model_build import model_build
from ml.model_build import model_evaluate
from ml.models.FedAvg import FedAvg

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
        break