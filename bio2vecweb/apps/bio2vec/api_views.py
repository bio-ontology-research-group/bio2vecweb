from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
import requests
import json
import itertools
from django.conf import settings
from collections import defaultdict
from bio2vec.models import Dataset
from bio2vecweb.apps.bio2vec.elasticsearch import execute_query


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
            index_name = settings.ELASTICSEARCH_INDEX_PREFIX + dataset.index_name
            r = execute_query(index_name, query)
            hits = r['hits']['hits']
            for item in hits:
                item = item['_source']
                result[item['id']] = []
                vector = item['embedding']
                query = {
                    "_source": {"excludes": ["embedding"]},
                    "query": {
                        "script_score": {
                            "query" : {
                                "match_all": {}
                            },
                            "script": {
                                "source": "cosineSimilarity(params.vector, 'embedding') + 1",
                                "params": {
                                    "vector": vector,
                                }
                            }
                        }
                    },
                    "from": offset,
                    "size": size
                }
                    
                r = execute_query(index_name, query)
                entities = r['hits']['hits']
                result[item['id']] = entities
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)})
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
        query = {
            '_source': {"includes": ["id", "label"]},
            'query': {
                'bool': {
                    'must': [
                        {'prefix': {'label': label}}
                    ]
                }
            },
            'from': offset,
            'size': size
        }
        dataset = Dataset.objects.filter(name=dataset_name)
        if dataset.exists():
            dataset = dataset.get()
            index = settings.ELASTICSEARCH_INDEX_PREFIX + dataset.index_name
        else:
            index = settings.ELASTICSEARCH_INDEX_PREFIX + 'dataset_*'
        result = []
        try:
            r = execute_query(index, query)
            result = r['hits']['hits']
        except Exception as e:
            print(e)
            return Response(
                {'status': 'exception', 'message': str(e)})

        return Response({'status': 'ok', 'result': result})


class EntitiesAPIView(APIView):

    def get(self, request, format=None):
        iris = request.GET.getlist('iri', None)
        dataset_name = request.GET.get('dataset', None)
        size = request.GET.get('size', 10)
        offset = request.GET.get('offset', 0)
        if dataset_name is None:
            return Response(
                {'status': 'error',
                 'message': 'Please provide dataset parameter!'})
        dataset = Dataset.objects.filter(name=dataset_name)
        if not dataset.exists():
            return Response(
                {'status': 'error',
                 'message': 'Dataset not found!'})
        dataset = dataset.get()
        query = {
            '_source': {"excludes": ["embedding"]},
            'from': offset,
            'size': size
        }

        if iris:
            query['query'] = {
                'terms': {
                    'id': iris
                }
            }
        else:
            query['query'] = {'match_all': {}}
        
        result = []
        try:
            index_name = settings.ELASTICSEARCH_INDEX_PREFIX + dataset.index_name
            r = execute_query(index_name, query)
            result = r['hits']['hits']
        except Exception as e:
            return Response(
                {'status': 'exception', 'message': str(e)})
        return Response({'status': 'ok', 'result': result})
