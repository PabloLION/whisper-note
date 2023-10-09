import sys

import pytest


# TODO:LTR with expensive tests, we should run them only when needed, so split
# run_all_tests into run_expensive_tests and run_cheap_tests
# tests can receive a parameter `request: pytest.FixtureRequest`
def run_all_tests():
    """Run all tests in the tests/ directory."""
    print("Running all tests...")  # no logger to not messes pytest output up
    sys.exit(pytest.main(["-sx", "./tests"]))  # do print, instant exit


if __name__ == "__main__":
    run_all_tests()
