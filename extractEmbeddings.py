import numpy as np
import pickle
from numpy import vstack,array,savetxt
from scipy.cluster.vq import kmeans,vq
import collections
from annoy import AnnoyIndex
import random


if __name__ == "__main__":
    rel_embeddings = np.load('/disk/scratch_big/sweber/ent_embeddings.npy')
    print(rel_embeddings.shape)
    relations_dict = pickle.load( open( "/disk/scratch_big/sweber/entities_dict.p", "rb" ) )
    print("Length : %d" % len(relations_dict))
    #print(entities_dict)"\t"
    reversed_relations_dict = dict((v,k) for k,v in relations_dict.items())
    
    f = 200
    
    t = AnnoyIndex(f)  # Length of item vector that will be indexed
    for i in range(226690):
        v = rel_embeddings[i]
        t.add_item(i, v)
    print("done adding")
    t.build(100) 
    t.save('testEnt.ann')
    
    u = AnnoyIndex(f)
    u.load('testEnt.ann') # super fast, will just mmap the file
    for i in range(200000,200100):
        nns=u.get_nns_by_item(i, 100)
        print("-------",reversed_relations_dict[i],"-------")
        for n in nns:
            if "::en" in reversed_relations_dict[n] or "::bi" in reversed_relations_dict[n]:
                print(reversed_relations_dict[n])
    
    
    """
    np.savetxt("ent_embeddings.tsv",ent_embeddings,delimiter="\t")
    f=open("entities_dict.tsv", "a")
    sorted_x = sorted(entities_dict.items(), key=lambda kv: kv[1])
    sorted_dict = collections.OrderedDict(sorted_x)
    for k, v in sorted_dict.items():
        f.write(k+"\n")
    """
    
    