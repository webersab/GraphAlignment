import networkx as nx
import sys
import matplotlib.pyplot as plt
import os

def constructGraphFromFile(filename,lambdaValue):
    G = nx.Graph()
    counter=0
    passedComponent=False
    passedRightLambda=False
    
    with open("/disk/scratch_big/sweber/entGraph/justGraphs/"+filename, 'r') as inF:
            number=-100
            for line in inF:
                if "lambda" in line and str(lambdaValue)==line[8:12]:
                    G = nx.Graph()
                    passedComponent=False
                    passedRightLamda=True
                    firstLine=line
                elif "lambda" in line and passedRightLambda:
                    E=nx.connected_components(G)
                    return E
                elif "component" in line and passedRightLambda:
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

def constructPrintoutsFromFile():
    #filename=sys.argv[1]
    #filename="/group/project/s1782911/EVENT#LOCATION_sim_HTLFRG"
    print("hup hup")
    f=open("/group/project/s1782911/deEntPrintout","a")

    G = nx.Graph()
    counter=0
    passedComponent=False
    passedLambda=False
    lambdaVal=0
    
    for filename in os.listdir("/disk/scratch_big/sweber/entGraph/justGraphs"):
        with open("/disk/scratch_big/sweber/entGraph/justGraphs/"+filename, 'r') as inF:
            number=-100
            for line in inF:
                if "lambda" in line and not passedLambda:
                    G = nx.Graph()
                    lambdaVal=line[8:12]
                    passedLambda=True
                    passedComponent=False
                    firstLine=line
                elif "lambda" in line and passedLambda:
                    E=nx.connected_components(G)
                    f=open("/disk/scratch_big/sweber/entGraph/justGraphs/"+filename+str(lambdaVal),"a")
                    f.write(firstLine)
                    for n in E: 
                        #print("-----------------------------------")
                        f.write("\n-------------------------\n")
                        for number in n:
                            #print(G.node[number])
                            f.write(str(G.node[number])+"\n")
                            f.write(str(G.edges(number))+"\n")
                    G = nx.Graph()
                    lambdaVal=line[8:12]
                    passedComponent=False
                    firstLine=line
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
                    
                
        #nx.draw_networkx_edges(n,pos=nx.spring_layout(n))
        #plt.show()
    

if __name__ == "__main__":
    print("Hup hup graph Construct!")
    E = constructGraphFromFile("EVENT#LOCATION_sim_HTLFRG",0.07)
    for a in E:
        print(a)
                
                