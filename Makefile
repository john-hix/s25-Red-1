# Makefile is modified from that written by user "oneself" and edited by
# Matt Ryall at https://stackoverflow.com/a/46188210
venv: .venv/touchfile

.venv/touchfile: requirements.txt
	test -d .venv || python3 -m venv .venv # TODO: analyze key project dependencies and set Python minor version accordingly.
	. .venv/bin/activate; pip install -Ur requirements.txt
	touch .venv/touchfile

run: venv
	. .venv/bin/activate; .venv/bin/flask --app src/flaskr run --debug

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
fix: venv
	. .venv/bin/activate; .venv/bin/isort tests src
	. .venv/bin/activate; .venv/bin/black tests src

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete
	find -iname "*__pycache__" -exec rm -r {} +
	find -iname "*.pytest_cache" -exec rm -r {} +
	find -iname "*.mypy_cache" -exec rm -r {} +
	
	