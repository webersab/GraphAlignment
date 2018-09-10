import itertools
from graphCreator import GraphCreator
from sklearn.metrics.pairwise import cosine_similarity
import random
import sys

class Aligner:
    
    def alignClusters(self, listOfClusters, entitySetLength):
        gc = GraphCreator()
        listOfTuplesOfClusters=[] 
        iterationList=listOfClusters
        while iterationList!=None:
            combinations=itertools.combinations(iterationList, 2)
            highestCosineSim=0
            winningTuple=tuple()
            for k1,k2 in combinations:
                if gc.hasOverlap(k1.vector,k2.vector):
                    v1=gc.createSparseMatrix(k1.vector, entitySetLength)
                    v2=gc.createSparseMatrix(k2.vector, entitySetLength)
                    cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
                    if cosineSim>highestCosineSim:
                        highestCosineSim=cosineSim
                        winningTuple=(k1,k2)
            listOfTuplesOfClusters.append(winningTuple)
            iterationList.remove(winningTuple[0])
            iterationList.remove(winningTuple[1])
        return listOfTuplesOfClusters
    
    def alignClustersNew(self,listOfClusters1,listOfClusters2,entitySetLength):
        gc = GraphCreator()
        listOfTuplesOfClusters=[] 
        internalClusterList1 = listOfClusters1
        internalClusterList2 = listOfClusters2
        
        while internalClusterList1!=None and internalClusterList2!=None:
            iterationTupleList = list(itertools.product(internalClusterList1, internalClusterList2))
            highestCosineSim=0
            winningTuple=tuple()
            for k1,k2 in iterationTupleList:
                if gc.hasOverlap(k1.vector,k2.vector):
                    v1=gc.createSparseMatrix(k1.vector, entitySetLength)
                    v2=gc.createSparseMatrix(k2.vector, entitySetLength)
                    cosineSim = cosine_similarity(v1.reshape(1, -1),v2.reshape(1, -1))
                    if cosineSim>highestCosineSim:
                        highestCosineSim=cosineSim
                        winningTuple=(k1,k2,cosineSim)
            #this is a stupid hack because I don't have actual linking
            if len(iterationTupleList)<1:
                return listOfTuplesOfClusters
            if winningTuple==tuple():
                winningTuple=list(random.sample(iterationTupleList,1)[0])
                winningTuple.append(0)
                winningTuple=tuple(winningTuple)
            listOfTuplesOfClusters.append(winningTuple)
            internalClusterList1.remove(winningTuple[0])
            internalClusterList2.remove(winningTuple[1])
                #redirect printouts to file:
            orig_stdout = sys.stdout
            with open('alignmentOutputWithcosineSim.txt', 'a') as f:
                sys.stdout = f   
                print(winningTuple[0].predicates)
                print(winningTuple[1].predicates)
                print(winningTuple[2])
                print("------------------------------")
                f.close()
            sys.stdout = orig_stdout
        return listOfTuplesOfClusters   
        
        