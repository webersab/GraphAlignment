import itertools
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import datetime
from scipy.sparse import csr_matrix
import networkx as nx
#import matplotlib.pyplot as plt
#from main import vectorMap, entitySetLengthDe
import multiprocessing as mp
import pickle
import pprint
from tqdm import tqdm
from vectorMap import VectorMap
from scipy import sparse


class GraphCreator():
    
    def createVector(self,listOfTuples,length):
        vector = [0]*length
        for tup in listOfTuples:
            vector[tup[0]]=tup[1]
        return np.asarray(vector)
    
    def createSparseMatrix(self,listOfTuples,length):
        zippedTuples = zip(*listOfTuples)
        counter = 0
        counts = np.array([0])
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
    
    def createSparseBigMatrix(self,listOfTuples, index, length, width):
        zippedTuples = zip(*listOfTuples)
        counter = 0
        counts = np.array([0])
        for w in zippedTuples:
            if counter==0:
                indexes = np.array(list(w))
                counter=counter+1
            elif counter==1:
                counts = np.array(list(w))
                counter=counter+1
            else:
                print("Error while zipping tuples")
        column =[index]*len(indexes)
        return csr_matrix((counts, (indexes, column)), shape=(length, width))
    
    def hasOverlap(self,listOfTuples1, listOfTuples2):
        bol = False
        zipped1=list(zip(*listOfTuples1))
        zipped2=list(zip(*listOfTuples2))
        if not set(zipped1[0]).isdisjoint(zipped2[0]):
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
    
    def split(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
        
    
    def calculateCosineSim(self,batch, entitySetLength, return_dict):
        for b in batch:
            key=batch.get(b)
            k1=key[0]
            k2=key[1]
            #print(" -- ")
            if k1!=k2 and k1!=[] and k2!=[] and self.hasOverlap(k1, k2):
                #print("...")
                v1=self.createSparseMatrix(key[0], entitySetLength)
                v2=self.createSparseMatrix(key[1], entitySetLength)
                cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
                if cosineSim>0:
                    return_dict[b]=cosineSim
            #print(b,return_dict[b])
        return True
    
    def selectForCalculateMap(self,keyPairBatch,vectorMap,actualCalculateMap): 
        for keyPair in tqdm(keyPairBatch,total=len(keyPairBatch),unit="batches"):
            k1=keyPair[0]
            k2=keyPair[1]
            if k1!=k2 and vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[] and self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
                actualCalculateMap[(k1,k2)]=(vectorMap.get(k1),vectorMap.get(k2))
    
    
    def createGraphMatrixMultiplication(self,vectorMap, entitySetLength):
        print("begin createGraph: ",datetime.datetime.now())
        cores = mp.cpu_count()
        print(cores, " cores available")
        
        index=0
        indexPredicateMap={}
        vectorMapLength=len(vectorMap.keys())
        #create sparse matrix with the right dimensions
        matrix=csr_matrix( (entitySetLength, vectorMapLength), dtype="int8" )
        print("vector map length ",vectorMapLength)
        for key, value in vectorMap.items():
            # remember the key and the index of the matrix the key belongs to
            if value:
                indexPredicateMap[index]=key
                #print("at predicate ",key)
                #extract from value the right values and indexes. Create a Matrix thats empty except for that
                #print("Input ",value, index, vectorMapLength, entitySetLength)
                predicateMatrix=self.createSparseBigMatrix(value, index, entitySetLength, vectorMapLength)
                #print("nonzer elements in predicate matrix: ", predicateMatrix.nonzero())
                #print(str(len(predicateMatrix.nonzero())),"non zero elements in predicate matrix")
                #add that matrix to the original empty one
                matrix=matrix+predicateMatrix
                #print(str(len(matrix.nonzero())),"non zero elements in matrix")
                index+=1
        
        #calculate cosine sim from that matrix
        similarities = cosine_similarity(matrix.transpose())
        #for all non-zero entries, create a node and in the graph and so on
        nonZeroEntries=similarities.nonzero()
        G=nx.Graph()
        
        for i in range(len(nonZeroEntries[0])):
            #walk trough the arrays and get the indexes
            predicate1index=nonZeroEntries[0][i]
            predicate2index=nonZeroEntries[1][i]
            #look up what predicates the indexes correspond to
            predicate1=indexPredicateMap[predicate1index]
            predicate2=indexPredicateMap[predicate2index]
            #look up the matrix value
            cosineSim=similarities[predicate1index][predicate2index]
            
            #create nodes and connection with those values
            if predicate1!=predicate2:
                self.createNode(G, predicate1,vectorMap.get(predicate1))
                self.createNode(G, predicate2,vectorMap.get(predicate2))
                G.add_edge(predicate1, predicate2, weight=cosineSim )
                #print("created egde between", predicate1, predicate2, cosineSim)
        
        print("end createGraph ",datetime.datetime.now())
        return G
        
    
    def createGraphParallel(self, vectorMap, entitySetLength):
        print("begin createGraph: ",datetime.datetime.now())
        
        #pairsToCaluclate=itertools.combinations(vectorMap, 2)
        #print(len(list((pairsToCaluclate)))," pairs to calculate")
        
        
        
        cores = mp.cpu_count()
        #cores=35
        print(cores, " cores available")
        """
        keyPairs=itertools.combinations(vectorMap.keys(), 2)
        keyPair_batches=list(self.split(list(keyPairs),cores))
        
        manager = mp.Manager()
        actualCalculateMap = manager.dict()
        jobs = []
        
        for kpbatch in keyPair_batches:
            pro = mp.Process(target=self.selectForCalculateMap, args=(kpbatch,vectorMap,actualCalculateMap))
            jobs.append(pro)
            pro.start()
            
        for proc in jobs:
            proc.join()
        
        #for k1, k2 in itertools.combinations(vectorMap, 2):
            #if k1!=k2 and vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[] and self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
                #actualCalculateMap[(k1,k2)]=(vectorMap.get(k1),vectorMap.get(k2))
        #for k1, v1 in tqdm(vectorMap.items(),total=len(vectorMap.items()),unit="predicates"):
        #    for k2, v2 in vectorMap.items():
        #        if k1!=k2 and vectorMap.get(k1)!=[] and vectorMap.get(k2)!=[] and self.hasOverlap(vectorMap.get(k1), vectorMap.get(k2)):
        #            actualCalculateMap[(k1,k2)]=(vectorMap.get(k1),vectorMap.get(k2))
        print(len(actualCalculateMap)," with cosineSim > 0")
        print("done with actual calulate map: ",datetime.datetime.now())
        
        #pickle for easier debugging
        with open("actualCalculateMap.dat", "wb") as f:
            pickle.dump(actualCalculateMap, f)
        with open("actualCalculateMap.dat", "rb") as f:
            actualCalculateMap=pickle.load(f)
        print("done pickle")  
        """ 
        actualCalculateMap={}
        
        for k1, k2 in tqdm(itertools.combinations(vectorMap, 2),total=(len(vectorMap.keys())*len(vectorMap.keys())*0.5),unit="preds"):
                actualCalculateMap[(k1,k2)]=(vectorMap.get(k1),vectorMap.get(k2))
        
        print("done calculate map")
        #multiprocessing of the actual calculate list begins here
        key_batches=list(self.split(list(actualCalculateMap.keys()),cores))
        batches=[]
        for keys in key_batches:
            newMap={}
            for element in keys:
                newMap[element]=actualCalculateMap.get(element)
            batches.append(newMap)
        
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        
        for ba in batches:
            p = mp.Process(target=self.calculateCosineSim, args=(ba,entitySetLength,return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        print("length of return dict",len(return_dict))
        
        with open("/group/project/s1782911/return_dict.dat", "wb") as f:
            pickle.dump(return_dict.copy(), f)
            
          
        with open("/group/project/s1782911/return_dict.dat", "rb") as f:
            return_dict=pickle.load(f)
            print("unpickled")
        
        G=nx.Graph()
        for key, value in return_dict:
            self.createNode(G, key,vectorMap.get(key))
            self.createNode(G, value,vectorMap.get(value))
            if return_dict.get((key,value))[0][0]>0:
                G.add_edge(key, value, weight=return_dict.get((key,value))[0][0] )
                print("created egde between", key, value, return_dict.get((key,value))[0][0])
        print("end createGraph ",datetime.datetime.now())
        return G
    
    
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
        
