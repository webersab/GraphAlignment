# coding=utf-8

import requests
import pickle
import os
import pprint
import time
import string
from tqdm import tqdm
import sys
import re
import csv


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def getAttributesFomInternet(entity,lang):
    if lang=="de":
        url = 'http://de.dbpedia.org/resource/'
        propUrl='http://de.dbpedia.org/property/'
    else:
        url = 'http://dbpedia.org/resource/'
        propUrl='http://dbpedia.org/property/'
        
    r = requests.get(url+entity)
    
    foundList=[]
    for line in r.text.split(sep="\n"):
        if lang=="de":
            found=find_between(line, "<li><span class=\"literal\"><a class=\"uri\" rev=\"prop-de:", "\"")
            found=propUrl+found
            
            if (found!=propUrl) and (found not in foundList):
                foundList.append(found)
        else:
            found=find_between(line, "</ul></td></tr><tr class=\"even\"><td class=\"property\"><a class=\"uri\" href=\"", "\"")
            if (found!="") and ("ontology" not in found) and found not in foundList:
                foundList.append(found)
    return foundList
    
def getAttributesFromFile(entity):
    foundList=[]
    propUrl='http://de.dbpedia.org/property/'
    toFind='<http://de.dbpedia.org/resource/'+entity+">"
    
    firstLetter=entity[0].lower()
    if firstLetter in list(string.ascii_lowercase):
        filePath="/disk/scratch_big/sweber/alphabetBatches/Attribute_"+firstLetter
        with open(filePath, 'r') as inF:
            for line in inF:
                if toFind in line:
                    #print(line)
                    found=find_between(line, propUrl, ">")
                    found=propUrl+found
                    #print(found)
                    if (found!=propUrl) and (found not in foundList):
                        foundList.append(found)
                
    return foundList
    
def getGermanLink(entity):
    firstLetter=entity[0].lower()
    if firstLetter in list(string.ascii_lowercase):
        filePath="/disk/scratch_big/sweber/alphabetBatches/InterLanguage_"+firstLetter
        with open(filePath, 'r') as inF:
            for line in inF:
                if str(entity) in str(line):
                    link=find_between(line, "http://de.dbpedia.org/resource/", ">")
                    link="http://de.dbpedia.org/resource/"+link
                    return link
    return ""

