import json
from http import HTTPStatus

from flask import url_for
import pytest


def test_successfully_rename_gallery_if_token_is_valid(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    gallery_name = {
        'newName': 'Test Gallery Name',
    }

    gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=1),
                             json=gallery_name,
                             headers=headers)

    assert gallery.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'invalid_access_token',
    [
        "Bearer ''",
        "Bearer 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'",
        "Bearer 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'"
         "eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4NjAyNDk4NCwian'"
         "RpIjoiMzFmYzA0ZWItMmQ1OC00Mzg2LWE1MzctYzAwNDM0N'"
         "jgzYzc3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmI'"
         "joxNjg2MDI0OTg0LCJleHAiOjE2ODg2MTY5ODR9.ITNGqd8O'"
         "jd78m7G7jKr3VTOdxrGuBMKpN6vcjSoQHb'"
    ]
    )
def test_cant_rename_gallery_if_token_is_invalid(
        flask_app,
        invalid_access_token,
        db_with_test_data,
        ):

    headers = {
        "Authorization": f"{invalid_access_token}"
    }
    gallery_name = {
        'newName': 'Test Gallery Name_2',
    }

    gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=1),
                             json=gallery_name,
                             headers=headers)

    assert gallery.json == {'msg': 'Not enough segments'} or {"msg": "Signature verification failed"}


def test_cant_rename_gallery_if_gallery_belongs_to_another_user(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    gallery_name = {
        'newName': 'Test Gallery Name',
    }

    gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=3),
                             json=gallery_name,
                             headers=headers)

    assert gallery.status_code == HTTPStatus.FORBIDDEN


def test_cant_rename_gallery_if_it_already_deleted(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    gallery_name = {
        'newName': 'Test Gallery Name',
    }

    gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=2),
                             json=gallery_name,
                             headers=headers)

    assert gallery.status_code == HTTPStatus.NOT_FOUND


def test_cant_delete_and_restore_gallery_if_it_nonexistent(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    gallery_name = {
        'newName': 'Test Gallery Name',
    }

    gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=4),
                             json=gallery_name,
                             headers=headers)

    assert gallery.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'gallery_name',
    [
        '',
        '     ',
    ]
    )
def test_cant_rename_gallery_if_name_is_empty_or_whitespace_name(
        flask_app,
        gallery_name,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    gallery_name = {
        'newName': gallery_name,
    }

    renaming_gallery = flask_app.post(url_for('api.galleries.rename_gallery', gallery_id=1),
                                      json=gallery_name,
                                      headers=headers)
    gallery_error_message = json.loads(renaming_gallery.text)

    assert renaming_gallery.status_code == HTTPStatus.BAD_REQUEST
    assert gallery_error_message[0]['msg'] == 'Gallery name must not be empty.'
