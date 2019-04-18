import networkx as nx
import sys
import matplotlib.pyplot as plt
import os

if __name__ == "__main__":
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
                elif "lambda" in line and passedLambda:
                    E=nx.connected_components(G)
                    f=open("/disk/scratch_big/sweber/entGraph/justGraphs/"+filename+str(lambdaVal),"a")
                    for n in E: 
                        #print("-----------------------------------")
                        f.write("\n-------------------------\n")
                        for number in n:
                            #print(G.node[number])
                            f.write(str(G.node[number])+"\n")
                    G = nx.Graph()
                    lambdaVal=line[8:12]
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
                    if line!="\n":
                        G.node[number][name]=line
                elif "component" not in line and passedComponent and line!="" and "=>" in line: 
                    lineSplit=line.split()
                    component=lineSplit[1]
                    G.add_edge(number, component)
                elif line=="":
                    passedComponent=False
                    
                
        #nx.draw_networkx_edges(n,pos=nx.spring_layout(n))
        #plt.show()
                
                