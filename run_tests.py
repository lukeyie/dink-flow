"""
Simple test runner to run layered tests:
Usage:
  python run_tests.py unit        # run fast unit tests
  python run_tests.py integration # run integration tests (slower)
  python run_tests.py all         # run all tests via unittest discovery
"""
import sys
import unittest

UNIT_TESTS = [
    "tests.test_select_fun_simple",
    "tests.test_fallback_behavior",
]
INTEGRATION_TESTS = [
    "tests.test_dinkup_bot",
]

if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    loader = unittest.defaultTestLoader
    runner = unittest.TextTestRunner(verbosity=2)
    if mode == "unit":
        suites = [loader.loadTestsFromName(name) for name in UNIT_TESTS]
        suite = unittest.TestSuite(suites)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    elif mode == "integration":
        suites = [loader.loadTestsFromName(name) for name in INTEGRATION_TESTS]
        suite = unittest.TestSuite(suites)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # default: run full discovery
        result = unittest.main(module=None)
        sys.exit(0 if result.result.wasSuccessful() else 1)
