from collections import namedtuple
import sys
import os
from rdflib import Graph, URIRef, Literal, Namespace
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from urlparse import urlparse
from logging import getLogger
import urlparse
import sys
import posixpath


log = getLogger(__name__)

class ImmutableClass(object):
    def __setattr__(self, *args, **kwargs):
        raise AttributeError("can't set attribute")


class App(namedtuple("Config", ["site_url", "format", "template_root", "output_root", "input_file"]), ImmutableClass):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        # TODO assert inputs

    def _io_parse_graph(app):
        return Graph().parse(
            app.input_file, 
            format=app.format, 
            publicID=app.site_url
        )

    def __call__(app):
        g = app._io_parse_graph()

        # configure the jinja2 env
        env =  Environment(
            loader=FileSystemLoader(app.template_root)
        )

        # detect static:Template classes using the template filenames
        g = app._detect_templates_classes(g, env)

        # find all the subjects with template classes
        subjects = app._find_all_subjects(g)

        # render those subjects according to their template class
        for subject in subjects:
            relative_uri_to_subject = lambda uri: relative_uri(subject.uri, uri)
            template = env.get_template(subject.template)
            path = app._uri_to_path(relative_uri(app.site_url, subject.uri))

            log.info("Rendering {uri!r} using {template!r} to {path!r}".format(
                uri=subject.uri,
                template=subject.template,
                path=path
            ))

            rendering = template.render(
                subject=subject,
                graph=g,
                URIRef=URIRef,
                relative_uri=relative_uri_to_subject
            )

            _mkdir(os.path.dirname(path))
            with open(path, "w") as fh:
                fh.write(rendering)

    def _uri_to_path(app, uri):
        """
        >>> __test_app()._uri_to_path(u'foo.txt')
        u'/tmp/output/foo.txt'
        """
        return os.path.join(app.output_root, uri)

    def _detect_templates_classes(app, g, env):
        # index the namespaces
        rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        static = Namespace("http://vocab-ld.org/vocab/static-ld#")
        
        for template in env.list_templates():
            qname, ext = os.path.splitext(template)
            try:
                uri = _expand_qname(g, qname)
            except:
                uri = None

            if uri:
                g.add(
                    (
                        URIRef(uri),
                        rdf.type,
                        static.Template
                    )
                )
        return g

    def _find_all_subjects(app, g):
        """
        >>> app = __test_app()
        >>> sorted(list(app._find_all_subjects(app._io_parse_graph())))
        [Subject(uri=u'file:///tmp/output/1.html', template=u'schema:Person.html'), Subject(uri=u'file:///tmp/output/2.html', template=u'schema:Thing.html')]
        """

        records = g.query("""
        SELECT ?subject ?templateClass
        WHERE {
          ?templateClass a static:Template .
          ?subject a ?templateClass
        }
        """)
        for record in records:
            yield Subject(
                g, 
                record.subject, 
                template=app._uri_to_template_name(g, record.templateClass)
            )

    def _uri_to_template_name(app, g, uri):
        """
        >>> from rdflib import URIRef
        >>> app = __test_app()
        >>> app._uri_to_template_name(app._io_parse_graph(), URIRef("http://schema.org/Name"))
        u'schema:Name.html'
        """
        return g.namespace_manager.qname(uri) + ".html"


class Subject(object):
    def __init__(self, g, identifier, template=None):
        self.__g = g
        self.id = identifier
        self.template = template
        self.uri = identifier.toPython()

    def __repr__(self):
        return "Subject(uri={uri!r}, template={template!r})".format(
            uri=self.uri,
            template=self.template
        )

    def __cmp__(self, y):
        return cmp(
            (self.uri, self.template),
            (y.uri, y.template)
        )

    def get(self, predicate_uri, default=""):
        for value in self.all(predicate_uri):
            return value
            break
        else:
            return default
        
    def all(self, predicate_uri):
        if not isinstance(predicate_uri, URIRef):
            predicate_uri = _expand_qname(self.__g, predicate_uri)
        for obj in self.__g.objects(self.id, URIRef(predicate_uri)):
            if not isinstance(obj, Literal):
                yield Subject(self.__g, obj)
            else:
                yield obj
            

def relative_uri(base, target):
    """
    >>> relative_uri(u"http://example.com/foo/", u"http://example.com/foo/bar")
    u'bar'

    >>> relative_uri(u"http://example.com/baz/", u"http://example.com/foo/bar")
    u'../foo/bar'

    >>> relative_uri(u"http://example2.com/baz/", u"http://example.com/foo/bar")
    u'http://example.com/foo/bar'

    """
    base_bits=urlparse.urlparse(base)
    target_bits=urlparse.urlparse(target)
    if base_bits.netloc != target_bits.netloc:
        return target
    base_dir='.'+posixpath.dirname(base_bits.path)
    target='.'+target_bits.path
    return posixpath.relpath(target,start=base_dir)

            

def _expand_qname(g, qname):
    """
    >>> _expand_qname(__test_app()._io_parse_graph(), "schema:name")
    u'http://schema.org/name'

    >>> _expand_qname(__test_app()._io_parse_graph(), "xyzzy:name")
    Traceback (most recent call last):
        ...
    Exception: Unknown prefix xyzzy

    u'http://schema.org/name'

    """
    prefix, name = qname.split(":")
    for ns_prefix, uri in g.namespace_manager.namespaces():
        if ns_prefix == prefix:
            return uri.toPython() + name
    raise Exception("Unknown prefix {prefix}".format(prefix=prefix))


def _mkdir(path):
    if not os.path.exists(path):
        os.makedirs(os.path.abspath(path))

def __test_app():
    return App(
        site_url="file:///tmp/output/",
        format="turtle",
        template_root="/tmp/templates/",
        output_root="/tmp/output/",
        input_file=BytesIO(
                """
                @prefix schema: <http://schema.org/> .
                @prefix static:  <http://vocab-ld.org/vocab/static-ld#> .

                <./1.html> a schema:Person .
                <./2.html> a schema:Thing .

                schema:Person a static:Template .
                schema:Thing a static:Template .
                """
        )
    )
