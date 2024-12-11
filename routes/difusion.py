import logging
from flask import Blueprint, request, jsonify, send_from_directory
from services.item_service import item_service
from services.image_service import image_service
from schemas import ItemSchema
from dataclass import Item
from services.animation_service import animation_service
import json
import os
from flask import Response

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

difusion_bp = Blueprint('difusion', __name__)

@difusion_bp.route('/generar-animacion', methods=['POST'])
def generar_animacion():
    logger.info("Iniciando generación de animación")
    data = request.json
    prompt = data.get('prompt', '')
    num_frames = data.get('num_frames', 16)
    
    if not prompt:
        logger.warning("Solicitud recibida sin prompt")
        return jsonify({"error": "Se requiere un prompt"}), 400
    
    try:
        def generate():
            animation_path, progress = animation_service.generate_animation(prompt, num_frames)
            if animation_path is not None:
                yield json.dumps({
                    "status": "complete",
                    "message": "Animación generada con éxito",
                    "animation_url": f"/images/{os.path.basename(animation_path)}",
                    "progress": 100
                })
            else:
                yield json.dumps({
                    "status": "error",
                    "message": "No se pudo generar la animación",
                    "progress": progress
                })

        return Response(generate(), mimetype='application/json')
    
    except Exception as e:
        logger.error(f"Error al generar la animación: {str(e)}")
        return jsonify({"error": f"Error al generar la animación: {str(e)}"}), 500

@difusion_bp.route('/generar-objeto', methods=['POST'])
def generar_objeto():
    logger.info("Iniciando generación de objeto")
    data = request.json
    palabra_clave = data.get('palabra_clave', '')
    
    if not palabra_clave:
        logger.warning("Solicitud recibida sin palabra clave")
        return jsonify({"error": "Se requiere una palabra clave"}), 400
    
    try:
        resultado_generacion = item_service.generate_item(palabra_clave)
        
        images_data = image_service.process_image(resultado_generacion['descripcion'], resultado_generacion['info_objeto']['id'], resultado_generacion['info_objeto'])
        logger.info(f"Imágenes generadas para el objeto")
        
        if images_data:
            resultado = {
                "message": "Objeto generado con éxito",
                "object": resultado_generacion['info_objeto'],
                "descripcion_en": resultado_generacion['descripcion'],
                "images": {
                    "no_bg_image": images_data['no_bg_image_base64'],
                    "base_image": images_data['base_image_base64'],
                    "isolated_image": images_data['isolated_image_base64']
                }
            }
            
            logger.info(f"Objeto generado exitosamente: {resultado_generacion['info_objeto']['name']}")
            return jsonify(resultado), 201
        else:
            logger.error("No se pudo generar la imagen para el objeto")
            return jsonify({"error": "Error al generar la imagen del objeto"}), 500
    
    except Exception as e:
        logger.error(f"Error al generar el objeto: {str(e)}")
        return jsonify({"error": f"Error al generar el objeto: {str(e)}"}), 500

@difusion_bp.route('/')
def serve_html():
    return send_from_directory('static', 'index.html')
