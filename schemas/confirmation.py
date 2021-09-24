from ma import ma
from models.confirmation import ConfirmationModel
from models.user import UserModel


class ConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        include_fk = True
        load_instance = True
