import sys

import pytest

from whisper_note import LOG


# TODO:LTR with expensive tests, we should run them only when needed, so split
# run_all_tests into run_expensive_tests and run_cheap_tests
# tests can receive a parameter `request: pytest.FixtureRequest`
def run_all_tests():
    """Run all tests in the tests/ directory."""
    LOG.info("Running all tests...")
    sys.exit(pytest.main(["-sx", "./tests"]))  # do print, instant exit


if __name__ == "__main__":
    run_all_tests()
