SHELL := /bin/bash
ENV=.venv

.PHONY: init install run migrate create-admin deactivate-expired clean

init:
	python3.10 -m venv $(ENV)
	. $(ENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "The virtual environment is created and dependencies are installed."

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "The dependencies are set."

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

create-admin:
	python app/scripts/create_admin.py

deactivate-expired:
	python app/scripts/deactivate_expired.py

clean:
	rm -rf $(ENV)
	rm -f shortener.db
	rm -rf alembic/versions/*
