""" Test fixtures module """
import pytest


@pytest.fixture(scope='session')
def django_db_setup():
    # Disable automatic database configuration
    pass
