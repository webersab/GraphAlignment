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
import socket
from _elementtree import Element
import itertools
import os
from scipy.sparse import csr_matrix
from graphCreator import GraphCreator
from sklearn.metrics import pairwise_distances
import mathUtils

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
    
def whereAmI():
    filePath=""
    outputFolder=""
    print("on "+socket.gethostname())
    if socket.gethostname()=="pataphysique.inf.ed.ac.uk":
        filePath="/disk/scratch_big/sweber/preprocessingOutput/"
        outputFolder="/disk/scratch_big/sweber/outputPickles/"
    elif socket.gethostname()=="ebirah.inf.ed.ac.uk":
        filePath="/group/project/s1782911/"
        outputFolder="/group/project/s1782911/outputPickles/"
    elif socket.gethostname()=="darkstar.inf.ed.ac.uk":
        filePath="/disk/data/darkstar2/s1782911/preprocessingOutput/"
        outputFolder="/disk/data/darkstar2/s1782911/outputPickles/"
    return filePath, outputFolder
            
    
def makeOtherSimilarities(pair, similarityMeasure):
    filePath,outputFolder=whereAmI()
    graphName="german#"+pair[0]+"#"+pair[1]
    #unpickle
    if os.path.getsize(outputFolder+graphName+"VectorMap.dat") > 0:
        with open(outputFolder+graphName+"VectorMap.dat", "rb") as f:
            vectorMap=pickle.load(f)
    if os.path.getsize(outputFolder+graphName+"setLengthsDeEn.dat") > 0:    
        with open(outputFolder+graphName+"setLengthsDeEn.dat", "rb") as f:
            setLengthsDeEN=pickle.load(f)
    print("done unpickling")
    
    entitySetLength=setLengthsDeEN[0]+1
    d = GraphCreator()
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
            #extract from value the right values and indexes. Create a Matrix thats empty except for that
            predicateMatrix=d.createSparseBigMatrix(value, index, entitySetLength, vectorMapLength)
            #add that matrix to the original empty one
            matrix=matrix+predicateMatrix
            index+=1
    
    reversedIndexMap={y:x for x,y in indexPredicateMap.items()}
    
    computeSimilarity(similarityMeasure, matrix, reversedIndexMap,outputFolder,graphName)
    print("done with ",pair)
    
    
def printSimilarities(similarities,reversedIndexMap):
    indexPredicateMap={y:x for x,y in reversedIndexMap.items()}  
    nonZeroLin=similarities.nonzero()
    for i in range(len(nonZeroLin[0])):
        #walk trough the arrays and get the indexes
        predicate1index=nonZeroLin[0][i]
        predicate2index=nonZeroLin[1][i]
        #look up what predicates the indexes correspond to
        predicate1=indexPredicateMap[predicate1index]
        predicate2=indexPredicateMap[predicate2index]
        #look up the matrix value
        linSimilarity=similarities[predicate1index][predicate2index]
        print(predicate1,predicate2,linSimilarity)    

def computeSimilarity(measure, matrix,reversedIndexMap,outputFolder, graphName):
    if measure=="lin":
        metric=mathUtils.lin
    if measure=="weedsRecall":
        metric=mathUtils.weeds_recall
    if measure=="weedsPrecision":
        metric=mathUtils.weeds_precision
    if measure=="binc":
        metric=mathUtils.binc 
        
    similarities= pairwise_distances(matrix.transpose(), metric=metric, n_jobs=30)  
    
    if len(similarities.nonzero()[0])==0:
        "Sanity check failed, no nonzero similarities!"
    
    with open(outputFolder+graphName+measure+"Similarities.dat", "wb") as f:
        pickle.dump(similarities, f,protocol=4)
    with open(outputFolder+graphName+measure+"reversedIndexMap.dat", "wb") as f:
        pickle.dump(reversedIndexMap, f,protocol=4)
    

