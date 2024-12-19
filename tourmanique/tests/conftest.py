from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from application import create_app
import logging

import pytest

from tourmanique.config.config_provider import ConfigProvider
from tourmanique.domain import Gallery
from tourmanique.domain.data_access_layer.db import db

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pytest.fixture
def flask_app():
    app = create_app(ConfigProvider)
    client = app.test_client()
    ctx = app.test_request_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture
def database_uri(flask_app):
    print('******************************', flask_app.application.config.get('SQLALCHEMY_DATABASE_URI'))
    return flask_app.application.config.get('SQLALCHEMY_DATABASE_URI')


@pytest.fixture
def db_session(flask_app, database_uri):
    engine = create_engine(
        database_uri,
        isolation_level='READ COMMITTED',
        pool_pre_ping=True,
    )
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )
    return session_factory


@pytest.fixture
def db_with_test_data(db_session):
    galleries_id = ['1',
                    '2',
                    '3']
    galleries_names = ['gallery_1',
                       'gallery_2',
                       'gallery_3']
    galleries_user_id = ['1',
                         '1',
                         '2']

    with db_session() as session:
        session.execute(delete(Gallery))
        session.commit()

        logger.info("Deleted test data from the database.")

        for galleries_id, name, user_id in zip(galleries_id, galleries_names, galleries_user_id):
            session.add(Gallery(id=galleries_id,
                                user_id=user_id,
                                name=name))
        session.commit()

        logger.info("Added test data to the database.")
