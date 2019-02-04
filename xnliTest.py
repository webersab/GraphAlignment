#standard
import codecs
import csv
import sys
from nltk.parse import DependencyGraph
sys.path.append("/disk/scratch_big/sweber/udpipe-1.1.0-bin")
import pickle
#custom
import udpipe_model as udp
import datetime
from tqdm import tqdm
import pprint

def testGermanClusters(clusterListPickle,xnliSlice):

    mapOfHits={}
    mapOfFails={}
    score=0
    #unpickle cluster list
    with open(clusterListPickle, "rb") as f:
        clusterList=pickle.load(f)
    print("unpickled")
    hitcounter=0
    totalcounter=0
    
    modelfile ="germanModel.udpipe"
    model = udp.UDPipeModel(modelfile)
    
    with open(xnliSlice) as fd:
        rd = csv.reader(fd, delimiter="\t")
        for row in tqdm(rd,total=2491):
            firstPredicates=extractPredicateFromSentence(model,row[1])
            secondPredicates=extractPredicateFromSentence(model,row[2])
        #for each combination of predictates from sentence one and two
            localHitCounter=0
            hitClusters=[]
            hitPredicates=[]
            for pred1 in firstPredicates:
                for pred2 in secondPredicates:
                    for cluster in clusterList:
                        #print("pred1",pred1)
                        #print("pred2",pred2)
                        #print("cluster",cluster.predicates)
                        if (pred1 in cluster.predicates) and (pred2 in cluster.predicates):
                            print("BLOOP")
                            print("row 0",row[0])
                            if row[0]=="neutral" or row[0]=="entailment":
                                print("DING!")
                                localHitCounter+=1
                                hitClusters.append(cluster)
                                hitPredicates.append((pred1,pred2))
            if localHitCounter>0:
                hitcounter+=1
                totalcounter+=1
                mapOfHits[hitPredicates]=hitClusters
            else:
                totalcounter+=1
                s=row[1]+row[2]
                firstPredicates.extend(secondPredicates)
                t=(",".join(firstPredicates))
                mapOfFails[t]=s
                #print(firstPredicates,secondPredicates)
    if totalcounter>0:
        score=hitcounter/totalcounter
    return score,mapOfHits, mapOfFails

def dependency_parse_to_graph(filename):
    """
    Read dependency parser output from file and construct graph
    """
    data = ''
    dtree = []
    with open(filename, 'r') as f:
        for line in f:
            if line[0] != '#':
                if 'root' in line:
                    elements = line.split('\t')
                    if elements[7] == 'root':
                        elements[7] = 'ROOT'
                        line = '\t'.join(elements)
                data += line
                if line == '\n':
                    dg = DependencyGraph(data)
                    dtree.append(dg)
                    data = ''
    return dtree


def parseToArray(testFile):
    array=[]
    with open(testFile) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            array.append(row)
    return array

def treeToPredList(d):   
    #in the simplest case root is predicate
    listOfPredicates=[]
    root=d.nodes[0]['deps']['ROOT'][0]
    predicate=d.nodes[root]['lemma']
    #other cases
    if d.nodes[root]['ctag'] != 'VERB':
        for n in d.nodes:
            #adj or noun plus 'be'
            if d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']=='sein' or d.nodes[n]['lemma']=='be'):
                predicate=d.nodes[root]['word']
                predicate=predicate+'.sein'
                listOfPredicates.append(predicate)
            elif d.nodes[n]['ctag']=='VERB' and (d.nodes[n]['lemma']!='sein'or d.nodes[n]['lemma']=='be'):
                listOfPredicates.append(d.nodes[n]['lemma'])
        #print(predicate)
        #print(listOfPredicates)
    else:
        listOfPredicates.append(predicate)
    return listOfPredicates

