static-ld
==========

A static site generator that uses Linked Data as its data source.


Usage
-------

`static-ld` takes advantage of Linked Data and Jinja2 to provide a modern
templating system for generating static content from your Linked Data.

Running the following command

```
   cat test/data/*.ttl | staticld -f turtle test/templates/ test/output/
```

Will combine the data in [test/data/*.ttl](test/data) with the templates in [test/templates/](test/templates) and
render them to `test/output/`



static namespace
------------------

The namespace for static-ld is http://vocab-ld.org/vocab/static-ld#. 
