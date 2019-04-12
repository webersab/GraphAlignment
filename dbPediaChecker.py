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
    filePath="/disk/scratch_big/sweber/infobox_properties_de.ttl"
    propUrl='http://de.dbpedia.org/property/'
    toFind='<http://de.dbpedia.org/resource/'+entity+">"
    
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
                if "http://dbpedia.org/resource/"+entity in line and "http://de.dbpedia.org/resource/" in line:
                    link=find_between(line, "http://de.dbpedia.org/resource/", "> .")
                    link="http://de.dbpedia.org/resource/"+link
                    return link
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
    f=open("/disk/scratch_big/sweber/GCN-in/relDict","a")
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
    """
    with open(inFile, 'r') as inF:
        print("processing file ",inFile)
        for line in tqdm(inF, total=500, unit="lines"):
                line=line.split("\t")
                ent=line[1]
                entity=find_between(ent, "http://de.dbpedia.org/resource/", "\n")
                if entity!="":
                    attributes=getAttributesFromFile(entity)
                    #print(attributes)
                    if attributes!=[]:
                        #print(attributes)
                        attrIn='http://dbpedia.org/resource/'+ent+"\t"+'\t'.join(attributes)+"\n"
                        f.write(attrIn)
    """
    
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

if __name__ == "__main__":
    #constructEnglishEntityDict()
    #createAlphabetBatchesForAttributes()
    #constructEnglishEntityDict()
    #constructRelationDictionary()
    
    inFile=sys.argv[1]
    lookUpAttributesDe(inFile)
    
    #writeFileWithTriples()
    #constructGermanRelationDictionary()

    """
    for entity in ["Wheat","Spelt","Rye","Corn","Yo_Mamma"]:
        
        getAttributesFomInternet(entity, "en")
    print("-------------------------------")
    for entity in ["Weizen","Angela_Merkel","Barack_Obama","Obama"]:
        getAttributesFromFile(entity)
    """
    