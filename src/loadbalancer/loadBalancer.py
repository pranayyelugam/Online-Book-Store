import os, time, sys, json
from flask import Flask
import requests
import threading
import subprocess

app = Flask(__name__)
scriptDir = os.path.dirname(__file__)
runType = None
log = os.path.join(scriptDir, './loadBalancerLog.txt')

class Replica:
    def __init__(self, host, port, path="/"):
        self.host = host
        self.port = port
        self.path = path
        self.connections = 0
        self.serverTimeout = 5
        self.alive = True
        self.protocol = "http://"

    def isReplicaAlive(self):
        """ Checks if the replica is alive or not by sending a request"""
        try:
            res = requests.get(self.getUrl() + self.path, timeout=self.serverTimeout)
            if res.status_code == 200:
                self.alive = True
            else:
                self.alive = False
        except Exception as E:
            self.alive = False
        return self.alive

    def getUrl(self):
        """ Constructs a Url from the input host and port"""
        return self.protocol + self.host + ":" + self.port


class LoadBalancer:
    def __init__(self):
        self.replicas = []
        self.count = 0
        self.lbType = ""
        data_path = os.path.join(scriptDir, './spawning.json')
        f = open(data_path)
        self.json_data = json.load(f)[runType]
        self.lock = threading.Lock()
        self.logLock = threading.Lock()

    def getTargetReplicaUsingRoundRobin(self):
        ## TODO ## catalog requests are not being load balanced
        """ Gets a replica from the list of replicas using Round Robin """
        if not self.replicas:
            return None
        targetReplica = self.replicas[self.count % len(self.replicas)]
        self.count += 1
        return targetReplica

    def getLeastLoadedReplica(self):
        """ Gets a replica from the list of replicas using Least Loaded """
        if not self.replicas:
            return None
        minConnectionReplica = min(
            (replica for replica in self.replicas if replica.alive == True),
            key=lambda r: r.connections,
        )
        return minConnectionReplica

    def registerReplica(self, host, port):
        """ Adds the input replica to the list of replicas """
        replica = Replica(host, port)
        if self.isReplicaPresentAlready(replica) == False:
            self.replicas.append(replica)
            return "True"
        return "False"

    def removeReplica(self, replica, index):
        """ Removes the replica from the list of replicas as the replica is down"""
        if replica in self.replicas:
            with self.lock:
                del self.replicas[index]

    def isReplicaPresentAlready(self, replica):
        """ Check if the input replica is already in the list of replicas"""
        for r in self.replicas:
            if r.getUrl == replica.getUrl:
                return True
        return False

    def processRequest(self, request):
        with self.lock:
            targetReplica = self.getTargetReplicaUsingRoundRobin()
            targetUri = targetReplica.getUrl()
            url = targetUri + request
            try:
                targetReplica.connections += 1
                res = requests.get(url, timeout=5)
                targetReplica.connections -= 1
                if res.status_code != 200:
                    targetReplica = self.getTargetReplicaUsingRoundRobin()
                    targetUri = targetReplica.getUrl()
                    url = targetUri + request
                    targetReplica.connections += 1
                    res = requests.get(url)
                    targetReplica.connections -= 1
            except Exception as E:
                targetReplica = self.getTargetReplicaUsingRoundRobin()
                targetUri = targetReplica.getUrl()
                url = targetUri + request
                with self.logLock:
                    file = open(log, "a+")
                    file.write("Retrying...")
                    file.write("{}\n".format(E))
                    file.close()
                print("Retrying...")
                targetReplica.connections += 1
                res = requests.get(url)
                targetReplica.connections -= 1
        return res.content

    def resync(self, endpoint, host, port, path="/resync"):
        print(endpoint + path + "/" + host + ":" + port)
        resp = requests.get(endpoint + path + "/" + host + ":" + port)

    def spawnReplicas(self):
        aliveServerToSync = None
        while True:
            for i, r in enumerate(self.replicas):
                if r.isReplicaAlive() == False:
                    print("server dead")
                    # Get the port of the dead replica
                    deadServerPort = r.port
                    # Remove server from the list of replicas
                    self.removeReplica(r, i)
                    # Spawn the server
                    spawnCommand = self.json_data[deadServerPort]
                    with self.logLock:
                        file = open(log, "a+")
                        file.write("{}\n".format(spawnCommand))
                        file.close()
                    time.sleep(1)
                    try:
                        subprocess.Popen([str(spawnCommand)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    except Exception as E:
                        with self.logLock:
                            file = open(log, "a+")
                            file.write("{}\n".format(E))
                            file.close()
                        print(E)                    
                    # If server type is catalog, then sync the db between the replicas
                    if self.lbType == "Catalog":
                        # Wait for the server to come alive
                        time.sleep(5)
                        # Check if the server is active
                        if r.isReplicaAlive() == True:
                            # Sync with the alive db
                            self.resync(r.getUrl(), aliveServerToSync.host, aliveServerToSync.port)
                else:
                    aliveServerToSync = r
            time.sleep(2)

class CatalogLoadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Catalog"

    def registerCatalogReplicas(self, request):
        host, port = request.split(":")
        return self.registerReplica(host, port)


class OrderloadBalanceManager(LoadBalancer):
    def __init__(self):
        super().__init__()
        self.lbType = "Order"

    def registerOrdereplicas(self, request):
        host, port = request.split(":")
        return self.registerReplica(host, port)


if __name__ == "__main__":

    configPath = os.path.join(scriptDir, './spawnConfig.txt')
    f = open(configPath)
    runType = f.readline()


    # Create objects for catalog and order LBs
    catalogLoadBalancer = CatalogLoadBalanceManager()
    orderLoadBalancer = OrderloadBalanceManager()
    
    # Threads to check if the servers are alive and respawn if they are dead.
    orderReplicaSpawnThread = threading.Thread(target = orderLoadBalancer.spawnReplicas)
    orderReplicaSpawnThread.start()

    catalogReplicaSpawnThread = threading.Thread(target = catalogLoadBalancer.spawnReplicas)
    catalogReplicaSpawnThread.start()

    # index route
    @app.route("/")
    def alive():
        return "alive"

    # main request route
    @app.route("/<request>")
    def loadBalancer(request):
        requestType = str(request).split("@")[1]
        request = request.replace("@", "/")
        if requestType in ["query", "reduceStock", "updateStock", "updateCost"]:
            return catalogLoadBalancer.processRequest(request)
        elif requestType in ["buy"]:
            return orderLoadBalancer.processRequest(request)
        # Add details of hosts and ports to each of replicas
        elif requestType in ["register_catalog"]:
            replicaUrl = str(request).split("/")[2]
            return catalogLoadBalancer.registerCatalogReplicas(replicaUrl)
        elif requestType in ["register_order"]:
            replicaUrl = str(request).split("/")[2]
            return orderLoadBalancer.registerOrdereplicas(replicaUrl)
        else:
            return "Invalid Route"

    app.run(host="0.0.0.0", port=8080)
