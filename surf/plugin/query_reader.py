# Copyright (c) 2009, Digital Enterprise Research Institute (DERI),
# NUI Galway
# All rights reserved.

# author: Cosmin Basca
# email: cosmin.basca@gmail.com

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#    * Neither the name of DERI nor the
#      names of its contributors may be used to endorse or promote  
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY DERI ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DERI BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-
__author__ = 'Cosmin Basca'

from surf.plugin.reader import RDFReader
from surf.query import Query, a, ask, select, Filter, optional_group, named_group

from rdflib.URIRef import URIRef

def query_SP(s, p, direct, context):
    """ Construct :class:`surf.query.Query` with `?v` and `?c` as unknowns. """ 
    
    s, v = (s, '?v') if direct else ('?v', s)
    query = select('?v', '?c').distinct()
    query.where((s, p, v)).optional_group(('?v', a, '?c'))
    if context:
        query.from_(context)
        
    return query 

def query_S(s, direct, context):
    """ Construct :class:`surf.query.Query` with `?p`, `?v` and `?c` as 
    unknowns. """

    s, v = (s, '?v') if direct else ('?v', s)
    query = select('?p','?v','?c').distinct()
    query.where((s, '?p', v)).optional_group(('?v', a, '?c')) 
    if context:
        query.from_(context)

    return query
    
def query_Ask(subject, context):
    """ Construct :class:`surf.query.Query` of type **ASK**. """ 

    query = ask()
    if context:
        pattern = named_group(context, (subject, '?p', '?o'))
        query.where(pattern)
    else:
        query.where((subject, '?p', '?o'))

    return query
    
def query_All(concept, limit = None, offset = None, context = None):
    """ Construct :class:`surf.query.Query` with `?s` as the unknown. """ 

    query = select('?s').distinct()
    query.where(('?s', a, concept)).limit(limit).offset(offset)
    if context:
        query.from_(context)
    
    return query 

def query_AllRelated(concept, limit = None, offset = None, context = None):
    """ Return Query that selects subjects and related triples.
        
    First, in subquery, select resource `URIs` that have type matching concept 
    argument. Then, in main query, select all triples that have previously
    selected `URIs` as subjects.  
    
    """
    
    inner_query = select('?s').where(('?s', a, concept))
    inner_query.limit(limit).offset(offset)
    
    query = select('?s', '?p', '?v', '?c').distinct()
    query.group(('?s', '?p', '?v'), optional_group(('?v',a,'?c')))
    query.where(inner_query)
    
    if context:
        query.from_(context)
    
    return query
    
#Resource class level
def query_P_S(c, p, direct, context):
    """ Construct :class:`surf.query.Query` with `?s` and `?c` as unknowns. """ 
    
    query = select('?s', '?c').distinct()
    if context:
        query.from_(context)
    
    for i in range(len(p)):
        s, v = ('?s', '?v%d' % i) if direct else ('?v%d' % i, '?s')
        if type(p[i]) is URIRef: query.where((s, p[i], v))
    query.optional_group(('?s', a, '?c'))
    
    return query

def query_PO(c, direct, filter = "", preds = {}, context = None):
    """ Construct :class:`surf.query.Query` with filters. 
    
    Filters have to follow SPARQL syntax.
    
    """ 

    query = select('?s', '?c').distinct().where(('?s', a, c))
    if context:
        query.from_(context)
    
    i = 0 
    for p, v in preds.items():
        f = Filter.regex('?v%d' % (i), v) if filter == 'regex' and direct else None
        s, v = ('?s', v) if direct else (v, '?s')
        query.where((s, p, v)).filter(f)
        i += 1
    query.optional_group(('?s', a, '?c'))
    return query

def query_P_V(c, direct, p = []):
    """ Construct :class:`surf.query.Query` with `?v` and `?c` as unknowns. """ 

    query = select('?v', '?c').distinct()
    for i in range(len(p)):
        s, v= (c, '?v') if direct else ('?v', c)
        query.where((s, p[i], v))
    query.optional_group(('?v', a, '?c'))
    return query
    
