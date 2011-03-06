from surf.session import Session
from surf.store import Store



class Multisession(Session):

    sessions = {}

    def __init__(self, default_store=None, default_query_contexts=None,
                 mapping={}, auto_persist=False, auto_load=False):
        """ Create a new `multisession` object that handles multiple sessions.
        Sessions will be cached.
        
        """

        self.mapping = mapping

        self.default_query_contexts = default_query_contexts

        self.__auto_persist = auto_persist
        self.__auto_load = auto_load
        self.__stores = {}

        if default_store:
            if type(default_store) is not Store:
                raise Exception('The argument is not a valid Store instance')
            self.default_store = default_store

    def __call__(self, *args, **kwargs):
        query_contexts = self.default_query_contexts
        if "query_contexts" in kwargs:
            query_contexts = kwargs.pop("query_contexts")
        return self.query_contexts(query_contexts).__call__(*args, **kwargs)

    def query_contexts(self, query_contexts):
        assert query_contexts
        if not isinstance(query_contexts, list):
            query_contexts = [query_contexts]

        query_contexts = frozenset(query_contexts)

        if query_contexts in self.sessions:
            return self.sessions[query_contexts]

        self.sessions[query_contexts] = super(Multisession, self).__init__(self.default_store, self.mapping,
                                                self.__auto_persist, self.__auto_load,
                                                list(query_contexts))

    def map_type(self, uri, store=None, query_contexts=None, *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        super(Multisession, self.query_contexts(query_contexts))\
                .map_type(uri, store=None, *classes)

    def get_class(self, uri, store=None, *classes):
        return ClassProxy(self, uri, store=None, *classes)

    def map_instance(self, concept, subject, store=None, classes=[],
                     block_auto_load=False, context=None, query_contexts=None):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return super(Multisession, self.query_contexts(query_contexts))\
                .map_instance(concept, subject, store=None, classes=[],
                              block_auto_load=False, context=None)

    def get_resource(self, subject, uri=None, store=None, graph=None,
                     block_auto_load=False, context=None, query_contexts=None,
                     *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return super(Multisession, self.query_contexts(query_contexts))\
                .get_resource(subject, uri=None, store=None, graph=None,
                              block_auto_load=False, context=None, *classes)

    def load_resource(self, uri, subject, store=None, data=None, file=None,
                      location=None, format=None, query_contexts=None, *classes):
        if query_contexts is None:
            query_contexts = self.default_query_contexts
        return super(Multisession, self.query_contexts(query_contexts))\
                .load_resource(uri, subject, store=None, data=None,
                               file=None, location=None, format=None, *classes)



class ClassProxy(object):
    def __init__(self, multisession, uri, store=None, *classes):
        self.multisession = multisession
        self.uri = uri
        self.store = store
        self.classes = classes

    def __call__(self, *args, **kwargs):
        query_contexts = self.multisession.default_query_contexts
        if 'query_contexts' in kwargs:
            query_contexts = kwargs.pop('query_contexts')
        return super(Multisession, self.multisession.query_contexts(query_contexts))\
                   .get_class(self.uri, self.store, *self.classes)\
                   .__call__(*args, **kwargs)

    def query_contexts(self, query_contexts):
        assert query_contexts
        return super(Multisession, self.multisession.query_contexts(query_contexts))\
                   .get_class(self.uri, self.store, *self.classes)


