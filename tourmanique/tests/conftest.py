import datetime

from flask_jwt_extended import create_access_token
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from application import create_app
import logging

import pytest

from tourmanique.config.config_provider import TestConfigProvider
from tourmanique.domain import Gallery
from tourmanique.domain.data_access_layer.db import db
from tourmanique.modules.auth.auth_routes import USER_ID

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pytest.fixture
def flask_app():
    app = create_app(TestConfigProvider)
    client = app.test_client()
    ctx = app.test_request_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture
def access_token(flask_app):
    access_token = create_access_token(identity=USER_ID,
                                       expires_delta=datetime.timedelta(days=30))
    return access_token


@pytest.fixture
def database_uri(flask_app):
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
    galleries_names = ['gallery_1',
                       'gallery_2',
                       'gallery_3']
    galleries_user_id = ['1',
                         '1',
                         '2']
    galleries_deleted_at_utc = [None,
                         '2023-06-19 06:27:04.065',
                         None]
    galleries_id = [i + 1 for i in range(len(galleries_names))]

    with db_session() as session:
        session.execute(delete(Gallery))
        session.commit()

        logger.info("Deleted test data from the database.")

        for galleries_id, name, user_id, deleted_at_utc in zip(galleries_id,
                                                               galleries_names,
                                                               galleries_user_id,
                                                               galleries_deleted_at_utc):
            session.add(Gallery(id=galleries_id,
                                user_id=user_id,
                                name=name,
                                deleted_at_utc=deleted_at_utc))
        session.commit()

        logger.info("Added test data to the database.")
