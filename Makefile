##
# Makefile for healthapp

default: html

html:
	python ./healthref.py -i ./treatment_alternatives.ttl -o index.html

serve:
	python -m SimpleHTTPServer 28080

view:
	x-www-browser ./index.html

view_served:
	x-www-browser http://localhost:28080/

install:
	pip install -r requirements.txt

push_hg:
	hg bookmark -f gh-pages
	hg push
	hg push -f git+ssh://git@github.com/westurner/healthref

push_git:
	git push -f ssh://git@github.com/westurner/healthref gh-pages
