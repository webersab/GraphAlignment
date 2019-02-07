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
    
    #max_key, max_value = max(d.items(), key = lambda x: len(set(x[1])))
    #print(max_key,max_value)

if __name__ == "__main__":
    print("Hello Graph Aligner")
    print("begin: ",datetime.datetime.now())
    #filePath="/disk/scratch_big/sweber/"
    filePath="/group/project/s1782911/"
    graphName="germanPERSON#PERSONbtchOfSix.txt"
    typePair="#PERSON.*#PERSON"
    
    #extract the German only entity set
    c = Parsing()
    entitySet = EntitySet()
    vectorMap = VectorMap()
    germanVectorMap, germanEntitySet = c.parse(filePath+graphName, entitySet, vectorMap, typePair)
    germanEntitySetLength=len(germanEntitySet.toSet())
    print("German entity set length: ",germanEntitySetLength,datetime.datetime.now())
    
    #extract the English only entity set
    #freshVectorMap = VectorMap()
    #freshEntitySet = EntitySet()
    #englishVectorMap, englishEntitySet = c.parse("/afs/inf.ed.ac.uk/user/s17/s1782911/location#location.txt", freshEntitySet, freshVectorMap)
    #englishEntitySetLength=len(englishEntitySet.toSet())
    #print("English entity set length: ",englishEntitySetLength)
    
    setLengthsDeEN=[germanEntitySetLength,0]
    
    #calculate the intersection of those sets. This is the overlap of entities
    #intersection=list(englishEntitySet.intersection(germanEntitySet.toSet()))
    #print("the overlap between the two sets is ",len(intersection))
    
    ###Extract the combined entity set and the according vector maps for English and German
    #entitySet = EntitySet()
    #vectorMap = VectorMap()
    #germanVectorMap, entitySet = c.parse("GermanLoc#LocNoRareEntities.txt", entitySet, vectorMap)
    #freshVectorMap = VectorMap()
    #englishVectorMap, entitySet = c.parse("/afs/inf.ed.ac.uk/user/s17/s1782911/location#location.txt", entitySet, freshVectorMap)
    
    #create Vector Maps that consider only the overlapping entities
    #overlapEnglishVectorMap=englishVectorMap.changeVectorsToOverlap(entitySet,intersection)
    #overlapGermanVectorMap=germanVectorMap.changeVectorsToOverlap(entitySet,intersection)
    
    #overlapEnglishVectorMap.printVectorMap()
    #overlapGermanVectorMap.printVectorMap()
    
    #pickling vector Maps for faster degbugging
    with open(filePath+graphName+"VectorMap.dat", "wb") as f:
        pickle.dump(germanVectorMap, f)
    #with open("englishVectorMap.dat", "wb") as f:
        #pickle.dump(englishVectorMap, f)
    #with open("intersection.dat", "wb") as f:
        #pickle.dump(intersection, f)
    with open(filePath+graphName+"set.dat", "wb") as f:
        pickle.dump(setLengthsDeEN, f)
    
    #unpickle
    with open(filePath+graphName+"VectorMap.dat", "rb") as f:
        germanVectorMap=pickle.load(f)
    # with open("englishVectorMap.dat", "rb") as f:
        #englishVectorMap=pickle.load(f)
    #with open("intersection.dat", "rb") as f:
        #intersection=pickle.load(f)
    with open(filePath+graphName+"set.dat", "rb") as f:
        setLengthsDeEN=pickle.load(f)
    print("done unpickling")
    
    #change vectors to PMI, if thats what you're after
    #overlapGermanVectorMap=overlapGermanVectorMap.changeVectorsToPmi()
    #overlapEnglishVectorMap=overlapEnglishVectorMap.changeVectorsToPmi()
    
    #create German graph
    d = GraphCreator()
    entitySetLengthDe=setLengthsDeEN[0]+1
    print("Entity Set len  de: ",entitySetLengthDe)
    G = d.createGraphParallel(germanVectorMap, entitySetLengthDe)
    G1= chineseWhisper.chinese_whispers(G, weighting='nolog', iterations=20, seed=None)
    
    #Creation of English graph begins here
    #entitySetLengthEn=setLengthsDeEN[1]+1
    #print("entity set len en: ",entitySetLengthEn)
    #G = d.createGraphParallel(englishVectorMap, entitySetLengthEn)
    #G2= chineseWhisper.chinese_whispers(G, weighting='nolog', iterations=20, seed=None)

    
    #print entity set line by line to file for translation for linking
    #entitySet.printEntitySetToFile()
    #print("PRINTED ENTITY SET")
    #print("entity Set length: ",entitySet.length()) 

    #pickling for easier debugging of later steps
    nx.write_gpickle(G1, filePath+graphName+"germanGraphPickle")
    #nx.write_gpickle(G2, "englishPicklePostParallel")
    #pickle entity set
    #with open("entitySet.dat", "wb") as f:
        #pickle.dump(entitySet, f)
      
    #unpickle
    G1=nx.read_gpickle(filePath+graphName+"germanGraphPickle")
    #G2=nx.read_gpickle("englishPicklePostPrallel")
    print(G1.nodes())
    #print(G2.nodes())
    #with open("intersection.dat", "rb") as f:
        #intersection=pickle.load(f)
    

    #extraction of clusters begins here
    print("begin clustering: ",datetime.datetime.now())
    k = Cluster()
    germanClusterList=k.getClustersFromGraph(G1,"german")
    print("done german")
    j=Cluster()
    #englishClusterList=j.getClustersFromGraph(G2,"english")
    #print(" done english")
    print("done clustering: ",datetime.datetime.now())
    
    #for i in germanClusterList:
        #print(i.printClusterPredicates())

    """
    
    #pickling to make debugging faster
    with open("clusteredGerman.dat", "wb") as f:
        pickle.dump(germanClusterList, f)
    #with open("clusteredEnglish.dat", "wb") as f:
        #pickle.dump(englishClusterList, f)
    print("done pickling")
    
    
    #unpickle
    with open("clusteredGerman.dat", "rb") as f:
        germanClusterList=pickle.load(f)
        
    for i in germanClusterList:
        print(i.predicates)
      
    with open("clusteredEnglish.dat", "rb") as f:
        englishClusterList=pickle.load(f)
    
    with open("intersection.dat", "rb") as f:
        intersection=pickle.load(f)
    print("done unpickling")
    #for cluster in germanClusterList:
        #print(cluster.predicates)
    entitySetLength=len(intersection)+1
    
    
    #alignment of clusters begins here
    a = Aligner()
    print("begin aligning: ",datetime.datetime.now())
    clusterTupleList=a.alignClustersNew(germanClusterList, englishClusterList, entitySetLength,intersection,"alignmentOutputWithcosineSim.txt")
    print("done aligning: ",datetime.datetime.now())
    
    #pickling of final list
    with open("alignedListNoPmi.dat", "wb") as f:
        pickle.dump(clusterTupleList, f)
    
    #for clusterTupel in clusterTupleList:
    #    clusterTupel[0].printClusterPredicates()
    #    clusterTupel[1].printClusterPredicates()
    #    print(clusterTupel[2])
    #    print("------------------------------")
    print("final result in alignmentOutputWithcosineSim.txt")
    """
    print (sys.version)