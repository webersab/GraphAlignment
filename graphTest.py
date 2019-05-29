
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
import itertools
sys.path.append("/disk/scratch_big/sweber/udpipe-1.1.0-bin")
import pickle
import udpipe_model as udp
import datetime
from tqdm import tqdm
import pprint
from generalEntityTyping import GeneralEntityTyping
import socket
from pygermanet.germanet import load_germanet
import os
from itertools import chain
import numpy
import xnliTest
import networkx as nx
import showEntGraphs
import pprint
import matplotlib 
import matplotlib.pyplot as plt



def testGraphWithLevy(lambdaValue):
    # parallel python graphTest.py ::: 0.200 0.100 0.050 0.059 0.070 0.079 0.090
    score=0
    
    inFile="googleTranslationReduced2.txt"
    
    counterMap={
    "hitcounter":0,
    "totalcounter":0,
    "truePositives":0,
    "trueNegatives":0,
    "falsePositives":0,
    "falseNegatives":0,
    "samePredicatesEntail":0,
    "samePredicatesNonEntail":0,
    "samePredicateTotal":0
    }
    
    truePosDict={"totalNumber":0, "samePredicates":0}
    falsePosDict={"totalNumber":0, "samePredicates":0}
    falseNegDict={"totalNumber":0, "samePredicates":0}
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(inFile) as file:
        #1948 is the number of lines in the levy data set, change accordingly
        #for line in tqdm(file,total=1948):
        for line in file:
            samePredicates=False
            globalClusterInfo={}
            line=line.rstrip()
            line=line.split(". ")
            print("-------------------------------------------")
            print("line ",line)
            if len(line)<3:
                print("oopsie! ",line)
                continue
            
            typePairList=[]
            counterMap["totalcounter"]+=1
            hits=0
            
            #each predicate has a list of type pairs
            firstPredicates=xnliTest.extractPredicateFromSentence(model,line[0])
            secondPredicates=xnliTest.extractPredicateFromSentence(model,line[1])

            #for each combination of predictates from sentence one and two
            #print("all predicates", firstPredicates.keys(), secondPredicates.keys(), "entailment ",line[2])
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    #determine which graph to pick dependent on predicate types
                    overlapOfTypes = [value for value in firstPredicates[pred1] if value in secondPredicates[pred2]] 
                    
                    if len(overlapOfTypes)>0:
                        typePairList=overlapOfTypes
                    else:
                        #typePairList = list(set(firstPredicates[pred1]) | set(secondPredicates[pred2])) 
                        typePairList=list(set(firstPredicates[pred1]+secondPredicates[pred2]))
                        
                    if len(typePairList)==0:
                        typePairList=[("MISC","MISC")]
                                          
                    print(typePairList)   
                    #Do this in case of way too low recall:
                    #typePairList=list(itertools.product(["PERSON","LOCATION","ORGANIZATION","EVENT","MISC"],repeat=2))
                    #typePairList.remove(("EVENT","EVENT"))
                    
                    #retrieve right graph
                    for typePair in set(typePairList):
                        #print("hits number A", hits)
                        graphFile=getRightGraphFile(typePair,lambdaValue)
                        try:
                            if graphFile!="":
                                E, G=showEntGraphs.constructGraphFromFile(graphFile, lambdaValue)
                                print("predicates ",pred1,pred2)
                                if pred1 in pred2 or pred2 in pred1:
                                    samePredicates=True
                                    print("Same Predicates!")
                                boo, clusterInfo = hasEntailment(pred1, pred2, G)
                                if boo:
                                    hits+=1
                                    globalClusterInfo.update(clusterInfo)
                                    print(globalClusterInfo)
                        except TypeError:
                            #print("Type error in ", typePair, lambdaValue)
                            continue
            #print("hits number B", hits)                    
            if hits>0:
                if line[2]=="y":
                    counterMap["truePositives"]+=1
                    truePosDict[" ".join(line)]=hits
                    truePosDict["totalNumber"]+=1
                    if samePredicates:
                        truePosDict["samePredicates"]+=1
                        counterMap["samePredicatesEntail"]+=1
                    truePosDict.update(globalClusterInfo)
                    #print(line[0],line[1])
                    print("true pos. hits",hits, "entailment ", line[2])
                    counterMap["hitcounter"]+=1
                else:
                    counterMap["falsePositives"]+=1
                    falsePosDict[" ".join(line)]=hits
                    falsePosDict.update(globalClusterInfo)
                    falsePosDict["totalNumber"]+=1
                    if samePredicates:
                        falsePosDict["samePredicates"]+=1
                        counterMap["samePredicatesNonEntail"]+=1
                    #print(line[0],line[1])
                    print("FALSE POS. hits ",hits, "entailment ", line[2])
            else:
                if line[2]=="y":
                    counterMap["falseNegatives"]+=1
                    falseNegDict[" ".join(line)]=hits
                    falseNegDict["totalNumber"]+=1
                    if samePredicates:
                        falseNegDict["samePredicates"]+=1
                        counterMap["samePredicatesEntail"]+=1
                    #print(line[0],line[1])
                    print("false neg. hits ",hits, "entailment ", line[2] )
                else:
                    counterMap["trueNegatives"]+=1
                    #print(line[0],line[1])
                    if samePredicates:
                        counterMap["samePredicatesNonEntail"]+=1
                    print("true neg. hits ",hits, "entailment ", line[2])
                    counterMap["hitcounter"]+=1

    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))
        precision=counterMap["truePositives"]/(counterMap["truePositives"]+counterMap["falsePositives"])
        recall=counterMap["truePositives"]/(counterMap["truePositives"]+counterMap["falseNegatives"])
        print("precision, recall ", precision, recall)
    with open("outputforLambda"+lambdaValue, "a") as f:
        f.write("------------TRUE PODITIVES ----------------\n")
        for a, b in truePosDict.items():
            f.write(str(a)+"\t"+str(b)+"\n")
        f.write("------------- FALSE POSITIVES -------------\n")
        for a,b in falsePosDict.items():
            f.write(str(a)+"\t"+str(b)+"\n")
        f.write("------------ FALSE NEGATIVES --------------\n")
        for a,b in falseNegDict.items():
            f.write(str(a)+"\t"+str(b)+"\n")
        f.write("------------- overall Count -------------\n")
        for a, b in counterMap.items():
            f.write(str(a)+"\t"+str(b)+"\n")
        f.write("score: "+str(score)+"\n")
        f.write("precision: "+str(precision)+"\n")
        f.write("recall: "+str(recall)+"\n")
        f1=(2*precision*recall)/(precision+recall)
        f.write("F1: "+str(f1)+"\n")
    return score


