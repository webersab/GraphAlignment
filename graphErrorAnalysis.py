import udpipe_model as udp
import xnliTest
import itertools
import graphTest
import showEntGraphs
import sys
from collections import OrderedDict
import networkx as nx

def main(lmbda):
    # constants
    inFile="googleTranslationReduced2.txt"
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    #make dict for all the y cases
    documentDict={} #maps line number to sentence Dict
    
    lineNumber=0
    with open(inFile) as file:
        for line in file:
            lineDict=OrderedDict({})
            lineDict["line"]=line
            lineNumber+=1
            line=line.rstrip()
            line=line.split(". ")
            if line[2]=="y":
                firstPredicates=xnliTest.extractPredicateFromSentence(model,line[0])
                secondPredicates=xnliTest.extractPredicateFromSentence(model,line[1])
                lineDict["predicates"]=list(firstPredicates.keys()).append(list(secondPredicates.keys()))
                for pred1 in firstPredicates.keys():
                    for pred2 in secondPredicates.keys():
                        typePairList=list(itertools.product(["PERSON","LOCATION","ORGANIZATION","EVENT","MISC"],repeat=2))
                        typePairList.remove(("EVENT","EVENT"))
                        clusterInfoCounter=0
                        for typePair in set(typePairList):
                            graphFile=graphTest.getRightGraphFile(typePair,lmbda)
                            try:
                                if graphFile!="":
                                    E, G=showEntGraphs.constructGraphFromFile(graphFile, lmbda)
                            except TypeError:
                                lineDict["type Error"]=str(typePair)+str(lmbda)
                                continue
                            boo, clusterInfo = graphTest.hasEntailment(pred1, pred2, G)
                            if boo:
                                lineDict["clusterInfo"+clusterInfoCounter]=clusterInfo
                                clusterInfoCounter+=1
                            else:
                                #look for pred1 in graph,
                                nodesList1, connectedComponent1 = findPredicateInGraph(pred1, G)
                                if len(nodesList1)>0:
                                    lineDict[" ".join(nodesList1)]=pred1
                                if len(connectedComponent1)>0:
                                    lineDict[" ".join(connectedComponent1)]="Connected component of "+pred1
                                nodesList2, connectedComponent2 = findPredicateInGraph(pred2, G)
                                if len(nodesList2)>0:
                                    lineDict[" ".join(nodesList2)]=pred2
                                if len(connectedComponent2)>0:
                                    lineDict[" ".join(connectedComponent2)]="Connected component of "+pred2
    
            documentDict[lineNumber]=lineDict
    
    f=open("errorAnalysis.txt","a")
    for k,v in documentDict:
        f.write(str(k)+"\t"+str(v))

def findPredicateInGraph(pred,G):
    nodesList=[]
    connectedComponentList=[]
    for n in list(G.nodes):
        for k, v in G.node[n].items(): 
            if pred in v:
                nodesList.append(n)
                connectedCompnent=nx.node_connected_component(G, n)
                if len(connectedCompnent)>1:
                    for k in connectedCompnent:
                        connectedComponentList.append(G.node[k])
    return nodesList, connectedComponentList
    

if __name__ == "__main__":
    lamb=sys.argv[1]
    main(lamb)
   
    """
    lambdaList= [0.019,
                 0.029,
                 0.039,
                 0.050,
                 0.059,
                 0.070,
                 0.079,
                 0.090,
                 0.100,
                 0.200,
                 0.300,
                 0.400,
                 0.600,
                 0.699,
                 0.800,
                 0.899]
    """
    
    