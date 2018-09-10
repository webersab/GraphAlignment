from parsing import Parsing
from entitySet import EntitySet
from vectorMap import VectorMap
import sys
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import numpy as np
from graphCreator import GraphCreator
import chineseWhisper
from cluster import Cluster
from aligner import Aligner
import datetime
import pickle
from linker import Linker
import operator
import entitySet

def printClustersAfterWhisper(G):
    labelDict={}
    for i in G.nodes.data():
        if i[1]['label'] not in labelDict:
            nodeList = []
            nodeList.append(i[0])
            labelDict[i[1]['label']]=nodeList
        else:
            nodeList= labelDict[i[1]['label']]
            nodeList.append(i[0])
            labelDict[i[1]['label']]=nodeList 

    for i,j in labelDict.items():
        print(i,j)
    
    max_key, max_value = max(d.items(), key = lambda x: len(set(x[1])))
    print(max_key,max_value)

if __name__ == "__main__":
    print("Hello Graph Aligner")

    #parse entity pairs, predicates and their counts
    c = Parsing()
    entitySet = EntitySet()
    vectorMap = VectorMap()
    germanVectorMap, entitySet = c.parse("germanLoc#Loc.txt", entitySet, vectorMap)
    entitySet.printEntitySetToFile()
    
    d = GraphCreator()
    entitySetLength=entitySet.length()+1
    G = d.createGraph(germanVectorMap, entitySetLength)
    G1= chineseWhisper.chinese_whispers(G, weighting='nolog', iterations=20, seed=None)
    
    #Creation of English graph begins here
    freshVectorMap = VectorMap()
    englishVectorMap, entitySet = c.parse("/afs/inf.ed.ac.uk/user/s17/s1782911/location#location.txt", entitySet, freshVectorMap)
    entitySetLength=entitySet.length()+1
    G = d.createGraph(englishVectorMap, entitySetLength)
    G2= chineseWhisper.chinese_whispers(G, weighting='nolog', iterations=20, seed=None)

    
    #print entity set line by line to file for translation for linking
    entitySet.printEntitySetToFile()
    print("PRINTED ENTITY SET")
    print("entity Set length: ",entitySet.length()) 

    #pickling for easier debugging of later steps
    nx.write_gpickle(G1, "germanPickle")
    nx.write_gpickle(G2, "englishPickle")
    #pickle entity set
    with open("entitySet.dat", "wb") as f:
        pickle.dump(entitySet, f)
    """
    #unpickle
    G1=nx.read_gpickle("germanPickle")
    G2=nx.read_gpickle("englishPickle")
    entitySetLength=26664
    print(G1.nodes())
    print(G2.nodes())
    with open("entitySet.dat", "rb") as f:
        entitySet=pickle.load(f)
    """
    #printClustersAfterWhisper(G1)


    #extraction of clusters begins here
    print("begin clustering: ",datetime.datetime.now())
    k = Cluster()
    germanClusterList=k.getClustersFromGraph(G1,"german")
    print("done german")
    j=Cluster()
    englishClusterList=j.getClustersFromGraph(G2,"english")
    print(" done english")
    print("done clustering: ",datetime.datetime.now())
    
    
    #pickling to make debugging faster
    with open("clusteredGerman.dat", "wb") as f:
        pickle.dump(germanClusterList, f)
    with open("clusteredEnglish.dat", "wb") as f:
        pickle.dump(englishClusterList, f)
    print("done pickling")
    
    """
    #unpickle
    entitySetLength=26664
    with open("clusteredGerman.dat", "rb") as f:
        germanClusterList=pickle.load(f)
        
    with open("clusteredEnglish.dat", "rb") as f:
        englishClusterList=pickle.load(f)
    print("done unpickling")
    #for cluster in germanClusterList:
        #print(cluster.predicates)
    """
    
    #alignment of clusters begins here
    a = Aligner()
    print("begin aligning: ",datetime.datetime.now())
    clusterTupleList=a.alignClustersNew(germanClusterList, englishClusterList, entitySetLength)
    print("done aligning: ",datetime.datetime.now())
    
    #pickling of final list
    with open("alignedList.dat", "wb") as f:
        pickle.dump(clusterTupleList, f)
    
    for clusterTupel in clusterTupleList:
        clusterTupel[0].printClusterPredicates()
        clusterTupel[1].printClusterPredicates()
        print(clusterTupel[2])
        print("------------------------------")

    print (sys.version)