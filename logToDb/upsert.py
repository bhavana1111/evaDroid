from helperFn import meta_data_list,embedding
from pinecone.grpc import PineconeGRPC as Pinecone
import json


def truncate_metadata(meta, max_size=40960, max_str_len=1000):
    """Return original meta if under limit, else return truncated version."""
    try:
        if len(json.dumps(meta).encode("utf-8")) <= max_size:
            return meta
    except Exception:
        pass  # fallback to truncation if serialization fails

    return {
        k: (v[:max_str_len] if isinstance(v, str) and len(v) > max_str_len else v)
        for k, v in meta.items()
        if isinstance(v, (str, int, float, bool))  # keep only simple safe types
    }

pc=Pinecone(api_key="fbff3bf2-dc8a-4a8c-ab9c-8e6db70b513a")
index=pc.Index("evaindex")
vectors_list=[]
for i in range(0,len(meta_data_list)):
    vector={}
    vector["id"]=meta_data_list[i]['app_name']+meta_data_list[i]['type']+str(i+1)
    vector["values"]=embedding[i]
    vector["metadata"]=truncate_metadata(meta_data_list[i])
    vectors_list.append(vector)
print(len(vectors_list[0]["values"]))
index.upsert(vectors=vectors_list,namespace='travel')
# ids_list=[f"ExpediaRandom{i}" for i in range(1, 700)]
# index.delete(ids=ids_list, namespace='travel')
# print("from upsert py",len(meta_data_list))
# print("from upsert embedding len",len(embedding[0][0]))