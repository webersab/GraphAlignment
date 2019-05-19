
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

def testGraphWithLevy(lambdaValue):
    mapOffalsePositives={}
    mapOffalseNegatives={}
    score=0
    
    #TODO
    inFile="googleTranslationReduced2.txt"
    
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
        #1948 is the number of lines in the levy data set, change accordingly
        for line in tqdm(file,total=1948):
            line=line.rstrip()
            line=line.split(". ")
            #print("line ",line)
            if len(line)<3:
                print("oopsie! ",line)
                continue
            
            listOfFoundClusters=[]
            typePairList=[]
            counterMap["totalcounter"]+=1
            hits=0
            
            #each predicate has a list of type pairs
            firstPredicates=xnliTest.extractPredicateFromSentence(model,line[0])
            secondPredicates=xnliTest.extractPredicateFromSentence(model,line[1])
            totalPredicateSet=set()
            #for each combination of predictates from sentence one and two
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
                                          
                    #print(typePairList)   
                    #Do this in case of way too low recall:
                    #typePairList=list(itertools.product(["PERSON","LOCATION","ORGANIZATION","EVENT","MISC"],repeat=2))
                    #typePairList.remove(("EVENT","EVENT"))
                    
                    #retrieve right graph
                    for typePair in set(typePairList):
                        graphFile=getRightGraphFile(typePair,lambdaValue)
                        if graphFile!="":
                            E, G=showEntGraphs.constructGraphFromFile(graphFile, lambdaValue)
                            #print(pred1,pred2)
                            if hasEntailment(pred1, pred2, G):
                                #At this point I am only counting true positives. 
                                #I need to implement a more detailled view of that
                                if line[2]=="y":
                                    hits+=1
                            else:
                                if line[2]=="n":
                                    hits+=1
                                
            if hits>0:
                counterMap["hitcounter"]+=1
                if line[2]=="y":
                    counterMap["truePositives"]+=1
                else:
                    counterMap["trueNegatives"]+=1
            else:
                if line[2]=="n":
                    counterMap["trueNegatives"]+=1
                else:
                    counterMap["falseNegatives"]+=1

    if counterMap["totalcounter"]>0:
        score=counterMap["hitcounter"]/counterMap["totalcounter"]
        print("score ",str(score))
        precision=counterMap["truePositives"]/(counterMap["truePositives"]+counterMap["trueNegatives"])
        recall=counterMap["truePositives"]/(counterMap["truePositives"]+counterMap["falseNegatives"])
        print("precision, recall ", precision, recall)
    with open("outputforLambda"+lambdaValue, "a") as f:
        for a, b in counterMap.items():
            f.write(str(a)+"\t"+str(b)+"\n")
            f.write("score: "+score+"\n")
            f.write("precision: "+precision+"\n")
            f.write("recall: "+recall+"\n")
            f1=(2*precision*recall)/(precision+recall)
            f.write("F1: "+str(f1))
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
        outputFile=outputFolder+type1+"#"+type2+"_sim_HTLFRG"
        fh=open(outputFolder+type1+"#"+type2+"_sim_HTLFRG", "r")
    except FileNotFoundError:
        pass
    try:
        outputFile=outputFolder+type2+"#"+type1+"_sim_HTLFRG"
        fh=open(outputFolder+type2+"#"+type1+"_sim_HTLFRG", "r")
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

    pred1NodesList=[]
    for n in list(G.nodes):
        for k, v in G.node[n].items(): 
            #print("v ", v, "pred1 ", pred1)
            if (bothNegated(pred1,v)or bothNonNegated(pred1,v)) and pred1 in v:
                pred1NodesList.append(n)
            
    #go trough list and check if pred2 is in node.successors
    for m in pred1NodesList:
        #test if word is in cluster
        for value in G.nodes[m].values():
            if (bothNegated(pred2,value)or bothNonNegated(pred2,value)) and pred2 in value:
                #print("IN SAME CLUSTER")
                return True
        #test if word is in agraph ancestors
        for k in nx.ancestors(G, m):
            for ke, va in G.node[k].items():
                if (bothNegated(pred2,va)or bothNonNegated(pred2,va)) and pred2 in va:
                    #print("IN GRAPH ANCESTORS")
                    return True
    return False

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
    lamb=sys.argv[1]
    testGraphWithLevy(lamb)
    
    
        
        