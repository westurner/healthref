#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
"""
healthref
"""
import codecs
import os
import logging

from collections import OrderedDict

import jinja2
import pygments
import rdflib
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name
from rdflib.namespace import Namespace

log = logging.getLogger()
log.setLevel(logging.DEBUG)


NAMESPACES = (
    (u'dbp', 'https://en.dbpedia.org/resource/'),
    (u'foaf', 'http://xmlns.com/foaf/0.1/'),
    (u'owl', 'http://www.w3.org/2002/07/owl#'),
    (u'rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    (u'rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
    (u'schema', 'http://schema.org/'),
    (u'td', 'http://example.org/ns/todo#'),
    (u'xml', 'http://www.w3.org/XML/1998/namespace'),
    (u'xsd', 'http://www.w3.org/2001/XMLSchema#'),
)


def get_namespace_manager(set_globals=False):
    nsm = rdflib.namespace.NamespaceManager(rdflib.Graph())
    for key, value in NAMESPACES:
        namespace = rdflib.namespace.Namespace(value)
        nsm.bind(key, namespace)
    return nsm


def set_namespace_globals(nsm):
    glbls = globals()
    for key, value in nsm.namespaces():
        namespace = rdflib.namespace.Namespace(value)
        nsm.bind(key, namespace)
        _key = key.upper()
        if _key in glbls:
            raise Exception("clobbering globals: %r" % _key)
        glbls[_key] = namespace


def print_namespace_globals(nsm):
    for key, value in sorted(nsm.namespaces()):
        print("%s = Namespace(%r)" % (key.upper(), unicode(value)))


NSM = get_namespace_manager()
# set_namespace_globals(NSM)
# print_namespace_globals(NSM)
DBP = Namespace(u'https://en.dbpedia.org/resource/')
FOAF = Namespace(u'http://xmlns.com/foaf/0.1/')
OWL = Namespace(u'http://www.w3.org/2002/07/owl#')
RDF = Namespace(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace(u'http://www.w3.org/2000/01/rdf-schema#')
SCHEMA = Namespace(u'http://schema.org/')
TD = Namespace(u'http://example.org/ns/todo#')
XML = Namespace(u'http://www.w3.org/XML/1998/namespace')
XSD = Namespace(u'http://www.w3.org/2001/XMLSchema#')


RDF_INPUT_FORMATS = {
    'ttl': 'text/turtle',
    'jsonld': 'json-ld'
}


def read_rdf_files(input_files, graph=None):
    if graph is None:
        graph = rdflib.ConjunctiveGraph()
    graph = rdflib.ConjunctiveGraph()  # Graph()
    for input_file in input_files:
        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            graph.parse(f,
                        format=RDF_INPUT_FORMATS.get(input_file.split('.')[-1]),
                        location=os.path.abspath(input_file))
    return graph


def get_label(g, subject):
    output = g.preferredLabel(subject, lang='en')
    if not output:
        return unicode(subject)  # TODO: qname?
    return unicode(output[0][-1])


DEFAULT_PREDICATE_ORDERING = [
    RDF.type,
    RDFS.label,
    OWL.sameAs,
    SCHEMA.alternateName
]


def slugify(content, prefix=None):
    _content = content.replace(" ", "-").lower()  # TODO
    if prefix:
        return u'%s--%s' % (prefix, _content)
    else:
        return _content


def iter_pred_obj(g, pred_obj_objects):
    for obj in pred_obj_objects:
        yield(
            get_label(g, obj),
            obj if isinstance(obj, rdflib.URIRef) else '')


def iter_subj_pred(g, subject, predicate_ordering):
    for predicate in predicate_ordering:
        objects = sorted(g.objects(subject, predicate))
        if not objects:
            continue
        yield (predicate, {
            "label": get_label(g, predicate),
            "objects": OrderedDict(iter_pred_obj(g, objects))})


def iter_subjects(g, subjects,
                  slug_prefix=None,
                  predicate_ordering=DEFAULT_PREDICATE_ORDERING):
    for subject in subjects:
        label = get_label(g, subject)
        yield (subject, {
            "label": label,
            "slug": slugify(label, slug_prefix),
            "properties": OrderedDict(
                iter_subj_pred(g, subject,
                               predicate_ordering=predicate_ordering))})


def iter_section(g, object, slug_prefix,
                 predicate_ordering=DEFAULT_PREDICATE_ORDERING):
    #groups = sorted(g.query("SELECT ?s WHERE { ?s a ?object }"))
    subjects = sorted(g.subjects(object=object))
    return OrderedDict(
        iter_subjects(g, subjects,
                      slug_prefix=slug_prefix,
                      predicate_ordering=predicate_ordering))


# TODO: .. JSON-LD + JS implementation (preferredLabel?)

def pygmentize(filename):
    lexer = get_lexer_by_name("n3")
    formatter = get_formatter_by_name('html')
    with codecs.open(filename, encoding='utf-8') as f:
        return pygments.highlight(f.read(), lexer, formatter)


def get_template(template='healthref.html'):
    env = jinja2.Environment(
        autoescape=True,)  # ... TODO
    loader = jinja2.FileSystemLoader(
        os.path.dirname(
            os.path.abspath(__file__)))
    tmpl = loader.load(env, 'healthref.html')
    return tmpl


def healthref(input_files, output):
    """
    mainfunc
    """
    g = read_rdf_files(input_files)
    c = OrderedDict()
    sections = c['sections'] = OrderedDict()
    sections['drug-groups'] = {
        "title": "Drug Groups",
        "object": TD.DrugGroup,
        "predicate_ordering": [
            # RDF.type,
            # RDFS.label,
            OWL.sameAs,
            SCHEMA.alternateName,
            TD.drugGroup,
            TD.AtcLink,
            TD.wikipediaLink,
            TD.medlineLink,
            TD.adverseEffectsLink,
        ]
    }
    sections['therapies'] = {
        "title": "Therapies",
        "object": DBP.Therapy,
        "predicate_ordering": [
            OWL.sameAs,
            SCHEMA.alternateName,
            TD.drugGroup,
            TD.effect,
            TD.contraindicationsLink,
            TD.contraindications,
            TD.adverseEffectsLink,
            TD.medlineLink,
            TD.wikipediaLink,
        ]
    }
    sections['diseases'] = {
        "title": "Diseases",
        "object": DBP.Disease,
        "predicate_ordering": [
            OWL.sameAs,
            SCHEMA.alternateName,
            TD.medlineLink,
            TD.wikipediaLink,
        ]
    }
    sections['symptoms'] = {
        "title": "Symptoms",
        "object": DBP.Symptom,
        "predicate_ordering": [
            OWL.sameAs,
            SCHEMA.alternateName,
            TD.medlineLink,
            TD.wikipediaLink,
        ]
    }
    sections['adverse-effects'] = {
        "title": "Adverse Effects",
        "object": DBP.Adverse_effect,
        "predicate_ordering": [
            OWL.sameAs,
            SCHEMA.alternateName,
            TD.medlineLink,
            TD.wikipediaLink,
        ]
    }

    for key, obj in sections.iteritems():
        c[key] = iter_section(g,
                              obj['object'],
                              # obj['title'],
                              key,
                              predicate_ordering=obj['predicate_ordering'])

    tmpl = get_template('healthref.html')

    return tmpl.render({
        'title': "Health Reference",
        'object': c,
        'source': jinja2.Markup(
            pygmentize('treatment_alternatives.ttl')),  # TODO: constant
    })


import unittest


class Test_healthref(unittest.TestCase):
    input_files = ('treatment_alternatives.ttl',)

    def test_get_namespace_manager(self):
        nsm = get_namespace_manager()
        for k, v in nsm.namespaces():
            print(k, v)
        self.assertTrue(nsm)

    def test_read_rdf_files(self):
        g = read_rdf_files(self.input_files)
        self.assertTrue(len(g))

    def test_iter_drug_groups(self):
        g = read_rdf_files(self.input_files)
        c = iter_section(g, TD.DrugGroup, "Drug Group")
        self.assertTrue(len(c))

        print(c.keys())
        import json
        print(json.dumps(c, indent=2))
        #from pprint import pformat
        # print(pformat(c))

    def test_z_healthref(self):
        output = sys.stdout
        output.write(healthref(self.input_files, output))
        output.flush()


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('-i', '--input-file',
                   dest='input_files',
                   action='append',
                   default=[])
    prs.add_option('-o', '--output',
                   dest='output',
                   action='store',
                   default='-')

    prs.add_option('-v', '--verbose',
                   dest='verbose',
                   action='store_true',)
    prs.add_option('-q', '--quiet',
                   dest='quiet',
                   action='store_true',)
    prs.add_option('-t', '--test',
                   dest='run_tests',
                   action='store_true',)

    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        sys.argv = [sys.argv[0]] + args
        import unittest
        sys.exit(unittest.main())

    output = None
    if opts.output == '-':
        output = sys.stdout
    else:
        output = codecs.open(opts.output, 'w+', encoding='utf-8')

    if not opts.input_files:
        prs.error("Must specify at least one input file with -i/--input")

    try:
        output.write(healthref(opts.input_files, output))
    finally:
        if opts.output != '-':
            output.close()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
