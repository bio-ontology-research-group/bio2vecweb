from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
import requests
import json
import itertools
from django.conf import settings
from collections import defaultdict
from bio2vec.models import Dataset

ELASTIC_INDEX_URL = getattr(
    settings, 'ELASTIC_INDEX_URL', 'http://localhost:9200/bio2vec')


class MostSimilarAPIView(APIView):

    def get(self, request, format=None):
        ids = request.GET.getlist('id', None)
        dataset_name = request.GET.get('dataset', None)
        size = request.GET.get('size', 10)
        offset = request.GET.get('offset', 0)
        dataset = Dataset.objects.filter(name=dataset_name)
        if not dataset.exists():
            return Response({'status': 'error', 'message': 'Dataset not found'})
        dataset = dataset.get()
        query = {
            'query': {
                'terms': {'id': ids}
            }
        }
        result = {}
        try:
            r = requests.post(
                ELASTIC_INDEX_URL + '/' + dataset.index_name + '/_search', json=query)
            if r.status_code != 200:
                return Response(
                    {'status': 'error', 'message': 'Index query error'})

            hits = r.json()['hits']['hits']
            for item in hits:
                item = item['_source']
                result[item['id']] = []
                vector = item['@model_factor']
                vector = vector.split()
                vector = list(map(lambda x: float(x.split('|')[1]), vector))
                query = {
                    "_source": {"excludes": ["@model_factor"]},
                    "query": {
                        "function_score": {
                            "script_score": {
                                "script": {
                	            "inline": "payload_vector_score",
                	            "lang": "native",
                	            "params": {
                    	                "field": "@model_factor",
                    	                "vector": vector,
                    	                "cosine" : True
                                    }
				}
                            },
                            "boost_mode": "replace"
                        }
                    },
                    "from": offset,
                    "size": size
                }
                    
                r = requests.post(
                    ELASTIC_INDEX_URL + '/' + dataset.index_name + '/_search',
                    json=query)
                if r.status_code != 200:
                    return Response(
                        {'status': 'error', 'message': 'Index query error'})
                entities = r.json()['hits']['hits']
                for entity in entities:
                    score = entity['_score']
                    entity = entity['_source']
                    result[item['id']].append({'score': score, 'entity': entity})
                    
        except Exception as e:
            print(e)
        return Response({'status': 'ok', 'result': result})


class SearchEntitiesAPIView(APIView):

    def get(self, request, format=None):
        label = request.GET.get('label', None)
        dataset_name = request.GET.get('dataset', None)
        if label is None:
            return Response(
                {'status': 'error',
                 'message': 'Please provide label parameter!'})
        size = request.GET.get('size', 10)
        offset = request.GET.get('offset', 0)
        dataset = Dataset.objects.filter(name=dataset_name)
        if not dataset.exists():
            return Response({'status': 'error', 'message': 'Dataset not found'})
        dataset = dataset.get()
        query = {
            'query': {
                'prefix': {'label': label}
            },
            'from': offset,
            'size': size
        }
        result = []
        try:
            r = requests.post(
                ELASTIC_INDEX_URL + '/' + dataset.index_name + '/_search', json=query)
            if r.status_code != 200:
                return Response(
                    {'status': 'error', 'message': 'Index query error'})

            hits = r.json()['hits']['hits']
            print(hits)
            result = list(map(lambda x: x['_source'], hits))
        except Exception as e:
            print(e)

        return Response({'status': 'ok', 'result': result})
