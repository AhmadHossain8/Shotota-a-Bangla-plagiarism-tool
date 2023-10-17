from http import client
import re
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import logout as auth_logout
from qdrant_client import models, QdrantClient
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from transformers import logging, AutoTokenizer, AutoModel
from django.contrib.auth import logout
from django.http import JsonResponse
import os
import re
import string, re
import time
import torch
import random
import numpy
from numpy import dot
import json
from bs4 import BeautifulSoup
from googlesearch import search
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
import pdfkit 
import docx2txt
import pdfplumber
from django.contrib.auth.decorators import login_required
from plagiarism.models import UploadFile



Sentences = []
bangla_sentences = []# Store preprocessed sentences
viewsen = []
inputsen = []
progress = 70
arr=[]
word=0
character=0
button=""
alert=""
plagScore=0
uniqueScore=0
count=0
flag = 0
tempDict = {}
temp_sen = []
count1 = 0
search_results = []
temp = []

result = {'sentence' : [] , 'source' : [],'value':[]}

def Profile(request):
    global plagScore
    global uniqueScore
    plagScore = 0
    uniqueScore = 0
    args = {
        'uniqueScore':uniqueScore,
        'plagScore':plagScore,   
    }
    return render(request, 'home.html', args)

def login(request):
    auth_logout(request)
    return render(request,'index.html')

