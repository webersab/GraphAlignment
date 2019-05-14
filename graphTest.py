
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

def testGraphWithLevy(lambdaValue):
    mapOffalsePositives={}
    mapOffalseNegatives={}
    score=0
    
    #TODO
    inFile="PUTlevyCorpusHere!!"
    
    counterMap={
    "hitcounter":0,
    "totalcounter":0,
    "truePositives":0,
    "trueNegatives":0,
    "falsePositives":0,
    "falseNegatives":0,
    "entCounter":0,
    "neuCounter":0}
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(inFile) as file:
        #4894 is the number of lines in the levy data set, change accordingly
        for line in tqdm(file,total=4894):
            line=line.rstrip()
            line=line.split(". ")
            print("line ",line)
            if len(line)<3:
                print("oopsie! ",line)
                continue
            
            listOfFoundClusters=[]
            typePairList=[]
            
            #each predicate has a list of type pairs
            firstPredicates=xnliTest.extractPredicateFromSentence(model,line[0])
            secondPredicates=xnliTest.extractPredicateFromSentence(model,line[1])
            totalPredicateSet=set()
            #for each combination of predictates from sentence one and two
            for pred1 in firstPredicates.keys():
                for pred2 in secondPredicates.keys():
                    #determine which cluster to pick dependent on predicate types
                    print(firstPredicates[pred1],secondPredicates[pred2])
                    overlapOfTypes = [value for value in firstPredicates[pred1] if value in secondPredicates[pred2]] 
                    
                    if len(overlapOfTypes)>0:
                        typePairList=overlapOfTypes
                    else:
                        typePairList = list(set(firstPredicates[pred1]) | set(secondPredicates[pred2])) 
                        
                    if len(typePairList)==0:
                        typePairList=[("MISC","MISC")]
                        
                    #Do this in case of way too low recall:
                    #typePairList=list(itertools.product(["PERSON","LOCATION","ORGANIZATION","EVENT","MISC"],repeat=2))
                    #typePairList.remove(("EVENT","EVENT"))
                    
                    #retrieve right cluster list
                    for typePair in set(typePairList):
                        graphFile=getRightGraphFile(typePair,lambdaValue)
                        g=createGraph(graphFile)
                        #make graph from graph file
                        for cluster in clusterList:
                            if len(cluster.predicates)<21:
                                predicateSet,listOfFoundClusters=checkClusters(pred1,pred2,cluster,listOfFoundClusters)
                                if predicateSet != set():
                                    for p in predicateSet:
                                        totalPredicateSet.add(p)
                #print(" total predicates Set", totalPredicateSet)
                print(" list of found clusters ",listOfFoundClusters)
            counterMap, mapOffalsePositives, mapOffalseNegatives = xnliTest.controlForEntailmentInLevy(listOfFoundClusters,line,firstPredicates,secondPredicates,
                                                                                           mapOffalsePositives,mapOffalseNegatives,counterMap, typePairList,totalPredicateSet)
            
    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))

    return score,mapOffalsePositives, mapOffalseNegatives

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
        outputFile=outputFolder+type1+"#"+type2+"_sim_HTLFRG"+lambdaValue
    except:
        pass
    try:
        outputFile=outputFolder+type1+"#"+type2+"_sim_HTLFRG"+lambdaValue
    except:
        outputFile=""
    
    return outputFile

if __name__ == "__main__":
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
    
    pred1="be_in"
    pred2="visit"
    
    #go trough all nodes and save node that fits into list
    pred1NodesList=[]
    for n in list(G.nodes):
        print("n ",n)
        print("gnode name ",G.node[n][name])
        if G.node[n][name]==pred1:
            pred1NodesList.append(n)
            print("Found pred 1 in ", G.node[n])
            
    #go trough list and check if pred2 is in node.successors
    print(pred1NodesList)
    for m in pred1NodesList:
        print(str(G.predecessors(m)))
        print(len(list(G.predecessors(m))))
        for k in G.predecessors(m):
            print("Bloop")
            print(G.node[k][name])
            if G.node[k][name]==pred2:
            #if so, call bingo
                print("Found pred2 in ", G.node[k])
                print("BINGO")
    
        
        
