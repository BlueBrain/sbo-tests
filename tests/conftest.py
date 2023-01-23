import pytest
from seleniumbase import BaseCase
from tests.utils import logger


@pytest.fixture(autouse=True)
def log_test_boundary(request):
    logger.info('Starting test %s', request.node.name.replace('/', '.'))
    yield
    logger.info('Ending test %s', request.node.name.replace('/', '.'))
