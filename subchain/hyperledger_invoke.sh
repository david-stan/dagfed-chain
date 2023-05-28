#!/bin/bash

export FabricL=/home/david-stan/fabric/fabric-samples/test-network
export PATH=${FabricL}/../bin:$PATH
export FABRIC_CFG_PATH=$FabricL/../config/

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${FabricL}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${FabricL}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

setEnvironments() {
  ORG=$1
  if [ $ORG -eq 1 ]; then
    export CORE_PEER_TLS_ENABLED=true
    export CORE_PEER_LOCALMSPID="Org1MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=${FabricL}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
    export CORE_PEER_MSPCONFIGPATH=${FabricL}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
    export CORE_PEER_ADDRESS=localhost:7051                                                                       
  elif [ $ORG -eq 2 ]; then      
    export CORE_PEER_TLS_ENABLED=true                                                                                 
    export CORE_PEER_LOCALMSPID="Org2MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=${FabricL}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt 
    export CORE_PEER_MSPCONFIGPATH=${FabricL}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
    export CORE_PEER_ADDRESS=localhost:7051
  else  
    echo "================== ERROR !!! ORG Unknown =================="                                            
  fi
}

# Release the FL task from fabric
function taskRelease() {
  ORG=$1
  setEnvironments $ORG
  # query='{"function":"CreateTaskReleaseAsset","Args":['\"task_release\"','\"$2\"']}'
  invoke="peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${FabricL}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles "${FabricL}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${FabricL}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{\"function\":\"CreateTaskReleaseAsset\",\"Args\":[\"task_release\", \"5grfti\"]}'"
  # echo $invoke
  eval ${invoke}
}

function taskReleaseRemove() {
  ORG=$1
  setEnvironments $ORG
  invoke="peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${FabricL}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles "${FabricL}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${FabricL}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{\"function\":\"DeleteTaskReleaseAsset\",\"Args\":[\"task_release\"]}'"
  # echo $invoke
  eval ${invoke}
}

# Publish the global model file aggregated in current epoch
function publishAggModel() {
  ORG=$1
  setEnvironments $ORG
  invoke="docker exec cli peer chaincode invoke -o orderer.example.com:7050 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -C mychannel -n mycc -c '{\"Args\":[\"set\",\"${2}\",\"{\\\"epoch\\\":$3,\\\"status\\\":\\\"$4\\\",\\\"paras\\\":\\\"$5\\\"}\"]}'"
  eval ${invoke}
}

# Publish the local model file trained in current epoch
function publishLocalModel() {
  ORG=$1
  setEnvironments $ORG
  invoke="docker exec cli peer chaincode invoke -o orderer.example.com:7050 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -C mychannel -n mycc -c '{\"Args\":[\"set\",\"${2}\",\"{\\\"taskID\\\":\\\"$3\\\",\\\"epoch\\\":$4,\\\"paras\\\":\\\"${5}\\\"}\"]}'"
  eval ${invoke}
}

# Query the info from the chaincode
function queryRelease(){
  ORG=$1
  setEnvironments $ORG
  query="peer chaincode query -C mychannel -n basic -c '{\"Args\":[\"ReadTaskReleaseAsset\", \"task_release\"]}'"
  # echo $query
  eval ${query}
}

if [[ $# -lt 1 ]] ; then
  printHelp
  exit 0
else
  MODE=$1
  shift
fi

if [ "${MODE}" == "release" ]; then
  taskRelease 1 $1
  sleep 2
  queryRelease 1
elif [ "${MODE}" == "local" ]; then
  publishLocalModel 1 $1 $2 $3 $4
elif [ "${MODE}" == "aggregated" ]; then
  publishAggModel 1 $1 $2 $3 $4
  sleep 2
  query 1 $1
elif [ "${MODE}" == "query" ]; then
  query 1 $1
else
  printHelp
  exit 1
fi