def getGermanFromDict(entity):
    with open("/disk/scratch_big/sweber/GraphAlignment/stringDictDeEn.tsv", 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        decode = {r[0]: r[1] for r in reader}
        
    if entity in decode.values():
        inv_map = {v: k for k, v in decode.items()}
        print("GOT it ",inv_map(entity))
        return inv_map(entity)
    else:
        return ""
    
    

def constructEntityDictionary():
    f=open("/disk/scratch_big/sweber/GCN-in/entDict","a")
    fileCounter=1
    entDict={}
    identifier=0
    
    for filename in os.listdir("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f"):
        with open("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f/"+filename, 'r') as inF:
            print("now in file ",filename, fileCounter, "of 355")
            fileCounter+=1
            for line in inF:
                doubleEnt=find_between(line, "inv idx of", " :")
                enti=doubleEnt.split(sep="#")
                for ent in enti:
                    ent=ent.lstrip()
                    ent=ent.title()
                    ent=ent.replace(" ", "_")
                    if ent=="":
                        continue
                    if ent not in entDict.keys():
                        entDict[ent]=identifier
                        idIn=str(identifier)+"\thttp://dbpedia.org/resource/"+ent+"\n"
                        f.write(idIn)
                        identifier+=1

    with open("/disk/scratch_big/sweber/GCN-in/entDict.dat", "wb") as f:
        pickle.dump(entDict, f)
        
def constructGermanEntityDictionary():
    f=open("/disk/scratch_big/sweber/GCN-in/deEntDict","a")
    entDict={}
    identifier=300000
    
    for filename in os.listdir("/disk/scratch_big/sweber/outputPickles"):
        if filename.endswith("germanEntitySet2.dat"):
            print(filename)
            with open("/disk/scratch_big/sweber/outputPickles/"+filename, 'rb') as inF:
                entitySet=pickle.load(inF)
                for doubleEnt in entitySet:
                    enti=doubleEnt.split(sep="#")
                    for ent in enti:
                        ent=ent.lstrip()
                        ent=ent.title()
                        ent=ent.replace(" ", "_")
                        if ent=="":
                            continue
                        if ent not in entDict.keys():
                            entDict[ent]=identifier
                            idIn=str(identifier)+"\thttp://de.dbpedia.org/resource/"+ent+"\n"
                            f.write(idIn)
                            identifier+=1
                        
    with open("/disk/scratch_big/sweber/GCN-in/deEntDict.dat", "wb") as f:
        pickle.dump(entDict, f)

def constructRelationDictionary():
    f=open("/disk/scratch_big/sweber/GCN-in/relDict","a")
    fileCounter=1
    relDict={}
    identifier=200000
    entityScope=False
    
    for filename in os.listdir("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f"):
        with open("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f/"+filename, 'r') as inF:
            print("now in file ",filename, fileCounter, "of 355")
            fileCounter+=1
            for line in inF:
                if "inv idx of" in line:
                    entityScope=True
                elif "inv idx of" not in line and entityScope:
                    relation=find_between(line, "(", ")#")
                    if relation not in relDict.keys():
                        relDict[relation]=identifier
                        inRel=relation+"\t"+str(identifier)+"\n"
                        f.write(inRel)
                        identifier+=1
    with open("/disk/scratch_big/sweber/GCN-in/relDict.dat", "wb") as g:
        pickle.dump(relDict, g)
        
def constructGermanRelationDictionary():
    f=open("/disk/scratch_big/sweber/GCN-in/deRelDict","a")
    relDict={}
    identifier=700000
    
    for filename in os.listdir("/disk/scratch_big/sweber/outputPickles"):
        if filename.endswith("2VectorMap.dat"):
            print(filename)
            with open("/disk/scratch_big/sweber/outputPickles/"+filename, 'rb') as inF:
                vectorMap=pickle.load(inF)
                for pred in vectorMap.keys():
                    if pred not in relDict.keys():
                            relDict[pred]=identifier
                            idIn=str(identifier)+"\t"+pred+"\n"
                            f.write(idIn)
                            identifier+=1
                            
    with open("/disk/scratch_big/sweber/GCN-in/deRelDict.dat", "wb") as g:
        pickle.dump(relDict, g)
    
    
    
    
def constructEnglishEntityDict():
    #files to be written for GCN align
    filesList=[open("/disk/scratch_big/sweber/GCN-in/ent_ids_1", 'a'),open("/disk/scratch_big/sweber/GCN-in/training_attrs_1", 'a'),
               open("/disk/scratch_big/sweber/GCN-in/triples_1", 'a'), open("/disk/scratch_big/sweber/GCN-in/interlanguage", 'a')]
    
    englishEntDict={}
    relationsDict={}
    identifier=0
    identifierRels=3000000
    
    counter=0
    fileCounter=1
    
    for filename in os.listdir("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f"):
        with open("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f/"+filename, 'r') as inF:
            print("now in file ",filename, fileCounter, "of 355")
            fileCounter+=1
            entityScope=False
            for line in inF:
                if "inv idx of" in line:
                    entityScope=True
                    previousIdentifiers=[]
                    start = time.time()
                    doubleEnt=find_between(line, "inv idx of", " :")
                    enti=doubleEnt.split(sep="#")
                    for ent in enti:
                        ent=ent.lstrip()
                        ent=ent.title()
                        ent=ent.replace(" ", "_")
                        if ent=="":
                            continue
                        if ent not in englishEntDict.keys():
                            newDict={}
                            newDict["identifier"]=identifier
                            previousIdentifiers.append(identifier)
                            newDict["URI"]='http://dbpedia.org/resource/'+ent
                            newDict["attributes"]=getAttributesFomInternet(ent,"en")
                            newDict["germanLink"]=getGermanLink(ent)
                            englishEntDict[ent]=newDict
                            
                            #Write entity specific files here!
                            idIn=str(identifier)+"\thttp://dbpedia.org/resource/"+ent+"\n"
                            filesList[0].write(idIn)
                            attrIn='http://dbpedia.org/resource/'+ent+"\t"+'\t'.join(getAttributesFomInternet(ent,"en"))+"\n"
                            filesList[1].write(attrIn)
                            langIn='http://dbpedia.org/resource/'+ent+'\t'+getGermanLink(ent)+"\n"
                            filesList[3].write(langIn)
                            
                            
                            counter+=1
                            identifier+=1
                            if counter % 1000 == 0:
                                end = time.time()
                                print("1000 loop took", end - start)
                                start = time.time()
                                print("at ", counter, " of max 2.129.718")
                        else:
                            if ent!="":
                                otherIdentifier=englishEntDict[ent]["identifier"]
                                previousIdentifiers.append(otherIdentifier)
                        
                elif "inv idx of" not in line and entityScope:
                    #do relation stuff with previous identifiers here
                    #extract the relation
                    relation=find_between(line, "(", ")#")
                    if relation in relationsDict.keys():
                        relId=relationsDict[relation]
                    else:
                        relationsDict[relation]=identifierRels
                        relId=identifierRels
                        identifierRels+=1
                    relIn=""
                    try:
                        relIn=str(previousIdentifiers[0])+"\t"+str(relId)+"\t"+str(previousIdentifiers[1])+"\n"
                    except IndexError:
                        print("something went wrong with the previous identifier indexes")
                    filesList[2].write(relIn)
    with open("/disk/scratch/sweber/englishEntDict.dat", "wb") as f:
            pickle.dump(englishEntDict, f)
    return englishEntDict
        
        
    

def createAlphabetBatchesForInterlanguage():
    openFilesMap={}
    for x in list(string.ascii_lowercase):
        f = open("/disk/scratch_big/sweber/alphabetBatches/InterLanguage_"+str(x), 'a')
        f.write("")
        openFilesMap[str(x)]=f
        
    filePath="/disk/scratch_big/sweber/interlanguage_links_en.ttl"
    with open(filePath, 'r') as inF:
        for line in tqdm(inF, total=44122707, unit="lines"):
            if "http://de.dbpedia.org/resource/" in line:
                entity=find_between(line, "<http://dbpedia.org/resource/", ">")
                firstLetter=entity[0].lower()
                if firstLetter!="/" and firstLetter in openFilesMap.keys():
                    f = openFilesMap[firstLetter]
                    f.write(line)

                
                #print(line)

def createAlphabetBatchesForAttributes():
    print("HupHUP")
    openFilesMap={}
    for x in list(string.ascii_lowercase):
        f = open("/disk/scratch_big/sweber/alphabetBatches/Attribute_"+str(x), 'a')
        f.write("")
        openFilesMap[str(x)]=f
        print("done files")
        
    filePath="/disk/scratch_big/sweber/infobox_properties_de.ttl"
    with open(filePath, 'r') as inF:
        for line in tqdm(inF, total=14048417, unit="lines"):
            if "<http://de.dbpedia.org/resource/" in line:
                entity=find_between(line, "<http://de.dbpedia.org/resource/", ">")
                firstLetter=entity[0].lower()
                if firstLetter!="/" and firstLetter in openFilesMap.keys():
                    f = openFilesMap[firstLetter]
                    f.write(line)
    for f in openFilesMap.values():
        f.close
        
def lookUpInterlanguageLinks(inFile):
    f=open("/disk/scratch_big/sweber/GCN-in/interLang"+inFile[-3:],"a")
    
    with open(inFile, 'r') as inF:
            for line in inF:
                line=line.split("\t")
                ent=line[1]
                ent=find_between(ent, "http://dbpedia.org/resource/", "\n")
                germanLink=getGermanLink(ent)
                if germanLink!= "":
                    langIn='http://dbpedia.org/resource/'+ent+'\t'+getGermanLink(ent)+"\n"
                    f.write(langIn)

def lookUpAttributes(inFile):
    f=open("/disk/scratch_big/sweber/GCN-in/attribute"+inFile[-3:],"a")
    
    with open(inFile, 'r') as inF:
            for line in inF:
                line=line.split("\t")
                ent=line[1]
                ent=find_between(ent, "http://dbpedia.org/resource/", "\n")
                attributes=getAttributesFomInternet(ent,"en")
                if attributes!=[]:
                    attrIn='http://dbpedia.org/resource/'+ent+"\t"+'\t'.join(attributes)+"\n"
                    f.write(attrIn)
                    
def lookUpAttributesDe(inFile):
    f=open("/disk/scratch_big/sweber/GCN-in/deAttribute"+inFile[-5:],"a")
    
    with open(inFile, 'r') as inF:
        for line in inF:
            line=line.split("\t")
            ent=line[1]
            entity=find_between(ent, "http://de.dbpedia.org/resource/", "\n")
            if entity!="":
                attributes=getAttributesFromFile(entity)
                if attributes!=[]:
                    #print(attributes)
                    ent=ent[:-1]
                    attrIn='http://de.dbpedia.org/resource/'+ent+"\t"+'\t'.join(attributes)+"\n"
                    f.write(attrIn)
                    
def writeGermanTriples(inVectorMap):
    s=""
    for i in inVectorMap:
        if i.isupper():
            s+=i
    r=open("/disk/scratch_big/sweber/GCN-in/triples"+s,"a")
    
    #load entity dict
    with open("/disk/scratch_big/sweber/GCN-in/deEntDict.dat", "rb") as h:
        entDict=pickle.load(h)
    #load relation dict
    with open("/disk/scratch_big/sweber/GCN-in/deRelDict.dat", "rb") as g:
        relDict=pickle.load(g)
    
    try:
        with open(inVectorMap, "rb") as f:
            vectorMap=pickle.load(f)
    except FileNotFoundError:
        print("oopsy")
        return None

    entitySetAddress=inVectorMap[:-14]
    entitySetAddress=entitySetAddress+"germanEntitySet2.dat"
    print(entitySetAddress)
    try:
        with open(entitySetAddress, "rb") as e:
            entitySet=pickle.load(e)
    except FileNotFoundError:
        print("oopsy")
        return None
        
    for pred in vectorMap.keys():
        if pred in relDict.keys():
            relNumber=relDict[pred]
            values=vectorMap.get(pred)
            for tup in values:
                entityIndex=tup[0]
                #entitySet.printEntitySet()
                entityPiar=entitySet.getEntity(entityIndex)
                print(entityPiar)
                if entityPiar!=None:
                    enti=entityPiar.split("#")
                    identifiers=[]
                    for ent in enti:
                            ent=ent.lstrip()
                            ent=ent.title()
                            ent=ent.replace(" ", "_")
                            if ent=="":
                                continue
                            #look up entity in entity dict, 
                            identifier=entDict[ent]
                            identifiers.append(identifier)
                    if len(identifiers)==2:
                        inStr=str(identifiers[0])+"\t"+str(relNumber)+"\t"+str(identifiers[1])+"\n"
                        r.write(inStr)
                
                
    
    
def writeFileWithTriples():
    #load entity dict
    with open("/disk/scratch_big/sweber/GCN-in/entDict.dat", "rb") as h:
        entDict=pickle.load(h)
    #load relation dict
    with open("/disk/scratch_big/sweber/GCN-in/relDict.dat", "rb") as g:
        relDict=pickle.load(g)
        
    f=open("/disk/scratch_big/sweber/GCN-in/triplesss","a")
    
    for filename in os.listdir("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f"):
        with open("/disk/scratch_big/sweber/typed_rels_aida_figer_3_3_f/"+filename, 'r') as inF:
            print("now in file ",filename)
            entityScope=False
            for line in inF:
                if "inv idx of" in line:
                    entityScope=True
                    previousIdentifiers=[]
                    doubleEnt=find_between(line, "inv idx of", " :")
                    enti=doubleEnt.split(sep="#")
                    for ent in enti:
                        ent=ent.lstrip()
                        ent=ent.title()
                        ent=ent.replace(" ", "_")
                        if ent=="":
                            continue
                        #look up entity in entity dict, 
                        identifier=entDict[ent]
                        previousIdentifiers.append(identifier)
                elif "inv idx of" not in line and entityScope:
                    relation=find_between(line, "(", ")#")
                    if relation=="":
                        continue
                    relId=relDict[relation]
                    relIn=""
                    try:
                        relIn=str(previousIdentifiers[0])+"\t"+str(relId)+"\t"+str(previousIdentifiers[1])+"\n"
                    except IndexError:
                        print("something went wrong with the previous identifier indexes")
                    f.write(relIn)
                    
def createPartialInterlanguageMapping(inFile):
    with open("/disk/scratch_big/sweber/GCN-in/deEntDict.dat", "rb") as h:
        deEntDict=pickle.load(h)
    with open("/disk/scratch_big/sweber/GCN-in/entDict.dat", "rb") as i:
        enEntDict=pickle.load(i)
        
    f=open("/disk/scratch_big/sweber/GCN-in/numInterLang"+inFile[-3:],"a")
    
    with open(inFile, 'r') as inF:
        for line in inF:
            line=line.split("\t")
            englishLink=line[1]
            englishEnt=englishLink[28:]
            englishEnt=englishEnt.rstrip()
            if englishEnt=="":
                continue
            germanLink=getGermanLink(englishEnt)
            germanEnt=germanLink[31:]
            germanNumber= -100
            englishNumber= -100
            if germanEnt in deEntDict.keys():
                germanNumber=deEntDict[germanEnt]
            if englishEnt in enEntDict.keys():
                englishNumber=enEntDict[englishEnt]
            if germanNumber>0 and englishNumber>0:
                inStr=str(germanNumber)+"\t"+str(englishNumber)+"\n"
                f.write(inStr)
          
                    
def findStringOverlap():
    
    with open("/disk/scratch_big/sweber/GCN-in/deEntDict.dat", "rb") as h:
        deEntDict=pickle.load(h)
    with open("/disk/scratch_big/sweber/GCN-in/entDict.dat", "rb") as i:
        enEntDict=pickle.load(i)
    
    f=open("/disk/scratch_big/sweber/GCN-in/interLangStringMatch","a")
    numberList=[]    
    for de in deEntDict.keys():
        if de in enEntDict.keys():
            germanNumber=deEntDict[de]
            englishNumber=enEntDict[de]
            numberList.append(germanNumber)
            numberList.append(englishNumber)
            inStr=str(germanNumber)+"\t"+str(englishNumber)+"\n"
            f.write(inStr)
    for en in enEntDict.keys():
        if en in deEntDict.keys():
            germanNumber=deEntDict[en]
            englishNumber=enEntDict[en]
            if germanNumber not in numberList and englishNumber not in numberList:
                inStr=str(germanNumber)+"\t"+str(englishNumber)+"\n"
                f.write(inStr)

def changeNamespace():
    """
    f=open("/disk/scratch_big/sweber/GCN-Align/data/de_en/ent_ids_11", "a")
    with open("/disk/scratch_big/sweber/GCN-Align/data/de_en/ent_ids_1","r") as inFile:
        for line in inFile:
            splitLine=line.split("\t") 
            number=int(splitLine[0])
            newNumber=number-32085
            f.write(str(newNumber)+"\t"+splitLine[1])
    """
    g=open("/disk/scratch_big/sweber/GCN-Align/data/de_en/triples_11", "a")
    with open("/disk/scratch_big/sweber/GCN-Align/data/de_en/leftovers/triples_1","r") as inFile:
        for line in inFile:
            splitLine=line.split("\t") 
            number=int(splitLine[0])
            newNumber1=number-166042
            newNumber2=int(splitLine[2])-166042
            g.write(str(newNumber1)+"\t"+splitLine[1]+"\t"+str(newNumber2)+"\n")
    """        
    h=open("/disk/scratch_big/sweber/GCN-Align/data/de_en/ref_ent_ids11","a")
    with open("/disk/scratch_big/sweber/GCN-Align/data/de_en/ref_ent_ids","r") as inFile:
        for line in inFile:
            splitLine=line.split("\t") 
            number=int(splitLine[0])
            newNumber=number-32085
            h.write(str(newNumber)+"\t"+str(splitLine[1]))
    """ 
    
def removeUselessMistakeIMadeInThatAttributeFile():
    f=open("/disk/scratch_big/sweber/GCN-Align/data/de_en/ACTUALtraining_attributes_1","a")
    with open("/disk/scratch_big/sweber/GCN-Align/data/de_en/training_attrs_1","r") as file:
        for line in file:
            lineN=line[31:]
            f.write(lineN)
            
def tagBilingualInTriples(inFileEn, inFileDe):
    germanEnglishDict={}
    f=open("/disk/scratch_big/sweber/bilingualTriples.txt","a")
    with open(inFileEn) as file:
        for line in file:
            newLine=[0,0,0]
            elements=line.strip().split("\t")
            count=0
            for el in elements:
                if count !=1:
                    germanLink=getGermanLink(el)
                    if germanLink!="":
                        germanEnglishDict[germanLink[31:]]=el
                        newLine[count]=str(el)+"::bi"
                    else:
                        newLine[count]=str(el)+"::en"
                else:
                    newLine[count]=str(el)+"::en"
                count+=1
        
            for n, i in enumerate(newLine):
                if isinstance(i,int):
                    newLine[n]=str(i) 
            f.write("\t".join(newLine)+"\n")
            print("\t".join(newLine)+"\n")
    
    with open(inFileDe) as otherFile:
        for line in otherFile:
            newLine=[0,0,0]
            elements=line.strip().split("\t")
            count=0
            for el in elements:
                if count !=1:
                    if el in germanEnglishDict.keys():
                        newLine[count]=str(germanEnglishDict(el))+"::bi"
                    else:
                        newLine[count]=str(el)+"::de"
                else:
                    newLine[count]=str(el)+"::de"
                count+=1 
            
            for n, i in enumerate(newLine):
                if isinstance(i,int):
                    newLine[n]=str(i)
            f.write("\t".join(newLine)+"\n")
            print("\t".join(newLine)+"\n")
                                

def tagBilingualInTriplesEN(inFileEn):
    f=open("/disk/scratch_big/sweber/bilingualTriples"+inFileEn[-4:]+".txt","a")
    with open(inFileEn) as file:
        for line in file:
            newLine=[0,0,0]
            elements=line.strip().split("\t")
            count=0
            for el in elements:
                if count !=1:
                    germanLink=getGermanFromDict(el)
                    if germanLink!="":
                        newLine[count]=str(el)+"::bi"
                    else:
                        newLine[count]=str(el)+"::en"
                else:
                    newLine[count]=str(el)+"::en"
                count+=1
        
            for n, i in enumerate(newLine):
                if isinstance(i,int):
                    newLine[n]=str(i) 
            f.write("\t".join(newLine)+"\n")
            
def tagBilingualInTriplesDE(inFileDe):
    with open("/disk/scratch_big/sweber/GraphAlignment/stringDictDeEn.tsv", 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        decode = {r[0]: r[1] for r in reader}
    
    g=open("/disk/scratch_big/sweber/bilingualTriplesDE"+inFileDe[-4:]+".txt","a")
    
    with open(inFileDe) as otherFile:
        for line in otherFile:
            newLine=[0,0,0]
            elements=line.strip().split("\t")
            count=0
            for el in elements:
                if count !=1:
                    if el in decode.keys():
                        newLine[count]=str(decode(el))+"::bi"
                    else:
                        newLine[count]=str(el)+"::de"
                else:
                    newLine[count]=str(el)+"::de"
                count+=1 
            
            for n, i in enumerate(newLine):
                if isinstance(i,int):
                    newLine[n]=str(i)
            g.write("\t".join(newLine)+"\n")
            print("\t".join(newLine)+"\n")
    
def createStringDict():
    with open("/disk/scratch_big/sweber/GCN-in/entDict.dat", "rb") as f:
                englishDict1=pickle.load(f)
                
    with open("/disk/scratch_big/sweber/GCN-in/deEntDict.dat", "rb") as g:
                germanDict1=pickle.load(g)
    
    h=open("stringDictDeEn.txt","a")
    
    germanDict = {v: k for k, v in germanDict1.items()}
    englishDict = {v: k for k, v in englishDict1.items()}
    
    with open("/disk/scratch_big/sweber/GCN-in/combinedInterLangNum","r") as inFile:
        for line in inFile:
            splitted=line.split("\t")
            first=splitted[0]
            german=germanDict[int(first)]
            second=splitted[1]
            english=englishDict[int(second)]
            print(german,"\t",english)
            h.write(german+"\t"+english+"\n")
    

if __name__ == "__main__":
    
    
    #tagBilingualInTriples("/disk/scratch_big/sweber/entGraph/typed_rels_aida_figer_3_3_fEnglish/allTuples_ptyped_uniqueEnglish.txt", "/disk/scratch_big/sweber/entGraph/justRels/allTuples_ptyped_uniqueGermanOnlyTest.txt")
    inFile=sys.argv[1]
    tagBilingualInTriplesEN(inFile)
    
    #removeUselessMistakeIMadeInThatAttributeFile()
    #changeNamespace()
    #constructEnglishEntityDict()
    #createAlphabetBatchesForAttributes()
    #constructEnglishEntityDict()
    #constructRelationDictionary()
    
    #inFile=sys.argv[1]
    #lookUpAttributesDe(inFile)
    #writeGermanTriples(inFile)
    #createPartialInterlanguageMapping(inFile)
    #getGermanLink("Zhengzhou")
    
    #findStringOverlap()
    
    #writeFileWithTriples()
    #constructRelationDictionary()
    #constructGermanRelationDictionary()

    """
    for entity in ["Wheat","Spelt","Rye","Corn","Yo_Mamma"]:
        
        getAttributesFomInternet(entity, "en")
    print("-------------------------------")
    for entity in ["Weizen","Angela_Merkel","Barack_Obama","Obama"]:
        getAttributesFromFile(entity)
    """
    