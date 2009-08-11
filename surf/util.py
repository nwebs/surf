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

from namespace import *
import re
import new
from uuid import uuid4

pattern_direct = re.compile('^[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}$', re.DOTALL)
pattern_inverse = re.compile('^is_[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}_of$', re.DOTALL)

def namespace_split(uri):
    '''same as `uri_split`, but instead of the base of the uri, returns the
    registered `namespace` for this uri
    
    .. code-block:: python
    
        >>> print util.namespace_split('http://mynamespace/ns#some_property')
        (rdflib.URIRef('http://mynamespace/ns#'), 'some_property')
        
    '''
    sp = '#' if uri.rfind('#') != -1 else '/'
    base, predicate = uri.rsplit(sp,1)
    return get_namespace('%s%s'%(base,sp))[1], predicate

def uri_split(uri):
    '''splits the `uri` into base path and remainder,
    the base is everything that comes before the last *#*' or */* including it
    
    .. code-block:: python
    
        >>> print util.uri_split('http://mynamespace/ns#some_property')
        ('NS1', 'some_property')
        
    '''
    sp = '#' if uri.rfind('#') != -1 else '/'
    base, predicate = uri.rsplit(sp,1)
    return get_namespace('%s%s'%(base,sp))[0], predicate

def uri_to_classname(uri):
    '''handy function to convert a `uri` to a Python valid `class name`
    
    .. code-block:: python
    
        >>> # prints Ns1some_class, where Ns1 is the namespace (not registered, assigned automatically)
        >>> print util.uri_to_classname('http://mynamespace/ns#some_class')
        Ns1some_class
        
    '''
    ns_key, predicate = uri_split(uri)
    return '%s%s'%(ns_key.title().replace('-','_'),predicate)

def attr2rdf(attrname):
    '''converts an `attribute name` in the form:
    
    .. code-block:: python
    
        # direct predicate
        instance1.foaf_name
        # inverse predicate
        instance2.if_foaf_title_of
            
    to
    
    
    .. code-block:: xml
    
        <!-- direct predicate -->
        <http://xmlns.com/foaf/spec/#term_name>
        <!-- inverse predicate -->
        <http://xmlns.com/foaf/spec/#term_title>
        
    
    the function returns two values, the `uri` representation and True if it's a
    direct predicate or False if its an inverse predicate
    '''
    def tordf(attrname):
        prefix, predicate = attrname.split('_',1)
        ns = get_namespace_url(prefix)
        try:
            return ns[predicate]
        except:
            return None
    
    if pattern_inverse.match(attrname):
        return  tordf(attrname.replace('is_','').replace('_of','')), False
    elif pattern_direct.match(attrname):
        return  tordf(attrname), True
    return None, None

def rdf2attr(uri,direct):
    '''this functions is the inverse of `attr2rdf`, returns the attribute name,
    given the `uri` and wether it is `direct` or not
    
    .. code-block:: python
    
        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_name',True)
        foaf_name
        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_title',False)
        if_foaf_title_of
        
    '''
    ns, predicate = uri_split(uri)
    attribute = '%s_%s'%(ns.lower(),predicate)
    return attribute if direct else 'is_%s_of'%attribute


def is_attr_direct(attrname):
    '''True if it's a direct `attribute`
    
    .. code-block:: python
    
        >>> util.is_attr_direct('foaf_name')
        True
        >>> util.is_attr_direct('is_foaf_name_of')
        False
        
    '''
    return False if pattern_inverse.match(attrname) else True
    
def uri_to_class(uri):
    '''returns a `class object` from the supplied `uri`, used `uri_to_class` to
    get a valid class name
    
    .. code-block:: python
    
        >>> print util.uri_to_class('http://mynamespace/ns#some_class')
        surf.util.Ns1some_class
        
    '''
    return new.classobj(str(uri_to_classname(uri)),(),{'uri':uri})

def uuid_subject(namespace=SURF):
    '''the function generates a unique subject in the provided `namespace` based on
    the :func:`uuid.uuid4()` method,
    If `namespace` is not specified than the default `SURF` namespace is used
    
    .. code-block:: python
    
        >>>  print util.uuid_subject(ns.SIOC)
        http://rdfs.org/sioc/ns#1b6ca1d5-41ed-4768-b86a-42185169faff
        
    '''
    return namespace[str(uuid4())] if namespace else SURF[str(uuid4())]
