#this files will take the test result logs and convert them into tuples
#Which will be used as an input for the embeddings 
#sentence transformer is used here


from sentence_transformers import SentenceTransformer

def convertingToVector(data):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings=model.encode(data)
    print(embeddings.shape)
    similarities=model.similarity(embeddings,embeddings)
    print(similarities)
