DOCKER_REGISTRY := docker.dragonfly.co.nz
IMAGE_NAME := $(shell basename `git rev-parse --show-toplevel`)
IMAGE := $(DOCKER_REGISTRY)/$(IMAGE_NAME)
GIT_TAG ?= $(shell git log --oneline | head -n1 | awk '{print $$1}')
RUN ?= docker run $(INTERACT) --rm -v $$(pwd):/work -w /work -u $(UID):$(GID) $(IMAGE)
UID ?= $(shell id -u)
GID ?= $(shell id -g)

crawl: news/nzherald_ids.txt
	cd news && $(RUN) scrapy crawl nzherald -o nzherald.json -t jsonlines

news/nzherald_ids.txt: news/nzherald.json
	$(RUN) cat $< | \
		   grep -oE 'objectid=[0-9]+' | \
		   grep -oE '[0-9]+' | \
		   uniq | \
		   sort > $@

.PHONY: docker
docker:
	docker build --tag $(IMAGE):$(GIT_TAG) .
	docker tag $(IMAGE):$(GIT_TAG) $(IMAGE):latest

.PHONY: docker-push
docker-push:
	docker push $(IMAGE):$(GIT_TAG)

.PHONY: enter
enter: INTERACT=-it
enter:
	$(RUN) bash
