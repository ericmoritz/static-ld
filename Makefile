.PHONY: test

dev: 
	python setup.py develop

test: dev
	pip install pytest
	py.test --doctest-modules staticld

acceptance:
	cucumber
