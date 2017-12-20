def mockLoggerFactory(*pargs):
    class MockLogger:
        def debug(*pargs):
            pass

        def info(*pargs):
            pass

        def warn(*pargs):
            pass

        def error(*pargs):
            pass

        def critical(*pargs):
            pass

    return MockLogger
