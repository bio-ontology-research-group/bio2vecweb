import logging
import uuid
import requests

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from django.conf import settings
from requests.auth import HTTPDigestAuth

logger = logging.getLogger(__name__)

es = None
esUrl = settings.ELASTICSEARCH_URL.split(",")
use_ssl = False 

if 'https' in esUrl[0]:
  use_ssl = True

http_auth = None
if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
  http_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)

if not es:
  es = Elasticsearch(esUrl, http_auth=http_auth,
        use_ssl=use_ssl,
        sniff_on_start=True,
        sniff_on_connection_fail=True,
        sniffer_timeout=60)
  logger.info("Connected to elasticesearch server: %s", str(es))

def create(index, index_settings):
  try:
    es.indices.create(index=index, body=index_settings, ignore=400)
    logger.info("Index created '%s'", index)
  except Exception as e:
      logger.exception("message")

def delete(index):
  try:
    es.indices.delete(index=index, ignore=[400, 404])
    logger.info("Index deleted '%s'", index)
  except Exception as e:
      logger.exception("message")

def index(index, id, document):
  try:
    result = es.index(index=index, id=id, body=document)
    if result["result"] == "created":
      return True
    return False 
  except Exception as e:
    logger.exception("message")

# def index_by_bulk(data):
#   try:
#     entries = []
#     for entry in data:
#       entries.append({ 
#           "_index": ENTITY_INDEX_NAME,
#           "_id": uuid.uuid4().hex,
#           "_source": entry
#       })
#     result = helpers.bulk(es, entries, refresh=True, request_timeout=(60 * 10))
#     logger.info("entries effected: %d", result[0])
#   except Exception as e:
#     logger.exception("message")

def execute_query(index, query):
  try:
    logger.debug("running query:%s", query)
    return es.search(index=index, body=query, request_timeout=60)
  except Exception as e:
      logger.exception("message")
