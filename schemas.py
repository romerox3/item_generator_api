from flask_marshmallow import Marshmallow
from dataclass import Item

ma = Marshmallow()

class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'item_type', 'strength_bonus', 'defense_bonus', 'agility_bonus', 'health_bonus', 'dodge_bonus', 'critical_chance_bonus', 'aura', 'no_bg_image_url', 'base_image_url')    

item_schema = ItemSchema()
