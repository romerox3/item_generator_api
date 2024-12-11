import random
import logging
import re
from .item_generator_service import ItemGenerator

logger = logging.getLogger(__name__)

class ItemService:
    def __init__(self):
        self.generator = ItemGenerator()

    def generate_item(self, keyword):
        logger.info(f"Iniciando generación de objeto para la palabra clave: {keyword}")
        
        descripcion = self.generator.generate_item_description(keyword)
        logger.info(f"Descripción generada: {descripcion}")
        
        info_objeto = self.generator.extract_item_info(descripcion)
        logger.info(f"Información del objeto extraída: {info_objeto}")
        
        return {
            "descripcion": descripcion,
            "info_objeto": info_objeto
        }

item_service = ItemService()