.PHONY: test

copy-config:
	cp config.yml.sample config.yml

start:
	python app.py

test:
	python -m coverage run -m unittest */test_*.py

test-cover:
	python -m coverage run -m unittest */test_*.py
	python -m coverage report
