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


