
##
# Makefile for healthapp

ifeq ($(__IS_MAC),true)
BROWSER="open"
else
BROWSER="x-www-browser"
endif

.PHONY: default html static serve view view_served install push_hg push_git

default: html

html:
	python ./healthref.py -i ./treatment_alternatives.ttl -o index.html

static:
	wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css' -O \
		static/css/bootstrap.min.css

serve:
	python -m SimpleHTTPServer 28080

view:
	$(BROWSER) ./index.html

view_served:
	$(BROWSER) http://localhost:28080/

install:
	pip install -r requirements.txt

push_hg:
	hg bookmark -f gh-pages
	hg push
	hg push -f git+ssh://git@github.com/westurner/healthref

push_git:
	git push -f ssh://git@github.com/westurner/healthref gh-pages
