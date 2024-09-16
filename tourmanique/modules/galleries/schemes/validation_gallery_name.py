from pydantic import BaseModel, validator, ValidationError


class ValidationGalleryName(BaseModel):
    gallery_name: str

    @validator('gallery_name')
    def validate_gallery_name(cls, gallery_name: str) -> str:
        gallery_name = gallery_name.strip()
        if gallery_name == '':
            raise ValueError('Gallery name must not be empty.')
        return gallery_name
