
from qdrant_client import models, QdrantClient
import pickle

file = open('9116996_corpus_part1.pkl', 'rb')
main_emb = pickle.load(file)

print(len(main_emb))

_COLLECTION_NAME = "Base"
qdrant =  QdrantClient(path="H:\\Qdrant")

qdrant.recreate_collection(
    collection_name=_COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size= 768, # Vector size is defined by used model
        distance=models.Distance.COSINE
    )
)
print("done")
qdrant.upload_records(
    collection_name=_COLLECTION_NAME,
    records=[
        models.Record(
            id=idx,
            vector= sentence.tolist(),
        ) for idx, sentence in enumerate(main_emb)
    ]
)
print("done")


search_queries = []
for i in range(len(main_emb)):
    search_queries.append(models.SearchRequest(
        vector=main_emb[i].tolist(),
        with_payload=True,
        limit=3
    ))

hits = qdrant.search_batch(
    collection_name=_COLLECTION_NAME,
    requests=search_queries
)

for i in enumerate(hits):
    for scored_point in i[1]:
        print("ID:", scored_point.id)
        print("Version:", scored_point.version)
        print("Score:", scored_point.score)
        print("Payload:", scored_point.payload)
        print("Vector:", scored_point.vector)

for i in range(len(main_emb)):
    hits = qdrant.search(
        collection_name=_COLLECTION_NAME,
        query_vector= main_emb[i].tolist(),
        limit=3
    )
    for hit in hits:
        print(hit.payload, "score:", hit.score)