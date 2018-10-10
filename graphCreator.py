import itertools
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import datetime
from scipy.sparse import csr_matrix
import networkx as nx
import matplotlib.pyplot as plt

class GraphCreator():
    
    def createVector(self,listOfTuples,length):
        vector = [0]*length
        for tup in listOfTuples:
            vector[tup[0]]=tup[1]
        return np.asarray(vector)
    
    def createSparseMatrix(self,listOfTuples,length):
        zippedTuples = zip(*listOfTuples)
        counter = 0
        for w in zippedTuples:
            if counter==0:
                indexes = np.array(list(w))
                counter=counter+1
            elif counter==1:
                counts = np.array(list(w))
                counter=counter+1
            else:
                print("Error while zipping tuples")
        column =[0]*len(indexes)
        return csr_matrix((counts, (indexes, column)), shape=(length, 1))
    
    def hasOverlap(self,listOfTuples1, listOfTuples2):
        bol = False
        zipped1=list(zip(*listOfTuples1))
        zipped2=list(zip(*listOfTuples2))
        if not set(zipped1).isdisjoint(zipped2):
            bol=True
        
        return bol
    
    def createNode(self,graph,node, vector):
        if node in graph:
            return graph
        else: 
            graph.add_node(node,vector=vector)
            return graph
    
    def graphToFile(self,graph,path):
        nx.draw(graph,with_labels=True)
        print("Printed graph to ",path)
        return None
    
    def createGraph(self,vectorMap,entitySetLength):
        print("begin createGraph: ",datetime.datetime.now())
        print(len(list(itertools.combinations(vectorMap, 2)))," pairs to calculate")
        counter=0
        G=nx.Graph()
        for k1, k2 in itertools.combinations(vectorMap, 2):
            if vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[]:
                self.createNode(G, k1,vectorMap.get(k1))
                self.createNode(G, k2,vectorMap.get(k2))
                if self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
                    v1=self.createSparseMatrix(vectorMap.get(k1), entitySetLength)
                    v2=self.createSparseMatrix(vectorMap.get(k2), entitySetLength)
                    cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
                    if cosineSim>0:
                        G.add_edge(k1, k2, weight=cosineSim )
                    counter=counter+1
        print("end createGraph ",datetime.datetime.now())
        print(counter," pairs calculated")
        return G
        
