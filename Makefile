# Makefile is modified from that written by user "oneself" and edited by
# Matt Ryall at https://stackoverflow.com/a/46188210
venv: .venv/touchfile

.venv/touchfile: requirements.txt
	test -d .venv || python3.13 -m venv .venv # TODO: analyze key project dependencies and set Python minor version accordingly.
	. .venv/bin/activate; pip install -Ur requirements.txt
	. .venv/bin/activate; pip install -e .
	touch .venv/touchfile

run: venv node
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

docker-logs:
	sudo docker compose -f ./docker/dev/docker-compose.yml logs -f --tail=200

# Removes all data
docker-clean: docker-down
	sudo docker volume rm cuecode-dev_pgdata cuecode-dev_pgadmindata

# Run the dbmate migrations per their docs in a cross-platform way
# https://github.com/amacneil/dbmate?tab=readme-ov-file#running-migrations
dbmate-up:
	sudo docker run --rm -it --network=host -v "$$(pwd)/db:/db" ghcr.io/amacneil/dbmate --url "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable" up

# Rollback the last dbmate migration per their docs in a cross-platform way
# https://github.com/amacneil/dbmate?tab=readme-ov-file#rolling-back-migrations
dbmate-rollback:
	sudo docker run --rm -it --network=host -v "$$(pwd)/db:/db" ghcr.io/amacneil/dbmate --url "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable" rollback

# Dump the database schema to a file in the local dev environment
# This happens automatically on `up` and `rollback` commands.
# https://github.com/amacneil/dbmate?tab=readme-ov-file#exporting-schema-file
dbmate-dump:
	sudo docker run --rm -it --network=host -v "$$(pwd)/db:/db" ghcr.io/amacneil/dbmate --url "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable" dump

db-seed:
	. .venv/bin/activate; python db/seed/dev_seed.py

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete
	find -iname "*__pycache__" -exec rm -r {} +
	find -iname "*.pytest_cache" -exec rm -r {} +
	find -iname "*.mypy_cache" -exec rm -r {} +
	rm -rf node_modules/
	rm package-lock.json
	
npm:
	npm install