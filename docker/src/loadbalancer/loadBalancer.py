import os, time, sys
from flask import Flask
import requests
import threading
import subprocess

app = Flask(__name__)

class Replica:
    def __init__(self, host, port, path='/'):
        self.host = host
        self.port = port
        self.path = path
        self.connections = 0
        self.serverTimeout = 5
        self.alive = True
        self.protocol = "http://"

    def isReplicaAlive(self):
        ''' Checks if the replica is alive or not by sending a request'''
        try:
            res = requests.get(self.getUrl()+self.path, timeout = self.serverTimeout)
            if res.status_code == 200:
                self.alive =  True
            else:
                self.alive =  False
        except Exception as E:
            self.alive =  False
        return self.alive
    
    def getUrl(self):
        ''' Constructs a Url from the input host and port'''
        return self.protocol + self.host+ ":" + self.port


class LoadBalancer:
    def __init__(self):
        self.replicas = []
        self.count = 0
        self.lbType =""

    def heartbeat(self):
        while True:
            for i,replica in enumerate(self.replicas):
                if replica.isReplicaAlive() == False:
                    self.removeReplica(i)

            time.sleep(5)

    def getTargetReplicaUsingRoundRobin(self):
        ## TODO ## catalog requests are not being load balanced
        ''' Gets a replica from the list of replicas using Round Robin '''
        if not self.replicas:
            return None
        targetReplica = self.replicas[self.count % len(self.replicas)]
        print(str(self.count) + " " + self.lbType )
        self.count += 1
        return targetReplica

    def getLeastLoadedReplica(self):
        ''' Gets a replica from the list of replicas using Least Loaded '''
        if not self.replicas:
            return None
        minConnectionReplica = min((replica for replica in self.replicas if replica.alive == True), key=lambda r: r.connections)
        return minConnectionReplica
        
    def registerReplica(self, host, port):
        ''' Adds the input replica to the list of replicas '''
        replica = Replica(host, port)
        if self.isReplicaPresentAlready(replica) == False:
            for x in self.replicas:
                print(x.getUrl())
            self.replicas.append(replica)
            return "True"
        return "False"

    def removeReplica(self, replica):
        ''' Removes the replica from the list of replicas as the replica is down'''
        if replica in self.replicas:
            del self.replicas[replica]

    def isReplicaPresentAlready(self, replica):
        ''' Check if the input replica is already in the list of replicas'''
        for r in self.replicas:
            if r.getUrl == replica.getUrl:
                return True
        return False
    
    def processRequest(self, request):
        targetReplica = self.getTargetReplicaUsingRoundRobin()
        targetUri = targetReplica.getUrl()
        url = targetUri + request
        print(url)
        try:
            targetReplica.connections += 1
            res =  requests.get(url)
            targetReplica.connections -= 1
        except Exception as E:
            print("Retrying...")
            targetReplica.connections += 1
            res =  requests.get(url)
            targetReplica.connections -= 1
        return res.content

    def resync(endpoint, targetEndpoint, path='/resync'):
        while True:
            resp = requests.get(endpoint + path + '/' + targetEndpoint)
            if resp.status_code == 200:
                break
    

class CatalogLoadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Catalog"
        ## TODO ## 
        # Add the files in the sh files
        self.spawnCommand = "python ../catalog-server-B/catalog.py http://0.0.0.0:8081"

    def registerCatalogReplicas(self, request):
        host,port = request.split(':')
        return self.registerReplica(host, port)


    def spawnReplicas(self):
        while True:
            aliveServerToSync = None
            for i,replica in enumerate(self.replicas):
                if replica.alive == False:
                    print("server dead")
                    # Spawn the server
                    subprocess.call([str(self.spawnCommand)], shell=True)
                    # Wait for the server to come alive
                    time.sleep(10)
                    # Check if the server is active
                    if replica.alive == True:
                        # Sync with the alive db
                        super().resync(replica.getUrl(), aliveServerToSync.getUrl())
                    time.sleep(5)
                else:
                    aliveServerToSync = replica
   

class OrderloadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Order"

    def registerOrdereplicas(self, request):
        host,port = request.split(':')
        return self.registerReplica(host, port)

    def spawnReplicas(self):
        while True:
            for i,replica in enumerate(self.replicas):
                if replica.alive == False:
                    print("server dead")
                    time.sleep(5)



if __name__ == "__main__":

    # Create objects for catalog and order LBs
    catalogLoadBalancer = CatalogLoadBalanceManager()
    orderLoadBalancer = OrderloadBalanceManager()


    '''    
    ----   TODO Threads to sync and update dbs ------ 

    # Start checking for the catalog replicas heartbeat
    catalogHeartbeatThread = threading.Thread(target = catalogLoadBalancer.heartbeat)
    catalogHeartbeatThread.start()

    # Start checking for the catalog replicas heartbeat
    orderHeartbeatThread = threading.Thread(target = orderLoadBalancer.heartbeat)
    orderHeartbeatThread.start()

    orderReplicaSpawnThread = threading.Thread(target = catalogLoadBalancer.spawnReplicas)
    orderReplicaSpawnThread.start()

    catalogReplicaSpawnThread = threading.Thread(target = catalogLoadBalancer.spawnReplicas)
    catalogReplicaSpawnThread.start()

    '''

    @app.route('/')
    def alive():
        return "alive"

    @app.route('/<request>')
    def loadBalancer(request):
        requestType = str(request).split('@')[1]
        request = request.replace('@', '/')
        if requestType in ['query','reduceStock', 'updateStock', 'updateCost']:
           return catalogLoadBalancer.processRequest(request)
        elif requestType in ['buy']:
            return orderLoadBalancer.processRequest(request)
        # Add details of hosts and ports to each of replicas
        elif requestType in ['register_catalog']:
            replicaUrl = str(request).split('/')[2]
            return catalogLoadBalancer.registerCatalogReplicas(replicaUrl)
        elif requestType in ['register_order']:
            replicaUrl = str(request).split('/')[2]
            return orderLoadBalancer.registerOrdereplicas(replicaUrl)
        else: 
            return "Invalid Route"
        
    app.run(host='0.0.0.0', port=8080)
        