def createGraph(graphFile):
    counter=0
    passedComponent=False
    passedLambda=False
    
    #for filename in os.listdir("/disk/scratch_big/sweber/entGraph/justGraphs"):
    with open(graphFile, 'r') as inF:
        number=-100
        for line in inF:
            if "lambda" in line and not passedLambda:
                G = nx.DiGraph()
                passedLambda=True
                passedComponent=False
            elif "component" in line:
                passedComponent=True
                lineSplit=line.split()
                number=int(lineSplit[1])
                G.add_node(number)
                #print("added ",number)
            elif "component" not in line and passedComponent and line!="" and "=>" not in line:
                name="verb"+str(counter)
                counter+=1
                if line!="\n" and number!=-100:
                    G.node[number][name]=line
            elif "component" not in line and passedComponent and line!="" and "=>" in line: 
                lineSplit=line.split()
                component=lineSplit[1]
                G.add_edge(number, component)
            elif line=="":
                passedComponent=False 
    return G

def getRightGraphFile(typePair,lambdaValue):
    outputFolder= "/disk/scratch_big/sweber/entGraph/justGraphs/"
    
    if typePair[0] == "NoSubj":
        type1="MISC"
    else:
        type1=typePair[0]
    if typePair[1]=="NoObj":
        type2="MISC"
    else:
        type2=typePair[1]
        
    try:
        outputFile=outputFolder+type1+"#"+type2+"_sim_HTLFRGZ"
        fh=open(outputFolder+type1+"#"+type2+"_sim_HTLFRGZ", "r")
    except FileNotFoundError:
        pass
    try:
        outputFile=outputFolder+type2+"#"+type1+"_sim_HTLFRGZ"
        fh=open(outputFolder+type2+"#"+type1+"_sim_HTLFRGZ", "r")
    except FileNotFoundError:
        outputFile=""
    return outputFile

def bothNegated(a,b):
    if ("NEG" in a) and ("NEG" in b):
        return True
    else:
        return False

def bothNonNegated(a,b):
    if "NEG" not in a and "NEG" not in b:
        return True
    else:
        return False

def hasEntailment(pred1, pred2, G):
    #print("len of G.nodes ", len(list(G.nodes)))
    clusterInfo={}

    pred1NodesList=[]
    for n in list(G.nodes):
        for k, v in G.node[n].items(): 
            #print("v ", v, "pred1 ", pred1)
            if (bothNegated(pred1,v)or bothNonNegated(pred1,v)) and pred1 in v:
                #print("found in ", v)
                pred1NodesList.append(n)
                connectedCompnent=nx.node_connected_component(G, n)
                #if len(connectedCompnent)>1:
                    #for k in connectedCompnent:
                        #print(G.node[k])
                
    #go trough list and check if pred2 is in node.successors
    for m in pred1NodesList:
        #test if word is in cluster
        for value in G.nodes[m].values():
            if (bothNegated(pred2,value)or bothNonNegated(pred2,value)) and pred2 in value:
                #print("IN SAME CLUSTER")
                #print(value,pred2)
                clusterInfo["IN SAME CLUSTER"]=[G.nodes[m].values()]
                return True, clusterInfo
        #test if word is in agraph ancestors
        for k in nx.ancestors(G, m):
            for ke, va in G.node[k].items():
                if (bothNegated(pred2,va)or bothNonNegated(pred2,va)) and pred2 in va:
                    #print("IN GRAPH ANCESTORS")
                    #print(va,pred2)
                    clusterInfo["IN GRAPH ANCESTORS"]=[nx.node_connected_component(G, k)]
                    return True, clusterInfo
    return False, clusterInfo

def createSmallTestGraph():
    #create small directed graph with two disconected components
    G = nx.DiGraph()
    name="verb"
    G.add_nodes_from([1,2,3,4,5,6,7])
    G.node[1][name]="be_in"
    G.node[2][name]="visit"
    G.node[3][name]="arrive"
    G.node[4][name]="leave"
    G.node[5][name]="play"
    G.node[6][name]="fail"
    G.node[7][name]="win"
    G.add_edges_from([(4,2),(2,1),(3,2),(7,5),(6,5)])
    print("created Graph")
    return G
    


if __name__ == "__main__":
    print("Hello Levy Graph Test!")
    print("begin: ",datetime.datetime.now())
    plt.plot([0.397,0.4224,0.3958,0.3437,0.3155,0.27,0.288,0.288,0.167,0.1510,0.1438,0.1428,0.1429],[0.58,0.588,0.5987,0.601,0.63,0.67,0.62,0.69,0.7477,0.76,0.786,0.7988,0.7988])
    plt.savefig('precision recall.png')
    
    #lamb=sys.argv[1]
    #testGraphWithLevy(lamb)
    
    
        
        