def InputText(request):
    global viewsen, bangla_sentences,button, alert,uniqueScore,plagScore
    viewsen =[]
    bangla_sentences = []
    if request.method == 'POST':
        print("response")
        text = request.POST.get('input_text', '')
        input_file = request.FILES.get('input_file')
        if input_file:
            file_extension = input_file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                text = ""
                with pdfplumber.open(input_file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text()
    
                
            elif file_extension  == 'docx':
                doc_text = docx2txt.process(input_file)
                
                text = doc_text

            elif file_extension  == 'txt':

                text = input_file.read().decode('utf-8')
                print("response")
    print(text)
    p = Preprocess(text)
    s = scrape(text, num_results=1)
    e = embedding(p)
    print(type(e))
    search_q(e,p)
    global word,character,arr
    global count, flag
    global search_results
    # for circular bar
    if count>0:
        plagScore = (count/len(viewsen))*100
        plagScore = round(plagScore, 2)
        uniqueScore = 100 - plagScore
        uniqueScore = round(uniqueScore, 2)
        print(plagScore)
        print(uniqueScore)
    elif count == 0:
        plagScore = 0
        uniqueScore = 0
    else:
        plagScore = 0
        uniqueScore = 0

    sentences = bangla_sentences

    print(button)
    print(search_results)
    args = {
        'text': bangla_sentences, 
        'sentences': sentences, 
        'word':word,
        'character':character, 
        'prog':progress,
        'dprog':(100-progress),
        'button':button,
        'uniqueScore':uniqueScore,
        'viewsen':viewsen,
        'plagScore':plagScore,
        'search_results':search_results,
    }
    print(args)
    return JsonResponse(args)



def Preprocess(text):
    global arr,word,character
    word=0
    character=0
    sentence_pattern = r'[^।!?]+[।!?]'
    global temp
    # Split the content into sentences using the defined pattern
    sentences = re.findall(sentence_pattern, text)


    print("Sentence")
    print(sentences)
    for i in range(len(sentences)):
        if len(sentences[i]) > 1:
            temp.append(sentences[i])
            
            
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
    #arr = [[bangla_sentences[i],"-", random.randint(0, 1)] for i in range(len(bangla_sentences))]       
    for sentence in bangla_sentences:
        words = sentence.split()
        word += len(words)
        character += len(sentence)
    #arr = [[bangla_sentences[i],"-", random.randint(0, 1)] for i in range(len(bangla_sentences))]
    #for i in range(len(bangla_sentences)):
       #bangla_sentences[i] = re.sub(sentence_pattern, '', bangla_sentences[i])

    return bangla_sentences
    


def embedding(bangla_sentences):
    
    tokenizer = AutoTokenizer.from_pretrained("sagorsarker/bangla-bert-base")
    model = AutoModel.from_pretrained("sagorsarker/bangla-bert-base")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    batch_size = 1
    max_length = 512

    main_emb = []  # reset the main_emb list
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

        # Clear the GPU memory
        del inputs_list, input_ids, outputs, token_embeddings, sentence_embeddings
    return main_emb

def scrape(bangla_sentences, num_results=1):
    global search_results
    
    try:
        count = 0
        delay = 5
        
        time.sleep(delay)
        for result in search(bangla_sentences, num_results=num_results):
            search_results.append(result)
            count += 1
            if count >= num_results:
                break
    except Exception as e:
        print("An error occurred:", str(e))
    
    return None

def search_q(main_emb, bangla_sen):
  
    _COLLECTION_NAME = "my_books"
    qdrant =  QdrantClient(path="H:\\Qdrant")
    search_queries = []
    for i in range(len(main_emb)):
        search_queries.append(models.SearchRequest(
        vector=main_emb[i].tolist(),
        with_payload=True,
        limit=1
        ))
    
    hits = qdrant.search_batch(
    collection_name=_COLLECTION_NAME,
    requests=search_queries
    )
    global viewsen
    global count, bangla_sentences, count1
    global temp
    print(hits)
    index = 0
    for i in enumerate(hits):
        for scored_point in i[1]:
             
            print("ID:", scored_point.id)
            print("Version:", scored_point.version)
            print("Score:", scored_point.score)
            scored_point.score = round(scored_point.score, 2)
            print("Payload:", scored_point.payload)
            scored_point.payload=scored_point.payload['org_sentence']
            print("Vector:", scored_point.vector)
            
            #inserting for viewing
            if scored_point.score >=0.80:
                index = index+1
                tempDict = {"payload": scored_point.payload,
                            "input_sentence": temp[count1],
                            "score": (scored_point.score)*100,
                            "index": index}
                viewsen.append(tempDict)
                count = count + 1
                count1 = count1 + 1
            elif scored_point.score < 0.80 and scored_point.score >= 0.60:
                index = index+1
                tempDict = {"payload": scored_point.payload,
                            "input_sentence": temp[count1],
                            "score": (scored_point.score)*100,
                            "index": index}

                viewsen.append(tempDict)
                count = count + 1
                count1 = count1 + 1
            else:
                index = index+1
                tempDict = {"payload": scored_point.payload,
                            "input_sentence": temp[count1],
                            "score": (scored_point.score)*100,
                            "index": index}
                print(tempDict)
                viewsen.append(tempDict)
                count1 = count1 + 1
                continue
            
    return None

def Profile(request):
    global bangla_sentences,word,character,arr,plagScore,uniqueScore
    global viewsen, count, flag
    global search_results
    # for circular bar
    if count>0:
        plagScore = (count/len(viewsen))*100
        plagScore = round(plagScore, 2)
        uniqueScore = 100 - plagScore
        uniqueScore = round(uniqueScore, 2)
        print(plagScore)
        print(uniqueScore)
    elif count == 0:
        plagScore = 0
        uniqueScore = 0
    else:
        plagScore = 0
        uniqueScore = 0

    sentences = bangla_sentences

    print(button)
    # print("Here is the search resultss---")
    print(search_results)
    args = {
        'text': bangla_sentences, 
        'sentences': sentences, 
        'word':word,
        'character':character, 
        'prog':progress,
        'dprog':(100-progress),
        'button':button,
        'uniqueScore':uniqueScore,
        'viewsen':viewsen,
        'plagScore':plagScore,
        'search_results':search_results,
        
    }
    reload_page(request)
    return render(request, 'home.html', args)

def reload_page(request):
    global plagScore,viewsen
    global uniqueScore
    global count, tempDict, count1
    global search_results
    viewsen = []
    plagScore = 0
    uniqueScore = 0
    count = 0
    tempDict = {}
    count1=0
    search_results = []

    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def generate_report(request):
    global bangla_sentences,word,character,arr
    global viewsen, count, flag
    global search_results
    global plagScore
    global uniqueScore
    # Your code to generate report data and context here
    report_date = viewsen


    # Load the HTML template for the report
    template = get_template('report_template.html')

    context = {
        'report_date': report_date,
        'viewsen':viewsen,
        'plagScore':plagScore,
        'uniqueScore':uniqueScore,
    }
    html_content = template.render(context)  # Directly passing the dictionary

    # Define the path to wkhtmltopdf
    WKHTMLTOPDF_CMD = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
    pdf_file = pdfkit.from_string(html_content, False, configuration=config)

    # Create an HttpResponse with the PDF content to trigger the download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="custom_report.pdf"'

    return response

def log_out(request):
  logout(request)
  return redirect('login')

def aboutus(request):

  return render(request, 'aboutus.html')

@login_required
def upload(request):
    user = request.user
    if request.method == 'POST':
        print("response")
        input_file = request.FILES.get('input_file')
        status = "Pending"
        
        up = UploadFile(file=input_file, status=status, user=user)
        up.save()
    
    show_files = UploadFile.objects.filter(user=user)
   
    args = {
        "show_files": show_files,
    }
    return render(request, 'upload.html', args)

def delete_file(request, pk):
    try:
        obj_to_delete = UploadFile.objects.get(id=pk)
        obj_to_delete.delete()
        
        return redirect('upload')  
    except UploadFile.DoesNotExist:
       
        return HttpResponse("Does not Exist")