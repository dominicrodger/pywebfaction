.PHONY: clean-pyc clean-build clean release test coverage flake8 docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "coverage - run tests to generate a code coverage report"
	@echo "docs - rebuild the docs"
	@echo "flake8 - run flake8 against the Python code"
	@echo "release - package and upload a release"
	@echo "test - run tests against all supported Python versions"


clean: clean-build clean-pyc
	rm -rf htmlcov/

clean-build:
	rm -rf *.egg/
	rm -rf __pycache__/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

test:
	tox

coverage:
	py.test --cov-report term-missing --cov pywebfaction

flake8:
	tox -e flake8

docs:
	tox -e docs
