    #!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard
from itertools import chain
from itertools import product
from collections import OrderedDict
import pickle
from pygermanet.germanet import load_germanet

    
 
def get_modifiers_to_verb(self, dt, i, mods):
    """
    Get open clausal components of the verb (i.e. the predicate)
    Look for the "xcomp" dependency
    """
    if 'xcomp' in dt.nodes[i]['deps']:
        l = dt.nodes[i]['deps']['xcomp']
        for n in l:
            #if dt.nodes[n]['tag'] != 'PTKNEG':
            if dt.nodes[n]['tag'] == 'VVINF':
                mods.append(n)
                mods = self.get_modifiers_to_verb(dt, n, mods)
    return mods

def checkForSeinPlusObject(self, dt, ent1, ent2):
    pred_string=""
    pred_index=dt.nodes[int(ent1['starttok'])]['head']
    if ("cop" in dt.nodes[pred_index]['deps'].keys()) and ("nmod" in dt.nodes[pred_index]['deps'].keys() or "advmod" in dt.nodes[pred_index]['deps'].keys()):
        copulaWordIndex=dt.nodes[pred_index]['deps']['cop']
        if "nmod" in dt.nodes[pred_index]['deps'].keys():
            nmodWordIndex=dt.nodes[pred_index]['deps']['nmod']
        elif "advmod" in dt.nodes[pred_index]['deps'].keys():
            nmodWordIndex=dt.nodes[pred_index]['deps']['advmod']
        if dt.nodes[copulaWordIndex[0]]["lemma"]== "sein":
            for i in nmodWordIndex:
                if int(i)==int(ent2['starttok']):
                    caseAttachment=self.get_case_attachment(dt, ent2)
                    pred_string=dt.nodes[pred_index]['lemma']+"_sein"+caseAttachment
    return pred_string, pred_index

def get_case_attachment(self,dt,ent2):
    if "case" in dt.nodes[int(ent2['starttok'])]['deps'].keys():
        for i in dt.nodes[int(ent2['starttok'])]['deps']['case']:
            return "_"+dt.nodes[i]["lemma"]
    return""

def checkForHabenPlusObject(self, dt, ent1, ent2):
    pred_string=""
    pred_index=dt.nodes[int(ent1['starttok'])]['head']
    if "obj" in dt.nodes[pred_index]['deps'].keys():
        predDependencies=dt.nodes[pred_index]['deps']['obj']
        for node in dt.nodes:
            if (node in predDependencies) and dt.nodes[node]['ctag']=='NOUN' and ('nmod' in dt.nodes[node]['deps'].keys()):
                nounDependencies=dt.nodes[node]['deps']['nmod']
                pred_string = dt.nodes[pred_index]['lemma']
                ent2Dependencies=dt.nodes[int(ent2['starttok'])]['deps']
                if (int(ent2['starttok']) in nounDependencies) and pred_string=="haben" and ('case' in ent2Dependencies):
                    caseAttachment=self.get_case_attachment(dt, ent2)
                    pred_string+="_"+dt.nodes[node]['lemma']+caseAttachment
    return pred_string, pred_index
    
    
def get_predicate(dt, ent1, ent2):
    """
    Get the predicate that links the two entities
    """
    pred_string = ''
    pred_index = -1
    passive = False
    with open("/disk/scratch_big/sweber/GraphAlignment/verbMap.dat", "rb") as f:
        verbMap=pickle.load(f)
    #new1=""
    #new2=""
    ent1rel = dt.nodes[int(ent1['starttok'])]['rel']
    #if ent1rel not in ['nsubj', 'nsubj:pass','dep']:
        #new1=self.checkOtherWordsInNamedEntity1(ent1,dt)
    #if new1 != "":
        #ent1rel, ent1=new1
    ent2rel = dt.nodes[int(ent2['starttok'])]['rel']
    #if ent2rel not in ['obj', 'obl','dep']:
        #new2=self.checkOtherWordsInNamedEntity1(ent2,dt)
    #f new2 != "":
        #ent2rel, ent2=new2
    if ent1rel in ['nsubj', 'nsubj:pass','dep'] and ent2rel in ['obj', 'obl','dep']:
        if ent1rel == 'nsubj:pass':
            passive = True
        ent1head = dt.nodes[int(ent1['starttok'])]['head']
        ent2head = dt.nodes[int(ent2['starttok'])]['head']
        ent2headhead = dt.nodes.get(ent2head)['head']
        ent2headrel= dt.nodes.get(ent2head)['rel']
        if ent1head == ent2head or (ent2headhead == ent1head and ent2headrel == 'xcomp'):
            pred_string = dt.nodes[ent1head]['lemma']
            pred_index = ent1head
            # Check if predicate is a particle verb
            if 'compound:prt' in dt.nodes[ent1head]['deps']:
                for prt in dt.nodes[ent1head]['deps']['compound:prt']:
                    pred_string += '_' + dt.nodes[prt]['lemma']
            #checking for light verb constructions in verb map goes here
            if pred_string in verbMap.keys():
                thesePPandN=[]
                predDependencies=dt.nodes[pred_index]['deps'].values()
                predDependencies = [y for x in predDependencies for y in x]
                for node in dt.nodes:
                    if node in predDependencies and dt.nodes[node]['ctag']=='NOUN' and ('case' in dt.nodes[node]['deps'].keys()):
                        prepLoc=int(dt.nodes[node]['deps']['case'][0])
                        prep=dt.nodes[prepLoc]['lemma']
                        noun=dt.nodes[node]['lemma']
                        PPandN=prep+" "+noun
                        thesePPandN.append(PPandN.encode('utf-8'))
                lst = [value for value in thesePPandN if value in verbMap[pred_string]] 
                if len(lst)>0:
                    ppn=lst[0]
                    ppn=ppn.replace(" ","_")
                    pred_string+="_"+ppn.decode('utf-8')
            # Add modifiers to verbs
            mods = get_modifiers_to_verb(dt, pred_index, [])
            for mod in mods:
                pred_string += '.' + dt.nodes[mod]['lemma']
            # Add prepositions
            if 'case' in dt.nodes[ent2['starttok']]['deps']:
                for prep in dt.nodes[ent2['starttok']]['deps']['case']:
                    pred_string += '.' + dt.nodes[prep]['lemma']
    #this is where I check for object attachment
    elif (ent1rel in ['nsubj', 'nsubj:pass','dep']) and (ent2rel in ['nmod']):
        if pred_string=="":
            pred_string, pred_index = checkForHabenPlusObject(dt, ent1, ent2)
        if pred_string=="":
            pred_string, pred_index = checkForSeinPlusObject(dt, ent1, ent2)
    return (pred_string, pred_index, passive)