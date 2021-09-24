from marshmallow import fields, Schema
from werkzeug.datastructures import FileStorage


class FileStorageField(fields.Field):
    default_error_message = {"invalid": "Not a valid image"}

    def deserialize(self, value, attr, data, **kwargs) -> FileStorage:
        if value is None:
            return None
        if not isinstance(value, FileStorage):
            self.fail("invalid")
        return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
