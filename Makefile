# Makefile to simplify test and build.

.PHONY: all up down test clean test-env lint style coverage

all: test

up:
	docker-compose up -d

down:
	docker-compose down

build-python:
	python setup.py sdist bdist_wheel

clean:
	rm -rf coverage_html_report .coverage
	rm -rf livetrackbot.egg-info
	rm -rf __pycache__
	rm -rf dist
	rm -rf build
	rm -rf venv-dev
	rm -rf .mypy_cache
	rm -rf .pytest_cache

test: lint style

lint:
	pytest --pylint --pylint-rcfile=.pylintrc --pylint-error-types=CWEF

style:
	flake8
	mypy livetrackbot
