from ma import ma
from models.item import ItemModel
from models.store import StoreModel
from schemas.item import ItemSchema


class StoreSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        include_fk = True
        load_instance = True
