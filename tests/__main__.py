import sys

import pytest


def run_all():
    """Run all tests in the tests/ directory."""
    print("Running all tests...")
    pytest.main(["."])
    # sys.exit(pytest.main(["-x", "tests"]))


if __name__ == "__main__":
    run_all()