if __name__ == "__main__":
    print("Hello Graph Aligner")
    print("begin: ",datetime.datetime.now())

    """
    typePairList=[("EVENT","LOCATION"),("ORGANIZATION","PERSON"),("MISC","PERSON"),
                ("LOCATION","ORGANIZATION"),("MISC","ORGANIZATION"),("LOCATION","PERSON"),("ORGANIZATION","ORGANIZATION"),
                ("ORGANIZATION","EVENT"),("EVENT","ORGANIZATION"),("PERSON","ORGANIZATION"),("LOCATION","EVENT"),
                ("PERSON","PERSON"),
                ("ORGANIZATION","LOCATION"),("LOCATION","LOCATION"),("MISC","MISC"),("MISC","LOCATION"),
                ("PERSON","EVENT"),("PERSON","LOCATION"),("LOCATION","MISC"),("ORGANIZATION","MISC"),("PERSON","MISC"),
                ("LOCATION","EVENT"),("PERSON","PERSON"),("ORGANIZATION","LOCATION"),("LOCATION","LOCATION"),("MISC","MISC"),("MISC","LOCATION"),
               ("PERSON","EVENT"),("PERSON","LOCATION"),("LOCATION","MISC"),("ORGANIZATION","MISC"),("PERSON","MISC"),("MISC","EVENT")]
    """
    typePairList=[("EVENT","ORGANIZATION")]
    similarityMeasures=["lin","weedsRecall","weedsPrecison","binc"]
    
    for a in typePairList:
        for b in similarityMeasures:
            makeOtherSimilarities(a, b)

    """
    #typePairList=itertools.product(["EVENT","LOCATION","PERSON","ORGANIZATION","MISC"], repeat=2)
    for pair in typePairList:
        
        graphName="german#"+pair[0]+"#"+pair[1]
        typePair="#"+pair[0]+".*#"+pair[1]
        
        filePath=""
        outputFolder=""
        print("on "+socket.gethostname())
        if socket.gethostname()=="pataphysique.inf.ed.ac.uk":
            filePath="/disk/scratch_big/sweber/preprocessingOutput/"
            outputFolder="/disk/scratch_big/sweber/outputPickles/"
        elif socket.gethostname()=="ebirah.inf.ed.ac.uk":
            filePath="/group/project/s1782911/"
            outputFolder="/group/project/s1782911/outputPickles/"
        elif socket.gethostname()=="darkstar.inf.ed.ac.uk":
            filePath="/disk/data/darkstar2/s1782911/preprocessingOutput/"
            outputFolder="/disk/data/darkstar2/s1782911/outputPickles/"
            
    
        
        
        #extract the German only entity set
        c = Parsing()
        entitySet = EntitySet()
        vectorMap = VectorMap()
        germanVectorMap, germanEntitySet = c.parse(filePath+graphName+".txt", entitySet, vectorMap, typePair)
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
        with open(outputFolder+graphName+"VectorMap.dat", "wb") as f:
            pickle.dump(germanVectorMap, f)
        #with open("englishVectorMap.dat", "wb") as f:
            #pickle.dump(englishVectorMap, f)
        #with open("intersection.dat", "wb") as f:
            #pickle.dump(intersection, f)
        with open(outputFolder+graphName+"setLengthsDeEn.dat", "wb") as f:
            pickle.dump(setLengthsDeEN, f)
            
        
        #unpickle
        if os.path.getsize(outputFolder+graphName+"VectorMap.dat") > 0:
            with open(outputFolder+graphName+"VectorMap.dat", "rb") as f:
                germanVectorMap=pickle.load(f)
        # with open("englishVectorMap.dat", "rb") as f:
            #englishVectorMap=pickle.load(f)
        #with open("intersection.dat", "rb") as f:
            #intersection=pickle.load(f)
        if os.path.getsize(outputFolder+graphName+"setLengthsDeEn.dat") > 0:    
            with open(outputFolder+graphName+"setLengthsDeEn.dat", "rb") as f:
                setLengthsDeEN=pickle.load(f)
        print("done unpickling")
        
        #change vectors to PMI, if thats what you're after
        #overlapGermanVectorMap=overlapGermanVectorMap.changeVectorsToPmi()
        #overlapEnglishVectorMap=overlapEnglishVectorMap.changeVectorsToPmi()
        
        #create German graph
        d = GraphCreator()
        entitySetLengthDe=setLengthsDeEN[0]+1
        print("Entity Set len  de: ",entitySetLengthDe)
        G = d.createGraphMatrixMultiplication(germanVectorMap, entitySetLengthDe,outputFolder,graphName)
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
        nx.write_gpickle(G1, outputFolder+graphName+"GraphPickle")
        #nx.write_gpickle(G2, "englishPicklePostParallel")
        #pickle entity set
        #with open("entitySet.dat", "wb") as f:
            #pickle.dump(entitySet, f)
          
        #unpickle
        G1=nx.read_gpickle(outputFolder+graphName+"GraphPickle")
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
    
        
        
        #pickling to make debugging faster
        with open(outputFolder+graphName+"Clustered.dat", "wb") as f:
            pickle.dump(germanClusterList, f)
        #with open("clusteredEnglish.dat", "wb") as f:
            #pickle.dump(englishClusterList, f)
        print("done pickling")
        
        
        #unpickle
        with open(outputFolder+graphName+"Clustered.dat", "rb") as f:
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
        
        #print (sys.version)
        print("Finished ",pair, datetime.datetime.now())
        """