def extractPredicateFromSentence(model, sentence):
    sent = model.tokenize(sentence)
    for s in sent:
        model.tag(s)
        model.parse(s)
    conllu = model.write(sent, "conllu")
    outfile = "conllOut.txt"
    with codecs.open(outfile, 'w', 'utf-8') as o:
        o.write(conllu)
    #print("wrote conllu file")
    
    predicateList=[]
    dtree = dependency_parse_to_graph("conllOut.txt")
    i=0
    for d in dtree:
        predicateList=treeToPredList(d)
    #print("done extracting predicates") 
    return predicateList

def extractPredicatesFromSentenceList(language,sentenceList):
    print("extracting predicates")
    sentenceToPredicateMap={}
    if language=="de":
        modelfile ="germanModel.udpipe"
    elif language=="en":
        modelfile ="englishModel.udpipe"

    model = udp.UDPipeModel(modelfile)
    for x in sentenceList:
        sent = model.tokenize(x)
        for s in sent:
            model.tag(s)
            model.parse(s)
        conllu = model.write(sent, "conllu")
        outfile = "conllOut"+language+".txt"
        with codecs.open(outfile, 'a', 'utf-8') as o:
            o.write(conllu)
    print("wrote conllu file")

    sentenceToPredicateMap={}
    dtree = dependency_parse_to_graph("conllOut"+language+".txt")
    i=0
    for d in dtree:
        predicateList=treeToPredList(d)
        sentenceToPredicateMap[i]=predicateList
        i+=1
    print("done extracting predicates") 
    return sentenceToPredicateMap


def testWithXNLI(testFile,listOfTuplesOfClusters,languagePair):
    mapOfJudgements={}
    #parse the tsv into a 2d array containing one entailment sentence pair per row. 
    inputArray=parseToArray(testFile)
    if [] in inputArray:
        inputArray.remove([])
    print("parsed text to array")   
    ##depending on the language pair zip the array to two lists
    if languagePair=="enDe":
        englishHalf, germanHalf= zip(*inputArray)
    elif languagePair=="deEn":
        germanHalf, englishHalf= zip(*inputArray)
    print("english")
    englishMapping=extractPredicatesFromSentenceList("en", englishHalf)
    print("german")
    germanMapping=extractPredicatesFromSentenceList("de", germanHalf)
    
    #if predicates in same cluster entail
    #if predicates not in same cluster contradict
    print(englishMapping)
    print(germanMapping)
    for el in listOfTuplesOfClusters:
        print(el[0].predicates,el[1].predicates, el[2])
    
    print("start looking in map")
    for i in englishMapping:
        englishPredicates=englishMapping[i]
        germanPredicates=germanMapping[i]
        for tup in listOfTuplesOfClusters:
            print(englishPredicates,germanPredicates,tup[0].predicates,tup[1].predicates)
            list1=tup[0].predicates
            list1.append(tup[1].predicates)
            #print(list1)
            if (englishPredicates in list1 and germanPredicates in list1):
                mapOfJudgements[i]=1
            else:
                mapOfJudgements[i]=0
    #add option for neutral based on other criteria as well? TODO
    
    return mapOfJudgements

def compareJudgements(goldJudgements,myJudgements):
    #make a list from the gold judgement input file
    #totalJudgements=len(goldList)
    #if golList[i]==myList[i] counter+=1
    #finalPercentage=counter/totalJudgements
    return None

if __name__ == "__main__":
    print("Hello XNLITest!")
    print("begin: ",datetime.datetime.now())
    
    score, mapOfHits, mapOfFails=testGermanClusters("clusteredGerman.dat","deXNLI.tsv")
    
    print("The score is: "+str(score))
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(mapOfHits)
    #pp.pprint(mapOfFails)
    
    
    
    """
    print("hup hup")
    with open("alignedList.dat", "rb") as f:
        clusterTupleList=pickle.load(f)
    print("got the pickle")
    mapOfJudegements=testWithXNLI("enDeXnli.txt", clusterTupleList, "enDe")
    print(mapOfJudegements)
    """
