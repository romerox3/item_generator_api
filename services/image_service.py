from diffusers import StableDiffusionPipeline, __version__ as diffusers_version
from diffusers import StableDiffusionXLPipeline
import os
from tqdm import tqdm
import logging
from rembg import remove
from PIL import Image
import io
import torch
import gc
import cv2
import numpy as np
import base64
from config import Config

logger = logging.getLogger(__name__)

logger.info("Configurando rutas de caché")
os.environ['TRANSFORMERS_CACHE'] = '/root/.cache/huggingface'
os.environ['HF_HOME'] = '/root/.cache/huggingface'

logger.info(f"Versión de diffusers: {diffusers_version}")

class ImageService:

    def __init__(self):
        logger.info("Inicializando ImageService")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo seleccionado: {self.device}")
        
        model_id = Config.DIFFUSION_MODEL
        logger.info(f"Cargando modelo de difusión: {model_id}")
        
        if Config.DIFFUSION_MODEL == 'animate-diff':
            logger.warning("ImageService inicializado, pero no se cargará el modelo stable-diffusion")
            return

        self.model = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        ).to(self.device)
        
        logger.info(f"Modelo {model_id} cargado correctamente")

    def generate_image(self, prompt, item_info):
        base_prompt = (
            f"A single {item_info['item_type']} in RPG style, 2D illustration. "
            f"The {item_info['item_type']} is made of {item_info['material']} "
            f"with {item_info['color']} color accents. "
            f"It has a {item_info['keyword']} feature or design element. "
            f"Isometric view, transparent background, detailed with sharp edges and soft shading. "
            f"High-quality game asset suitable for an RPG inventory icon. "
            f"Only one {item_info['item_type']} in the image, centered composition."
        )
        logger.info(f"Prompt utilizado: {base_prompt}")
        logger.info(f"Descripción del objeto: {prompt}")
        progress_bar = tqdm(total=self.steps, desc="Generando imagen", unit="paso")

        def callback_function(step: int, timestep: int, latents: torch.FloatTensor):
            progress_bar.update(1)
            logger.info(f"Progreso de generación de imagen: {step}/{self.steps} pasos")

        try:
            logger.info("Iniciando la generación de la imagen")
            result = self.model(
                prompt=base_prompt,
                negative_prompt="multiple items, group of items, collection, low quality, blurry, pixelated, rough, simplistic",
                num_inference_steps=50,
                guidance_scale=7.5,
                callback=callback_function,
                callback_steps=1,
                height=512,
                width=512
            )
            logger.info("Generación de imagen completada")
            
            if result.images is None or len(result.images) == 0:
                raise ValueError("La generación de imagen falló y devolvió un resultado inválido")
            
            image = result.images[0]
            logger.info("Imagen extraída del resultado")
            progress_bar.close()
            logger.info("Barra de progreso cerrada")
            return image
        except Exception as e:
            logger.error(f"Error al generar la imagen: {str(e)}")
            logger.error(f"Tipo de excepción: {type(e).__name__}")
            logger.error("Traceback completo:", exc_info=True)
            progress_bar.close()
            return None
        finally:
            logger.info("Finalizando la función generate_image")
            torch.cuda.empty_cache()
            gc.collect()

    def remove_background(self, image):
        logger.info("Eliminando el fondo de la imagen")
        return remove(image)

    def isolate_largest_object(self, image):
        logger.info("Aislando el objeto más grande de la imagen")
        
        # Convertir la imagen PIL a un array de numpy
        np_image = np.array(image)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        
        # Aplicar umbral
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Encontrar el contorno más grande
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Crear una máscara para el objeto más grande
        mask = np.zeros(thresh.shape, np.uint8)
        cv2.drawContours(mask, [largest_contour], 0, 255, -1)
        
        # Aplicar la máscara a la imagen original
        result = cv2.bitwise_and(np_image, np_image, mask=mask)
        
        # Convertir de vuelta a imagen PIL
        result_pil = Image.fromarray(result)
        
        return result_pil

    def process_image(self, prompt, object_id, item_info):
        logger.info(f"Procesando imagen para objeto ID: {object_id}")
        logger.info(f"Prompt completo: {prompt}")
        image = self.generate_image(prompt, item_info)
        if image is None:
            logger.error("No se pudo generar la imagen")
            return None
        logger.info("Imagen generada exitosamente")
        
        object_name = f"{object_id}.png"
        image_url, image_base64 = self.save_image_locally(image, object_name)
        
        image_no_bg = self.remove_background(image)
        object_name_no_bg = f"{object_id}_no_bg.png"
        image_url_no_bg, image_no_bg_base64 = self.save_image_locally(image_no_bg, object_name_no_bg)
        logger.info("Fondo de la imagen removido")
        
        isolated_image = self.isolate_largest_object(image_no_bg)
        logger.info("Objeto más grande aislado")
        object_name_isolated = f"{object_id}_isolated.png"
        image_isolated_url, image_isolated_base64 = self.save_image_locally(isolated_image, object_name_isolated)
        logger.info(f"Imagen con objeto aislado guardada localmente: {image_isolated_url}")
        
        return {
            "no_bg_image_url": image_url_no_bg,
            "no_bg_image_base64": image_no_bg_base64,
            "base_image_url": image_url,
            "base_image_base64": image_base64,
            "isolated_image_url": image_isolated_url,
            "isolated_image_base64": image_isolated_base64
        }

    def save_image_locally(self, image, object_name):
        logger.info(f"Guardando imagen localmente: {object_name}")
        img_path = os.path.join('/app/images', object_name)
        image.save(img_path, format='PNG')
        
        # Convertir la imagen a base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"/images/{object_name}", img_str

image_service = ImageService()