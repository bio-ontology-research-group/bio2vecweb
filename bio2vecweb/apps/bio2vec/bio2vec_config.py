from django.apps import AppConfig
from bio2vecweb.apps.bio2vec.elasticsearch import init as init_es

def startup():
    init_es()
    
class Bio2vecConfig(AppConfig):
    name = 'bio2vec'
    verbose_name = "bio2vec"

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            startup()