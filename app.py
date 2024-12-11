from flask import Flask
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_migrate import Migrate
import torch
import logging
import os
from flask import send_from_directory
from config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ma = Marshmallow()
migrate = Migrate()

def verificar_gpu():
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA disponible: {torch.cuda.is_available()}")
    logger.info(f"Número de GPUs: {torch.cuda.device_count()}")

    logger.info(f"CUDA version: {torch.version.cuda}")
    logger.info(f"cuDNN version: {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else 'No disponible'}")
    logger.info(f"CUDA arch list: {torch.cuda.get_arch_list() if torch.cuda.is_available() else 'No disponible'}")

    if torch.cuda.is_available():
        logger.info(f"GPU actual: {torch.cuda.get_device_name(0)}")
        logger.info(f"Índice de la GPU actual: {torch.cuda.current_device()}")
    else:
        logger.warning("No se detectó ninguna GPU. Se usará la CPU.")
        logger.info(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'No establecido')}")
        logger.info(f"NVIDIA_VISIBLE_DEVICES: {os.environ.get('NVIDIA_VISIBLE_DEVICES', 'No establecido')}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Dispositivo seleccionado: {device}")
    return device

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = '/app/images'
    app.add_url_rule('/images/<filename>', 'uploaded_file',
                     lambda filename: send_from_directory(app.config['UPLOAD_FOLDER'], filename))

    ma.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        from routes import register_blueprints
        register_blueprints(app)

    return app

app = create_app()
device = verificar_gpu()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)