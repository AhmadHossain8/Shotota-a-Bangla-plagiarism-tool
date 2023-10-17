from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from transformers import logging, AutoTokenizer, AutoModel
import os
import re
import string, re
import time
import torch
import random
import numpy
from numpy import dot

corpus_file = 'C:\\Users\\Rashidul\\Desktop\\2604856_corpus_part25.txt'
sentence_pattern = r"([।!?])"

with open(corpus_file, encoding="utf-8") as f:
    corpus = f.read().replace('\n',' ').replace('\n\n',' ')

sentences = re.split(sentence_pattern, corpus)
temp = []
for i in range(len(sentences)):
    if len(sentences[i]) > 1:
        temp.append(sentences[i])

pre_sentences = []
bangla_sentences = []
for i in range(len(temp)):
    if len(temp[i]) > 0:
        new_x = ""
        for j in range(len(temp[i])):
            unicode_val = ord(temp[i][j]) 
            if (0x0980 <= unicode_val <= 0x09FF):
                new_x += temp[i][j]
            elif temp[i][j] == ' ':
                if len(new_x) > 0 and new_x[len(new_x)-1] != ' ':
                    new_x += temp[i][j]

        if len(new_x) > 0:
            new_x = new_x.lstrip(" ")
            new_x = new_x.rstrip(" ")
            bangla_sentences.append(new_x)

print("Total Bangla Sentences {}".format(len(bangla_sentences)))


tokenizer = AutoTokenizer.from_pretrained("sagorsarker/bangla-bert-base")
model = AutoModel.from_pretrained("sagorsarker/bangla-bert-base")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)


batch_size = 1
max_length = 512

main_emb = []  # reset the main_emb list
lol = 0
for i in range(0, len(bangla_sentences), batch_size):
    
    # Create the inputs tensor
    batch_sentences = bangla_sentences[i:i+batch_size]
    inputs_list = [tokenizer(s, padding=True, truncation=True, max_length=max_length, return_tensors='pt').to(device) for s in batch_sentences]
    input_ids = torch.cat([x['input_ids'] for x in inputs_list], dim=0)

    # Get the outputs from the model
    outputs = model(input_ids=input_ids)

    # Get the sentence embeddings by taking the average of the token embeddings
    token_embeddings = outputs.last_hidden_state.to(device)
    sentence_embeddings = token_embeddings.mean(dim=1)
    main_emb.extend(sentence_embeddings.cpu().detach().numpy())
    lol = lol+1
    print(lol)
    # Clear the GPU memory
    del inputs_list, input_ids, outputs, token_embeddings, sentence_embeddings


print("Total embed Sentences {}".format(len(main_emb)))

#qdrant part

_COLLECTION_NAME = "my_data"
qdrant =  QdrantClient(path="H:\\Qdrant")

qdrant.recreate_collection(
    collection_name=_COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size= 768, # Vector size is defined by used model
        distance=models.Distance.COSINE
    )
)

qdrant.upload_records(
    collection_name=_COLLECTION_NAME,
    records=[
        models.Record(
            id=idx,
            vector= sentence.tolist(),
            payload={ "org_sentence" : bangla_sentences[idx] }
        ) for idx, sentence in enumerate(main_emb)
    ]
)

