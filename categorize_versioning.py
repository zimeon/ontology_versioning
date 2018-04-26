#!/usr/bin/env python
"""Attempt to categorize ontology versioning schemes."""

import gzip
import json
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
import re
from urllib.parse import urlparse


def uri_path(uri):
    """Get path component of URI, including fragment if present."""
    p = urlparse(uri)
    path = p.path
    if p.fragment or uri.endswith('#'):
        path += '#' + p.fragment
    return path

        
VANN = Namespace("http://purl.org/vocab/vann/")
VOAF = Namespace("http://purl.org/vocommons/voaf#")
ZIMEON = Namespace("http://zimeon.com/terms/")

statuses = {}
with open("manual_assessments.ttl", "r") as ttlfh:
    g2 = Graph()
    g2.parse(ttlfh, format="turtle")
    for (vocab, status) in g2.subject_objects(ZIMEON.versioning):
        statuses[vocab] = str(status)
        print("%s - %s" % (status, vocab))
print("Read %d manual assessments" % (len(statuses)))

with gzip.open("lov.n3.gz", "r") as n3fh:
    g = Graph()
    g.parse(n3fh, format="n3")

categories = {'no': set()}
no_num = 0

for vocab in g.subjects(RDF.type, VOAF.Vocabulary):
    prefix = g.value(vocab, VANN.preferredNamespacePrefix)
    path = uri_path(vocab)
    if re.search(r'''\d''', path):
        status = statuses[vocab] if vocab in statuses else "unknown"
        print('%20s %s' % (prefix, status))
        if (status not in categories):
            categories[status] = set()
        categories[status].add(vocab)
    else:
        no_num += 1
        categories['no'].add(vocab)

print("Summary stats:")
print("- vocabs with no number in namespace URI: %d" % (no_num))
for status in categories:
    print("- vocabs with %15s versioning of namespace:  %d" % (status, len(categories[status])))
