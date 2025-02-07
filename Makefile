# Makefile is modified from that written by user "oneself" and edited by
# Matt Ryall at https://stackoverflow.com/a/46188210
venv: .venv/touchfile

.venv/touchfile: requirements.txt
	test -d .venv || python3.13 -m venv .venv # TODO: analyze key project dependencies and set Python minor version accordingly.
	. .venv/bin/activate; pip install -Ur requirements.txt
	. .venv/bin/activate; pip install -e .
	touch .venv/touchfile

run: venv
	. .venv/bin/activate; .venv/bin/flask --app src/app:create_app run --debug

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
#
# GitHub runner info:
# Service containers have their ports mapped to the Runner's localhost interface.
# Source: https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/about-service-containers#running-jobs-on-the-runner-machine
test: venv ci-setup-as-needed
	echo "TODO: set up separate Docker PG with seeds for local integration testing"
	. .venv/bin/activate; pytest --cov=src/app --cov=src/configuration --cov=src/common --cov=src/runtime --cov-report=html ./src

# Assumes dbmate has been installed on the CI runner
ci-setup-as-needed: venv
	[ "$$CI" = "true" ] && cp .env.sample .env || echo "Running locally"
	[ "$$CI" = "true" ] && dbmate --url "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable" up || echo "Skipping migration for local run"


lint: venv
	. .venv/bin/activate; .venv/bin/pylint --load-plugins=pylint_module_boundaries src/**/*.py

# Static typing analysis
static: venv
	. .venv/bin/activate; .venv/bin/mypy --pretty src/**/*.py

# Run import sort and opionated Python formatting
style-fix: venv
	. .venv/bin/activate; .venv/bin/isort --profile black src
	. .venv/bin/activate; .venv/bin/black src

style-check: venv
	. .venv/bin/activate; .venv/bin/isort --profile black src --check
	. .venv/bin/activate; .venv/bin/black src --check

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
	
	
