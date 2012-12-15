SHELL = /bin/bash

.PHONY: init
init: env requirments

env:
	@if [ ! -e "env/bin/activate" ]; \
	then \
		virtualenv --prompt="<paper>" env; \
	fi

requirments:
	@if [ ! -d "env" ]; \
	then \
		echo "no env found"; \
		exit 1; \
	else \
		source env/bin/activate; \
		pip install -U distribute; \
		pip install -U -r deploy/requirments.txt; \
	fi


key:
	./bin/generate_key.py


.PHONY: database
database:
	source env/bin/activate; \
	python application.py syncdb


.PHONY: run
run:
	source env/bin/activate; \
	gunicorn -c deploy/paper_gunicron_conf.py application:app
