""" Module for allegro_franz plugin tests. """

from unittest import TestCase

from rdflib import URIRef
import surf
from surf.test.plugin import PluginTestMixin


from surf.multisession import Multisession, ClassProxy
from surf.session import Session

class MultisessionWrap(Multisession):
    def get_resource(self, *args, **kwargs):
        kwargs['query_contexts'] = ClassProxyWrap._query_contexts()
        return super(MultisessionWrap, self).get_resource(*args, **kwargs)

class ClassProxyWrap(ClassProxy):

    @classmethod
    def _query_contexts(cls):
        return [URIRef("http://surf_test_graph/dummy2"),
                URIRef("http://my_context_1"),
                URIRef("http://other_context_1")]

    def __call__(self, *args, **kwargs):
        kwargs['query_contexts'] = self._query_contexts()
        return super(ClassProxyWrap, self).__call__(*args, **kwargs)

    def get_by(self, *args, **kwargs):
        kwargs['query_contexts'] = self._query_contexts()
        return super(ClassProxyWrap, self).get_by(*args, **kwargs)

    def all(self, *args, **kwargs):
        kwargs['query_contexts'] = self._query_contexts()
        return super(ClassProxyWrap, self).all(*args, **kwargs)



class AllegroFranzMultiSessionTestMixin(object):

    def _get_store_session(self, use_default_context=True):
        """ Return initialized SuRF store and session objects. """

        # FIXME: take endpoint from configuration file,
        kwargs = {"reader": "allegro_franz",
                  "writer" : "allegro_franz",
                  "server" : "localhost",
                  "port" : 10035,
                  "catalog" : "testcatalog",
                  "repository" : "test_chris"}

        if True: #use_default_context:
            kwargs["default_context"] = URIRef("http://surf_test_graph/dummy2")

        store = surf.Store(**kwargs)
#        session = MultisessionWrap(store,
#                                   default_query_contexts=None,
#                                   proxy_class=ClassProxyWrap)
        session = Multisession(store,
                               default_query_contexts=[URIRef("http://surf_test_graph/dummy2"),
                                                       URIRef("http://my_context_1"),
                                                       URIRef("http://other_context_1")])

        # Fresh start!
        store.clear(URIRef("http://surf_test_graph/dummy2"))
        store.clear(URIRef("http://my_context_1"))
        store.clear(URIRef("http://other_context_1"))
        store.clear()


        Person = session.get_class(surf.ns.FOAF + "Person")
        person = session.get_resource("http://Humbert", Person, context=URIRef("http://hhumbert"))
        person.foaf_name = "Humbert"
        person.save()

        return store, session

class MultiSessionPluginTest(TestCase, AllegroFranzMultiSessionTestMixin, PluginTestMixin):
    pass
