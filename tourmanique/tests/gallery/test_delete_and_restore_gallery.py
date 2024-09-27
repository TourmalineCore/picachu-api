from http import HTTPStatus

from flask import url_for
import pytest


def test_successfully_delete_and_restore_gallery_if_token_is_valid(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    deleted_gallery = flask_app.delete(url_for('api.galleries.delete_gallery', gallery_id=1), headers=headers)
    restored_gallery = flask_app.post(url_for('api.galleries.restore_gallery', gallery_id=1), headers=headers)

    assert deleted_gallery.status_code == HTTPStatus.OK
    assert deleted_gallery.json == 1
    assert restored_gallery.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'invalid_access_token',
    [
        ("Bearer ''"),
        ("Bearer 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'"),
    ]
    )
def test_cant_delete_and_restore_gallery_if_token_is_invalid(
        flask_app,
        invalid_access_token,
        db_with_test_data,
        ):

    headers = {
        "Authorization": f"{invalid_access_token}"
    }

    deleted_gallery = flask_app.delete(url_for('api.galleries.delete_gallery', gallery_id=1), headers=headers)
    restored_gallery = flask_app.post(url_for('api.galleries.restore_gallery', gallery_id=1), headers=headers)

    assert deleted_gallery.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert restored_gallery.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_cant_delete_and_restore_gallery_if_gallery_belongs_to_another_user(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    deleted_gallery = flask_app.delete(url_for('api.galleries.delete_gallery', gallery_id=3), headers=headers)
    restored_gallery = flask_app.post(url_for('api.galleries.restore_gallery', gallery_id=3), headers=headers)

    assert deleted_gallery.status_code == HTTPStatus.FORBIDDEN
    assert restored_gallery.status_code == HTTPStatus.NOT_FOUND


def test_cant_delete_gallery_if_it_already_deleted(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    deleted_gallery = flask_app.delete(url_for('api.galleries.delete_gallery', gallery_id=2), headers=headers)

    assert deleted_gallery.status_code == HTTPStatus.NOT_FOUND


def test_cant_delete_and_restore_gallery_if_it_nonexistent(
        flask_app,
        db_with_test_data,
        access_token):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    deleted_gallery = flask_app.delete(url_for('api.galleries.delete_gallery', gallery_id=4), headers=headers)
    restored_gallery = flask_app.post(url_for('api.galleries.restore_gallery', gallery_id=4), headers=headers)

    assert deleted_gallery.status_code == HTTPStatus.NOT_FOUND
    assert restored_gallery.status_code == HTTPStatus.NOT_FOUND
