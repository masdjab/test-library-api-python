.PHONY: test

copy-config:
	cp config.yml.sample config.yml

start:
	python3 app.py

test:
	python3 -m unittest