def query_Concept(subject):
    """ Construct :class:`surf.query.Query` with `?c` as the unknown. """ 

    return select('?c').distinct().where((subject, a, '?c'))

class RDFQueryReader(RDFReader):
    """ Super class for all SuRF Reader plugins that wrap queryable `stores`. """    
    
    def __init__(self,*args,**kwargs):
        RDFReader.__init__(self,*args,**kwargs)
        self.use_subqueries = kwargs.get('use_subqueries',False)
        if type(self.use_subqueries) in [str, tuple]:
            self.use_subqueries = True if self.use_subqueries.lower() == 'true' else False
        elif type(self.use_subqueries) is not bool:
            raise ValueError('The use_subqueries parameter must be a bool or a string set to "true" or "false"')
    
    #protected interface
    def _get(self, subject, attribute, direct, context):
        query = query_SP(subject, attribute, direct, context)
        result = self._execute(query)
        return self.convert(result, 'v', 'c')
    
    def _load(self, subject, direct, context):
        query = query_S(subject, direct, context)
        result = self._execute(query)
        return self.convert(result, 'p', 'v', 'c')
    
    def _is_present(self, subject, context):
        query = query_Ask(subject, context)
        result = self._execute(query)
        return self._ask(result)
    
    def _all(self, concept, limit = None, offset = None, full = False,
             context = None):
        
        if full and self.use_subqueries:
            query = query_AllRelated(concept, limit = limit, offset = offset,
                                     context = context)
                        
            result = self._execute(query)
            return self.convert(result, 's', 'p', 'v', 'c')
        else:
            query = query_All(concept, limit = limit, offset = offset, 
                              context = context)
            
            result = self._execute(query)
            return self.convert(result,'s')
    
    def _concept(self,subject):
        query = query_Concept(subject)
        result = self._execute(query)
        return self.convert(result, 'c')
        
    def _instances_by_attribute(self, concept, attributes, direct, context):
        query = query_P_S(concept, attributes, direct, context)
        result = self._execute(query)
        return self.convert(result, 's', 'c')
        
    def _instances(self, concept, direct, filter, predicates, context):
        query = query_PO(concept, direct, filter = filter, preds = predicates,
                         context = context)
        
        result = self._execute(query)
        return self.convert(result, 's', 'c')

    def __apply_limit_offset_order_get_by(self, params, query):
        """ Apply limit, offset, order parameters to query. """
        
        if "limit" in params:
            query.limit(params["limit"])
        
        if "offset" in params:
            query.offset(params["offset"])

        if "order" in params:
            if params["order"] == True:
                # Order by subject URI
                query.order_by("?s")
            else:
                # Match another variable, order by it
                query.optional_group(("?s", params["order"], "?o")) 
                query.order_by("?o")

        if "get_by" in params:
            for attribute, value, direct  in params["get_by"]:
                if direct:
                    query.where(("?s", attribute, value))
                else:
                    query.where((value, attribute, "?s"))
        
        return query
        
    def _get_by(self, params):
        
        # Decide which loading strategy to use
        if "full" in params:
            if self.use_subqueries:
                return self.__get_by_subquery(params)
            else:
                return self.__get_by_n_queries(params)

        # No details, just subjects and classes
        query = select("?s", "?c")
        query.optional_group(("?s", a, "?c"))
        self.__apply_limit_offset_order_get_by(params, query)

        if "context" in params:
            query.from_(params["context"])

        self.__apply_limit_offset_order_get_by(params, query)

        # Load just subjects and their types
        table = self._to_table(self._execute(query))
        
        # Create response structure, preserve order, don't include 
        # duplicate subjects if some subject has multiple types
        subjects = {} 
        results = []
        for match in table:
            subject = match["s"]
            if not subject in subjects:
                instance_data = {"direct" : {a : {}}}
                subjects[subject] = instance_data
                results.append((subject, instance_data))

            if "c" in match:
                concept = match["c"]
                subjects[subject]["direct"][a][concept] = []
            
        return results

    def __get_by_n_queries(self, params):
        context = params.get("context", None)
            
        query = select("?s")
        query.from_(context)

        self.__apply_limit_offset_order_get_by(params, query)
                
        # Load details, for now the simplest approach with N queries. 
        # Use _to_table instead of convert to preserve order.
        results = []
        for match in self._to_table(self._execute(query)):
            subject = match["s"]
            instance_data = {}
            
            result = self._execute(query_S(subject, True, context))
            result = self.convert(result, 'p', 'v', 'c')
            instance_data["direct"] = result

            if not params.get("only_direct"):
                result = self._execute(query_S(subject, False, context))
                result = self.convert(result, 'p', 'v', 'c')
                instance_data["inverse"] = result
            
            results.append((subject, instance_data))
        
        return results

    def __get_by_subquery(self, params):
        context = params.get("context", None)
            
        inner_query = select("?s")
        inner_params = params.copy()
        if "order" in inner_params:
            del inner_params["order"]
        self.__apply_limit_offset_order_get_by(inner_params, inner_query)
        
        query = select("?s", "?p", "?v", "?c").distinct()
        query.group(('?s', '?p', '?v'), optional_group(('?v',a,'?c')))
        query.where(inner_query)
        query.from_(context)

        # Need ordering in outer query
        if "order" in params:
            if params["order"] == True:
                # Order by subject URI
                query.order_by("?s")
            else:
                # Match another variable, order by it
                query.optional_group(("?s", params["order"], "?order")) 
                query.order_by("?order")

        table = self._to_table(self._execute(query))
        subjects = {} 
        results = []
        for match in table:
            subject = match["s"]
            predicate = match["p"]
            value = match["v"]

            # Add subject to result list if it's not there
            if not subject in subjects:
                instance_data = {"direct" : {}}
                subjects[subject] = instance_data
                results.append((subject, instance_data))
            
            # Add predicate to subject's direct predicates if it's not there
            direct_attributes = subjects[subject]["direct"]
            if not predicate in direct_attributes:
                direct_attributes[predicate] = {}

            # Add value to subject->predicate if ...
            predicate_values = direct_attributes[predicate]
            if not value in predicate_values:
                predicate_values[value] = []
                
            # Add RDF type of the value to subject->predicate->value list 
            if "c" in match:
                predicate_values[value].append(match["c"])
            
        return results
        
    def _instances_by_value(self, concept, direct, attributes):
        query = query_P_V(concept, direct, p = attributes)
        result = self._execute(query)
        return self.convert(result, 'v', 'c')
    
    # to implement
    def _ask(self, result):
        """ Return boolean value of an **ASK** query. """
        
        return False
    
    # execute
    def _execute(self, query):
        """ To be implemented by classes the inherit from `RDFQueryReader`.
        
        This method is called internally by :meth:`execute`.
        
        """
        
        return None

    def _to_table(self, result):
        return []
    
    def __convert(self, query_result, *keys):
        results_table = self._to_table(query_result)
        
        if len(keys) == 1:
            return [row[keys[0]] for row in results_table]
        
        last = len(keys)-2
        results = {}
        for row in results_table:
            data = results
            for i in range(len(keys)-1):
                k = keys[i]
                if k not in row:
                    continue
                v = row[k]
                if i < last:
                    if v not in data:
                        data[v] = {}
                    data = data[v]
                elif i == last:
                    if v not in data:
                        data[v] = []
                    data[v].append(row.get(keys[i+1]))
        return results

    # public interface    
    def execute(self, query):
        """ Execute a `query` of type :class:`surf.query.Query`. """

        q = query if type(query) is Query else None
        if q:
            return self._execute(q)
        return None
    
    def convert(self, query_result, * keys):
        """ Convert the results from the query to a multilevel dictionary.
        
        This method is used by the :class:`surf.resource.Resource` class. 
        
        """
        
        try:
            return self.__convert(query_result, *keys)
        except Exception, e:
            self.log.error('Error on Convert : ' + str(e))
        return []