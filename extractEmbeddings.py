import numpy as np

if __name__ == "__main__":
    data = np.load('/disk/scratch_big/sweber/ent_embeddings.npy')
    print(data.shape)
    entities_dict = pickle.load( open( "/disk/scratch_big/sweber/entities_dict.p", "rb" ) )
    print(entities_dict)
    