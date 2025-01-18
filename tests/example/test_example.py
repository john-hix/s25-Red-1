"""Example unit tests
Example adapted from https://github.com/hamcrest/PyHamcrest/blob/main/README.rst
on Jan 18, 2025
"""

from hamcrest import assert_that, equal_to


def test_example():
    """An example test function with a Hamcrest style assertion. The function name
    must be prefixed with 'test_'."""

    assert_that(True, equal_to(True))
