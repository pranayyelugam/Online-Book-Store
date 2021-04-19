import os, time, sys
from flask import Flask
import requests
import threading

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
        count = 0

    def heartbeat(self):
        while True:
            for i,replica in enumerate(self.replicas):
                if replica.isReplicaAlive() == False:
                    print(replica.getUrl())
                    print("dead")
                    self.removeReplica(i)

            time.sleep(5)

    def getTargetReplicaUsingRoundRobin(self):
        ''' Gets a replica from the list of replicas using Round Robin '''
        if not self.replicas:
            return None
        targetReplica = self.replicas[self.count % len(self.replicas)]
        return targetReplica.getUrl

    def getLeastLoadedReplica(self):
        ''' Gets a replica from the list of replicas using Least Loaded '''
        if not self.replicas:
            return None
        minConnectionReplica = min((replica for replica in self.replicas if replica.alive == True), key=lambda r: r.connections)
        return minConnectionReplica
        
    def addReplica(self, host, port):
        ''' Adds the input replica to the list of replicas '''
        replica = Replica(host, port)
        if self.isReplicaPresentAlready(replica) == False:
            self.replicas.append(replica)

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
        targetReplica = self.getLeastLoadedReplica()
        targetUri = targetReplica.getUrl()
        url = targetUri + request
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
    

class CatalogLoadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Catalog"

    def addCatalogReplicas(self, catalogList):
        endpoints = catalogList.split('|')
        for x in endpoints:
            host,port = x.split(':')
            self.addReplica(host, port)        

class OrderloadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Order"

    def addOrderReplicas(self, orderList):
        endpoints = orderList.split('|')
        for x in endpoints:
            host,port = x.split(':')
            self.addReplica(host, port)


if __name__ == "__main__":

    # Create objects for catalog and order LBs
    catalogLoadBalancer = CatalogLoadBalanceManager()
    orderLoadBalancer = OrderloadBalanceManager()

    # Add details of hosts and ports to each of replicas
    catalogLoadBalancer.addCatalogReplicas("0.0.0.0:8080|0.0.0.0:8089")
    orderLoadBalancer.addOrderReplicas("0.0.0.0:8082|0.0.0.0:8087")

    # Start checking for the catalog replicas heartbeat
    catalogHeartbeatThread = threading.Thread(target = catalogLoadBalancer.heartbeat)
    catalogHeartbeatThread.start()

    # Start checking for the catalog replicas heartbeat
    orderHeartbeatThread = threading.Thread(target = orderLoadBalancer.heartbeat)
    orderHeartbeatThread.start()

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
        else: 
            return "Invalid Route"
        
    app.run(host='0.0.0.0', port=8085, debug=True)
        
