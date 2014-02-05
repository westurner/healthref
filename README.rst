healthref
==========

A Health Reference Application

Generates a static HTML reference page from RDF.

Usage
------
Install:::

    git clone https://github.com/westurner/healthref
    pip install -r requirements.txt

Generate:::

    make html
    # python ./healthref.py -i treatment_alternatives.ttl -o index.html

View:::

    make view
    # x-www-browser ./index.html
    

Requirements
-------------
* [RDFLib](https://github.com/RDFLib/rdflib)
* [Jinja2](https://github.com/mitsuhiko/jinja2)
* [Pygments](https://bitbucket.org/birkenfeld/pygments-main)
* [n3pygments](https://github.com/gniezen/n3pygments)
