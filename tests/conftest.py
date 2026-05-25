def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "smoke: live integration tests that hit external APIs (deselect with -m 'not smoke')",
    )
