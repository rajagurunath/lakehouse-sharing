#!/usr/bin/make

.DEFAULT_GOAL := help
# COLORS

BOLD := $(shell tput bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM=30

.PHONY: venv
## create a virtual environment for development
venv:
	virtualenv -p python3 env
	source env/bin/activate && \
	pip install pip --upgrade && \
	pip install -r frontend/requirements.txt \
	-r backend/requirements.txt



.PHONY: start_backend_server
## starts prefect server
start_backend_server: venv
## make sure you have docker installed and docker-deamon was up and running
	cd backend/ && python -m uvicorn main:server --reload --app-dir app/


.PHONY: start_frontend_server
## starts prefect agent
start_frontend_server: venv
	cd frontend/ && python -m streamlit run app/main.py



.PHONY: help
## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
