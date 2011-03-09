# -*- coding: utf-8 -*-

from surf.session import Session
from surf.store import Store
from surf.rdf import URIRef

class ClassProxy(object):
    def __init__(self, multisession, uri, store=None, *classes):
        self.multisession = multisession
        self.uri = uri
        self.store = store
        self.classes = classes

    def __call__(self, *args, **kwargs):
        query_contexts = kwargs.pop('query_contexts',
                                    self.multisession.default_query_contexts)
        return self.query_contexts(query_contexts)\
                   .__call__(*args, **kwargs)

    def query_contexts(self, query_contexts):
        if query_contexts is None:
            raise Exception("query_contexts must not be None")
        if not isinstance(query_contexts, list):
            query_contexts = [query_contexts]
        return self.multisession.query_contexts(query_contexts)\
                   .get_class(self.uri, self.store, *self.classes)

    def get_by(self, *args, **kwargs):
        query_contexts = kwargs.pop('query_contexts',
                                    self.multisession.default_query_contexts)
        return self.query_contexts(query_contexts).get_by(*args, **kwargs)

    def all(self, *args, **kwargs):
        query_contexts = kwargs.pop('query_contexts',
                                    self.multisession.default_query_contexts)
        return self.query_contexts(query_contexts).all(*args, **kwargs)

class Multisession(Session):

    sessions = {}

    def __init__(self, default_store, default_query_contexts=None,
                 mapping={}, auto_persist=False, auto_load=False, proxy_class=ClassProxy):
        """ Create a new `multisession` object that handles multiple sessions.
        Sessions will be cached.
        
        """

        self.default_query_contexts = default_query_contexts
        self.proxy_class = proxy_class

        super(Multisession, self).__init__(default_store=default_store, mapping=mapping,
                 auto_persist=auto_persist, auto_load=auto_load, query_contexts=default_query_contexts)

        del self.query_contexts

    def query_contexts(self, query_contexts):
        if query_contexts is None:
            raise Exception("query_contexts must not be None")
        if not isinstance(query_contexts, list):
            query_contexts = [query_contexts]
        if not isinstance(query_contexts, list):
            query_contexts = [query_contexts]

        query_contexts = frozenset(query_contexts)

        if query_contexts in self.sessions:
            return self.sessions[query_contexts]
        self.sessions[query_contexts] = Session(default_store=self.default_store,
                                                mapping=self.mapping,
                                                auto_persist=self._Session__auto_persist,
                                                auto_load=self._Session__auto_load,
                                                query_contexts=list(query_contexts))
        return self.sessions[query_contexts]

    def map_type(self, uri, store=None, query_contexts=None, *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return self.query_contexts(query_contexts).map_type(uri, store=store, *classes)

    def get_class(self, uri, store=None, *classes):
        return self.proxy_class(self, uri, store=None, *classes)

    def map_instance(self, concept, subject, store=None, classes=[],
                     block_auto_load=False, context=None, query_contexts=None):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return self.query_contexts(query_contexts)\
                .map_instance(concept, subject, store=store, classes=classes,
                              block_auto_load=block_auto_load, context=context)

    def get_resource(self, subject, uri=None, store=None, graph=None,
                     block_auto_load=False, context=None, query_contexts=None,
                     *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        if isinstance(uri, self.proxy_class):
            uri = uri.query_contexts(query_contexts)
        return self.query_contexts(query_contexts)\
                .get_resource(subject, uri=uri, store=store, graph=graph,
                              block_auto_load=block_auto_load, context=context, *classes)

    def load_resource(self, uri, subject, store=None, data=None, file=None,
                      location=None, format=None, query_contexts=None, *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return self.query_contexts(query_contexts)\
                .load_resource(uri, subject, store=store, data=data,
                               file=file, location=location, format=format, *classes)





