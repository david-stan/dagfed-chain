import subprocess
import json
import sys
import time

sys.path.append('../')

from common.ipfs import ipfsGetFile

def queryLocal(lock, taskID, deviceID, currentEpoch, flagSet, localFileName):
    """
    Query and download the paras file of local model trained by the device.
    """
    localQuery = subprocess.Popen(args=['../commonComponent/interRun.sh query '+deviceID], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    outs, errs = localQuery.communicate(timeout=15)
    if localQuery.poll() == 0:
        localDetail = json.loads(outs.strip())
        if localDetail['epoch'] == currentEpoch and localDetail['taskID'] == taskID:
            print("The query result of the " + deviceID + " is ", outs.strip())
            while 1:
                # localFileName = './clientS/paras/' + taskID + '-' + deviceID + '-epoch-' + str(currentEpoch) + '.pkl'
                outs, stt = ipfsGetFile(localDetail['paras'], localFileName)
                if stt == 0:
                    break
                # else:
                #     print(outs.strip())
            lock.acquire()
            t1 = flagSet
            t1.add(deviceID)
            flagSet = t1
            lock.release()
        # else:
        #     print('*** This device %s has not updated its model! ***'%(deviceID))
    # else:
    #     print("Failed to query this device!", errs)

def simpleQuery(key):
    """
    Use the only key to query info from fabric network.
    """
    infoQuery = subprocess.Popen(args=["./hyperledger_invoke.sh query " + key], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    outs, errs = infoQuery.communicate(timeout=15)
    if infoQuery.poll() == 0:
        return outs.strip(), infoQuery.poll()
    else:
        print("*** Failed to query the info of " + str(key) + "! ***" + errs.strip())
        return errs.strip(), infoQuery.poll()
    
def query_release():
    """
    Use the only key to query info from fabric network.
    """
    infoQuery = subprocess.Popen(args=["./hyperledger_invoke.sh query_release"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    outs, errs = infoQuery.communicate(timeout=15)
    if infoQuery.poll() == 0:
        return outs.strip(), infoQuery.poll()
    else:
        print("*** Failed to query the info of query_release! ***" + errs.strip())
        time.sleep(2)
        return errs.strip(), infoQuery.poll()
    
def query_task(taskID):
    """
    Use the only key to query info from fabric network.
    """
    infoQuery = subprocess.Popen(args=[f"./hyperledger_invoke.sh query_task {taskID}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    outs, errs = infoQuery.communicate(timeout=15)
    if infoQuery.poll() == 0:
        return outs.strip(), infoQuery.poll()
    else:
        print("*** Failed to query the info of " + taskID + "! ***" + errs.strip())
        time.sleep(2)
        return errs.strip(), infoQuery.poll()