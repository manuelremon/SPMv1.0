import os


def pytest_ignore_collect(path, config):
    """Ignore the legacy top-level `tests/` directory unless RUN_ALL_TESTS=1 is set.

    This helps migration: we run the new `version 2` tests by default and preserve the legacy
    suite if a developer wants to run everything locally.
    """
    try:
        strpath = str(path)
        # Normalize path separators
        if os.path.sep + 'tests' + os.path.sep in strpath or strpath.endswith(os.path.sep + 'tests'):
            if os.environ.get('RUN_ALL_TESTS') == '1':
                return False
            return True
    except Exception:
        pass
    return False
