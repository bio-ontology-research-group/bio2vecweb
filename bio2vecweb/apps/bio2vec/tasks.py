from celery import task
from celery.task.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Max
from django.utils import timezone
from bio2vec.models import Dataset
import os
import gzip
import requests
from MulticoreTSNE import MulticoreTSNE as TSNE
from bio2vec.fast_tsne import fast_tsne
import numpy as np


ELASTICSEARCH_URL = getattr(
    settings, 'ELASTICSEARCH_URL', 'http://localhost:9200/')
TSNE_JOBS = getattr(
    settings, 'TSNE_JOBS', 8)



def configure_index(index_url, dims):
    r = requests.head(index_url)
    if r.status_code != 404:
        requests.delete(index_url)

    mapping = {
        "mappings" : {
            "properties" : {
                "embedding": {
                    "type": "dense_vector",
                    "dims": dims
                },
                "id": {"type": "keyword"},
                "label": {"type": "keyword"},
                "alt_ids": {"type": "keyword"},
                "synonyms": {"type": "keyword"},
                "type": {"type": "keyword"}
            }
        }
    }
    r = requests.put(index_url, json=mapping)
    print(r.json())


@task
def index_dataset(dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    distrib = dataset.get_latest_dist()
    filepath = distrib.embeddings_file.path
    index_url = ELASTICSEARCH_URL + dataset.index_name
    dims = distrib.embedding_size
    configure_index(index_url, dims)
    
    _, ext = os.path.splitext(filepath)
    if ext == '.gz':
        f = gzip.open(filepath, 'rt')
    else:
        f = open(filepath, 'rt')
    i = 0
    data = []
    embeds = []
    for line in f:
        it = line.strip().split('\t')
        embed = it[5].split(',')
        embed = list(map(lambda x: float(x), embed))
        embeds.append(embed)
        doc = {
            'id': it[0],
            'label': it[1],
            'alt_ids': it[2].split(','),
            'synonyms': it[3].split(','),
            'type': it[4],
            'embedding': embed
        }
        data.append(doc)
    embeds = np.hstack(embeds).reshape(-1, dims)
    #res = TSNE(n_jobs=TSNE_JOBS).fit_transform(embeds)
    
    res = fast_tsne(embeds, input_file=filepath + '.in', out_file=filepath + '.out')
    for i, doc in enumerate(data):
        doc['x'] = res[i, 0]
        doc['y'] = res[i, 1]
        r = requests.put(
            index_url + '/_doc/' + str(i), json=doc)
    
    dataset.indexed = True
    dataset.save()
        
        
    
