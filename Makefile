# Makefile to simplify test and build.

.PHONY: all run-followus run-alpsfreeride run-axlair test clean test-env lint style coverage

all: test

build-base:
	docker build -f Dockerfile.base -t livetrackbot-base .

build: build-base
	docker build -f Dockerfile.code -t livetrackbot-code .

run-docker: build
	docker run -d \
	--restart=always \
	-v /var/log:/code/logs livetrackbot-code \
	--channel $(channel) --url $(url)

run:
# Check the arguments.
ifndef channel
	$(error Error channel is not set)
endif
ifndef url
	$(error Error url is not set)
endif
	@echo "Starting bot $(name) for channel $(channel) and url $(url)"
	$(MAKE) run-docker

run-followus:
	$(MAKE) run channel="@FollowUsIfYouCan_channel" url="https://livetrack.gartemann.tech/json4Others.php?grp=Cross"

run-alpsfreeride:
	$(MAKE) run channel="@alpsfreeride" url="https://www.alpsfreeride.com/livetracking/json4Others.php"

run-axlair:
	$(MAKE) run channel="@FollowAxlair" url="https://livetrack.gartemann.tech/json4Others.php?pL=Axel"

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
