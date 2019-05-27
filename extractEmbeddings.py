import numpy as np
import pickle
from numpy import vstack,array,savetxt
from scipy.cluster.vq import kmeans,vq
import collections
from annoy import AnnoyIndex


if __name__ == "__main__":
    ent_embeddings = np.load('/disk/scratch_big/sweber/rel_embeddings.npy')
    print(ent_embeddings.shape)
    entities_dict = pickle.load( open( "/disk/scratch_big/sweber/relations_dict.p", "rb" ) )
    print("Length : %d" % len(entities_dict))
    #print(entities_dict)"\t"
    
    """
    f = 200
    t = AnnoyIndex(f)  # Length of item vector that will be indexed
    for i in xrange(1000):
        v = [random.gauss(0, 1) for z in xrange(f)]
        t.add_item(i, v)

        t.build(10) # 10 trees
        t.save('test.ann')
    
    
    
    np.savetxt("ent_embeddings.tsv",ent_embeddings,delimiter="\t")
    f=open("entities_dict.tsv", "a")
    sorted_x = sorted(entities_dict.items(), key=lambda kv: kv[1])
    sorted_dict = collections.OrderedDict(sorted_x)
    for k, v in sorted_dict.items():
        f.write(k+"\n")
    """
    
    #centroids,_ = kmeans(ent_embeddings,50000)
    #idx,_ = vq(data,centroids)
    
    #print(idx)
    
    