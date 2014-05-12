from collections import namedtuple
import sys
from rdflib import Graph
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from urlparse import urlparse

Config = namedtuple(
    "Config", 
    [
        "format", # rdflib format
        "template_root",  # the root dir for the templates
        "output_root", # the root dir for the renderings
        "input_file",   # the file handle to read the statements from
    ]
)
    

class ImmutableClass(object):
    def __setattr__(self, *args, **kwargs):
        raise AttributeError("can't set attribute")


class App(namedtuple("Config", ["format", "template_root", "output_root", "input_file"]), ImmutableClass):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        # TODO assert inputs

    def _io_parse_graph(app):
        return Graph().parse(
            app.input_file, 
            format=app.format, 
            publicID=app.output_root
        )

    def __call__(app):
        g = app._io_parse_graph()

        # configure the jinja2 env
        env =  Environment(loader=FileSystemLoader(app.template_root))

        # find all the subjects with template classes
        subjects = app._find_all_subjects(g)

        # render those subjects according to their template class
        for subject in subjects:
            template = env.get_template(subject.template)
            rendering = template.render()
            app._io_write_rendering(subject.uri, rendering)

            path = app._uri_to_path(uri)
            _io_ensure_path(path)
            with open(path, "w") as fh:
                fh.write(rendering)

    def _uri_to_path(app, uri):
        """
        >>> __test_app()._uri_to_path(u'file:///tmp/foo.txt')
        u'/tmp/foo.txt'
        """
        return urlparse(uri).path

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
            yield Subject(record.subject.toPython(), app._uri_to_template_name(g, record.templateClass))

    def _uri_to_template_name(app, g, uri):
        """
        >>> from rdflib import URIRef
        >>> app = __test_app()
        >>> app._uri_to_template_name(app._io_parse_graph(), URIRef("http://schema.org/Name"))
        u'schema:Name.html'
        """
        return g.namespace_manager.qname(uri) + ".html"


Subject = namedtuple("Subject", ["uri", "template"])

def __test_app():
    return App(
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
