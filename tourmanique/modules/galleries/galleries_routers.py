from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from tourmanique.domain import Gallery
from tourmanique.helpers.s3_helper import S3Helper


from tourmanique.modules.auth.is_user_has_access import IsUserHasAccess
from tourmanique.modules.galleries.commands.delete_gallery_command import DeleteGalleryCommand

from tourmanique.modules.galleries.commands.restore_gallery_command import RestoreGalleryCommand
from tourmanique.modules.galleries.commands.new_gallery_command import NewGalleryCommand
from tourmanique.modules.galleries.commands.update_gallery_command import UpdateGalleryCommand
from tourmanique.modules.galleries.queries.get_gallery_query import GetGalleryQuery
from tourmanique.modules.galleries.schemes.validation_gallery_name import ValidationGalleryName

from tourmanique.modules.photos.commands.sorting_params import SortingParams
from tourmanique.modules.photos.queries.get_photos_query import GetPhotoQuery
from tourmanique.modules.photos.queries.get_sorted_photos import GetSortedPhotosQuery


galleries_blueprint = Blueprint('galleries', __name__, url_prefix='/galleries')


@galleries_blueprint.route('/', methods=['POST'])
@jwt_required()
def add_gallery():
    current_user_id = get_jwt_identity()
    validation_param = ValidationGalleryName(gallery_name=request.json.get('name'))
    if not IsUserHasAccess().to_service(current_user_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN

    gallery_entity = {
                      'name': validation_param.gallery_name,
                      'user_id': current_user_id,
                      }

    try:
        gallery_entity = Gallery(**gallery_entity)
        gallery_id = NewGalleryCommand.create(gallery_entity)

        return jsonify(gallery_id), HTTPStatus.CREATED

    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST


@galleries_blueprint.route('/<int:gallery_id>/rename/', methods=['POST'])
@jwt_required()
def rename_gallery(gallery_id):
    current_user_id = get_jwt_identity()
    try:
        validation_param = ValidationGalleryName(gallery_name=request.json.get('newName'))
    except ValidationError as err:
        return jsonify(err.errors()), HTTPStatus.BAD_REQUEST

    if not GetGalleryQuery.by_id(gallery_id):
        return jsonify({'msg': 'Not Found'}), HTTPStatus.NOT_FOUND
    if not IsUserHasAccess().to_gallery(current_user_id, gallery_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN
    try:
        UpdateGalleryCommand().rename(validation_param.gallery_name, gallery_id)
        return jsonify({'msg': 'OK'}), HTTPStatus.OK

    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST


@galleries_blueprint.route('/<int:gallery_id>/', methods=['DELETE'])
@jwt_required()
def delete_gallery(gallery_id):
    current_user_id = get_jwt_identity()
    if not GetGalleryQuery.by_id(gallery_id):
        return jsonify({'msg': 'Not Found'}), HTTPStatus.NOT_FOUND
    if not IsUserHasAccess.to_gallery(current_user_id, gallery_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN
    try:
        DeleteGalleryCommand().delete(gallery_id)
        return jsonify(gallery_id), HTTPStatus.OK

    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST


@galleries_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_galleries():
    current_user_id = get_jwt_identity()
    if not IsUserHasAccess().to_service(current_user_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN
    try:
        galleries_list = GetGalleryQuery().by_user_id(current_user_id)
        result = []

        for gallery in galleries_list:
            photos_list = GetPhotoQuery().for_gallery_preview(gallery.id)
            photos_links = list(map(lambda photo: {
                'photoPath': S3Helper().s3_get_full_file_url(photo.photo_file_path_s3)
            }, photos_list))
            result.append({'id': gallery.id,
                           'name': gallery.name,
                           'photosCount': GetPhotoQuery.count_photos(gallery.id),
                           'previewPhotos': photos_links
                           })
        return jsonify(result), HTTPStatus.OK
    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST


@galleries_blueprint.route('/<int:gallery_id>/restore/', methods=['POST'])
@jwt_required()
def restore_gallery(gallery_id):
    current_user_id = get_jwt_identity()
    if not GetGalleryQuery().deleted_by_id(gallery_id):
        return jsonify({'msg': 'Not Found'}), HTTPStatus.NOT_FOUND
    if not IsUserHasAccess().to_gallery(current_user_id, gallery_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN

    try:
        RestoreGalleryCommand().restore(gallery_id)
        return jsonify({'msg': 'OK'}), HTTPStatus.OK

    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST


@galleries_blueprint.route('/<int:gallery_id>/photos', methods=['GET'])
@jwt_required()
def get_photos(gallery_id):
    current_user_id = get_jwt_identity()
    if not GetGalleryQuery().by_id(gallery_id):
        return jsonify({'msg': 'Not Found'}), HTTPStatus.NOT_FOUND
    if not IsUserHasAccess().to_gallery(current_user_id, gallery_id):
        return jsonify({'msg': 'Forbidden'}), HTTPStatus.FORBIDDEN
      
    params = SortingParams(offset=request.args.get('offset'),
                           limit=request.args.get('limit'),
                           sorted_by=request.args.get('sortedBy'))
    photos_sorted = GetSortedPhotosQuery().get_sorted_photos(gallery_id,
                                                             params.sorted_by,
                                                             params.offset,
                                                             params.limit)
    result = []
    try:
        for photo in photos_sorted:
            result.append(
                {
                    'id': photo.id,
                    'photoPath': S3Helper().s3_get_full_file_url(photo.photo_file_path_s3),
                    'uniqueness': photo.overall_uniqueness,
                }
            )
        return jsonify({
            'list': result,
            'totalNumberOfItems': GetPhotoQuery().count_photos(gallery_id)
        }), HTTPStatus.OK 
    except Exception as err:
        return jsonify(str(err)), HTTPStatus.BAD_REQUEST
