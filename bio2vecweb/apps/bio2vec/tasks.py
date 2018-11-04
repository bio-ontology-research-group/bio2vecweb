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
from sklearn.decomposition import TruncatedSVD

ELASTIC_INDEX_URL = getattr(
    settings, 'ELASTIC_INDEX_URL', 'http://localhost:9200/bio2vec')

def create_index():
    settings = {
        "settings" : {
            "analysis": {
                "analyzer": {
                    "payload_analyzer": {
                        "type": "custom",
                        "tokenizer":"whitespace",
                        "filter":"delimited_payload_filter"
                    }
                }
            }
        }
    }
    r = requests.put(ELASTIC_INDEX_URL, json=settings)
    print(r.json())

def configure_index(dataset_name):
    r = requests.head(ELASTIC_INDEX_URL)
    if r.status_code == 404:
        create_index()

    match_all = {"query": {"match_all":{}}}
    r = requests.post(
        ELASTIC_INDEX_URL + '/' + dataset_name + '/_delete_by_query?conflicts=proceed',
        json=match_all)
    print('Delete', r.json())
    mapping = {
        dataset_name : {
            "properties" : {
                "@model_factor": {
                    "type": "text",
                    "term_vector": "with_positions_offsets_payloads",
                    "analyzer" : "payload_analyzer"
                },
                "id": {"type": "keyword"},
                "label": {"type": "keyword"},
                "alt_ids": {"type": "keyword"},
                "synonyms": {"type": "keyword"},
                "type": {"type": "keyword"}
            }
        }
    }
    r = requests.post(
        ELASTIC_INDEX_URL + '/' + dataset_name + '/_mapping', json=mapping)
    print(r.json())


@task
def index_dataset(dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    configure_index(dataset.index_name)
    
    filepath = dataset.embeddings_file.path
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
        embeds.append(list(map(lambda x: float(x), embed)))
        embed = ' '.join(map(lambda x: str(x[0]) + '|' + x[1], enumerate(embed)))
        doc = {
            'id': it[0],
            'label': it[1],
            'alt_ids': it[2].split(','),
            'synonyms': it[3].split(','),
            'type': it[4],
            '@model_factor': embed
        }
        data.append(doc)
    svd = TruncatedSVD(n_components=2)
    res = svd.fit_transform(embeds)
    for i, doc in enumerate(data):
        doc['x'] = res[i, 0]
        doc['y'] = res[i, 1]
        r = requests.post(
            ELASTIC_INDEX_URL + '/' + dataset.index_name + '/' + str(i), json=doc)
        i += 1
    
    dataset.indexed = True
    dataset.save()
        
        
    
