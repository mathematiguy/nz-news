DOCKER_REGISTRY := mathematiguy
IMAGE_NAME := $(shell basename `git rev-parse --show-toplevel`)
IMAGE := $(DOCKER_REGISTRY)/$(IMAGE_NAME)
GIT_TAG ?= $(shell git log --oneline | head -n1 | awk '{print $$1}')
RUN ?= docker run $(DOCKER_ARGS) --rm -v $$(pwd):/work -w /work -u $(UID):$(GID) $(IMAGE)
UID ?= $(shell id -u)
GID ?= $(shell id -g)
LOG_LEVEL ?= INFO

.PHONY: crawl jupyter clean docker docker-push enter enter-root

crawl: data/nzherald.json

.PRECIOUS: data/nzherald.json
data/nzherald.json:
	$(RUN) scrapy crawl nzherald -o data/nzherald.json -t jsonlines  --loglevel $(LOG_LEVEL)

JUPYTER_PASSWORD ?= jupyter
JUPYTER_PORT ?= 8888
jupyter: UID=root
jupyter: GID=root
jupyter: DOCKER_ARGS=-u $(UID):$(GID) --rm -it -p $(JUPYTER_PORT):$(JUPYTER_PORT) -e NB_USER=$$USER -e NB_UID=$(UID) -e NB_GID=$(GID)
jupyter:
	$(RUN) jupyter lab \
		--allow-root \
		--port $(JUPYTER_PORT) \
		--ip 0.0.0.0 \
		--NotebookApp.password=$(shell $(RUN) \
			python3 -c \
			"from IPython.lib import passwd; print(passwd('$(JUPYTER_PASSWORD)'))")

clean:
	rm -f data/nzherald_ids.txt data/nzherald.json

docker:
	docker build --tag $(IMAGE):$(GIT_TAG) .
	docker tag $(IMAGE):$(GIT_TAG) $(IMAGE):latest

docker-push:
	docker push $(IMAGE):$(GIT_TAG)

enter: DOCKER_ARGS=-it
enter:
	$(RUN) bash

enter-root: DOCKER_ARGS=-it
enter-root: UID=root
enter-root: GID=root
enter-root:
	$(RUN) bash
