# Makefile is modified from that written by user "oneself" and edited by
# Matt Ryall at https://stackoverflow.com/a/46188210
venv: .venv/touchfile

.venv/touchfile: requirements.txt
	test -d .venv || python3 -m venv .venv # TODO: analyze key project dependencies and set Python minor version accordingly.
	. .venv/bin/activate; pip install -Ur requirements.txt
	touch .venv/touchfile

run: venv
	. .venv/bin/activate; .venv/bin/flask --app src/flaskr run --debug

# For devs wanting to mirror a complete CI run locally before pushing to GitHub
all-checks: style-check static lint test
	echo "Done"

# Pytest command to run all unit/integration tests.
# For running only a subset of all tests, invoke pytest
# directly (after activating the venv).
#
# Example:
# pytest ./tests/example/test_example.py
#
# Consult with the Pytest documentation for other use cases:
# https://docs.pytest.org/en/stable/how-to/usage.html#usage
test: venv
	. .venv/bin/activate; pytest ./tests

lint: venv
	. .venv/bin/activate; .venv/bin/pylint tests/* src/**/*.py

# Static typing analysis
static: venv
	. .venv/bin/activate; .venv/bin/mypy --pretty tests/**/*.py src/**/*.py

# Run import sort and opionated Python formatting
style-fix: venv
	. .venv/bin/activate; .venv/bin/isort tests src
	. .venv/bin/activate; .venv/bin/black tests src

style-check: venv
	. .venv/bin/activate; .venv/bin/isort tests src --check --verbose
	. .venv/bin/activate; .venv/bin/black tests src --check --verbose

docker-run:
	sudo docker compose -f ./docker/dev/docker-compose.yml up -d

# Does not remove data
docker-down:
	sudo docker compose -f ./docker/dev/docker-compose.yml down

# Removes all data
docker-clean: docker-down
	sudo docker volume rm cuecode-dev_pgdata cuecode-dev_pgadmindata

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete
	find -iname "*__pycache__" -exec rm -r {} +
	find -iname "*.pytest_cache" -exec rm -r {} +
	find -iname "*.mypy_cache" -exec rm -r {} +
	
	