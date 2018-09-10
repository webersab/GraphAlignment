

import sys
#import pprint
#from Cython.Compiler.ExprNodes import inc_dec_constructor

#reload(sys)  
#sys.setdefaultencoding('utf8')

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


if __name__ == "__main__":
#Find the predicates
    print("Hello preprocessor!")
    filePath = '/afs/inf.ed.ac.uk/user/s17/s1782911/allTheOptuptDedup.txt'
    inFile = open(filePath,'r')
    print("open file ",inFile)
    dicto = {}
    for line in inFile:
        if ("(" in line):
            word = find_between(line,"(",")#location#location")
            if word in dicto:
                value = dicto.get(word)
                dicto[word] = value+1
            else:
                dicto[word] = 1

# Eliminate long tail:
#    for a,b in dict.items():
#        if b<4:
#            del dict[a]
    numOfPreds= len(dicto)-1
    tuples = dicto.items()
    d = {}
    
    for tup in tuples:
        filePath = '/afs/inf.ed.ac.uk/user/s17/s1782911/allTheOptuptDedup.txt'
        inFile = open(filePath,'r')
        print("open file",inFile)
        dict2 = {}
        for line in inFile:
            if ("|||" in line):
                word = find_between(line,"("+tup[0]+")#location#location::","|||")
                if word in dict2:
                    value = dict2.get(word)
                    dict2[word] = value+1
                else:
                    dict2[word] = 1   
        d[tup] = {}
        for key, value in dict2.items():
            d[tup][key] = value
    print("second dict done")
    
    invIdxDict = {}
    for x,y in d.items():
        print("x:")
        print(x)
        print("y:")
        print(y)
        if '' in y:
            del y['']
        if bool(y):
            for o in y.items():
                if o[0] in invIdxDict:
                    #print("case 2.1")
                    #print("o[0]:")
                    #print(o[0])
                    listo = invIdxDict.get(o[0])
                    listo.append(x)
                    invIdxDict[o[0]] = listo
                    #print(list)
                else:
                    #print("case 2.2")
                    #print("o[0]:")
                    #print(o[0])
                    listo = []
                    listo.append(x)
                    invIdxDict[o[0]] = listo
                    #print(list)
           
#Printing happens here:
    orig_stdout = sys.stdout
    f = open('allThePipelinOut.txt', 'w')
    sys.stdout = f
    print("types: location#location, num preds: "+str(numOfPreds))

    for key, value in d.items():
        if '' in y:
            del value['']
        #s = unicode(key[0]).decode('utf-8')
        #f.write(s)
        print("predicate: ("+key[0]+")#location#location")
        for v, k in value.items():
            v=v.replace("::","#")
            print(v+": "+str(k))
        print("\n")
    
    for key, value in invIdxDict.items():
        k = key
        k=k.replace("::","#")
        print("inv idx of "+k+" :"+str(len(value)))
        for v in value:
            print("(" + v[0]+")#location#location")
    
    sys.stdout = orig_stdout
    f.close()

