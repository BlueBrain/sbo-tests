import pytest
from seleniumbase import BaseCase

@pytest.fixture()
def selbase(request):
    """Defines the basic seleniumbase driver."""

    sb = BaseCase()
    sb.setUp()
    yield sb
    sb.tearDown()
