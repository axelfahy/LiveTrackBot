# Makefile to simplify test and build.

.PHONY: all test clean test-env lint style coverage

all: test

build-base:
	docker build -f Dockerfile.base -t livetrackbot-base .

build: build-base
	docker build -f Dockerfile.code -t livetrackbot-code .

run-docker: build
	docker run -d \
	--restart=unless-stopped \
	--name=$(channel) \
	--network=monitoring \
	--expose=9095 \
	-l "prometheus.io/scrape=true" \
	-l "prometheus.io/extra-labels=livetrack:$(channel)" \
	-v /var/log:/code/logs livetrackbot-code \
	--channel $(channel) --url $(url)

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
