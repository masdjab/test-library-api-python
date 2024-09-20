.PHONY: test

copy-config:
	cp config.yml.sample config.yml

dev:
	python3 app.py

test:
	python3 -m unittest
