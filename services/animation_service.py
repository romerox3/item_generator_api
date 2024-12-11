from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import torch
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class AnimationService:
    def __init__(self):
        logger.info("Inicializando AnimationService")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        logger.info(f"Dispositivo seleccionado: {self.device}, Tipo de datos: {self.dtype}")
        
        logger.info("hollaallalalalalallalalalalla")

        if Config.DIFFUSION_MODEL != 'animate-diff':
            logger.warning("AnimationService inicializado, pero no se cargará el modelo AnimateDiff")
            return
        
        self.step = 20  # Reducido de 100 a 20
        self.repo = "ByteDance/AnimateDiff-Lightning"
        self.ckpt = f"animatediff_lightning_{self.step}step_diffusers.safetensors"
        self.base = "emilianJR/epiCRealism"
        
        try:
            self.adapter = MotionAdapter().to(self.device, self.dtype)
            adapter_path = hf_hub_download(self.repo, self.ckpt)
            if not os.path.exists(adapter_path):
                raise FileNotFoundError(f"No se encontró el archivo del adaptador: {adapter_path}")
            self.adapter.load_state_dict(load_file(adapter_path, device=self.device))
            
            self.pipe = AnimateDiffPipeline.from_pretrained(
                self.base, 
                motion_adapter=self.adapter, 
                torch_dtype=self.dtype
            ).to(self.device)
            self.pipe.scheduler = EulerDiscreteScheduler.from_config(
                self.pipe.scheduler.config, 
                timestep_spacing="trailing", 
                beta_schedule="linear"
            )
            
            logger.info("Modelo AnimateDiff cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo AnimateDiff: {str(e)}")
            self.pipe = None

    def generate_animation(self, prompt, num_frames=16):
        if self.pipe is None:
            logger.error("El modelo AnimateDiff no se cargó correctamente. No se puede generar la animación.")
            return None, 0

        logger.info(f"Generando animación para prompt: {prompt}")
        try:
            progress = 0
            total_steps = self.step * num_frames
            
            def callback(step: int, timestep: int, latents: torch.FloatTensor):
                nonlocal progress
                progress += 1
                percentage = (progress / total_steps) * 100
                logger.info(f"Progreso de generación de animación: {percentage:.2f}%")

            output = self.pipe(
                prompt=prompt,
                negative_prompt="low quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                num_inference_steps=self.step,
                num_frames=num_frames,
                guidance_scale=7.5,
                callback=callback,
                callback_steps=1
            )
            
            output_path = os.path.join('/app/images', f"{prompt.replace(' ', '_')}.gif")
            export_to_gif(output.frames[0], output_path)
            
            logger.info(f"Animación generada exitosamente y guardada en {output_path}")
            return output_path, 100
        except Exception as e:
            logger.error(f"Error al generar la animación: {str(e)}")
            return None, 0

animation_service = AnimationService()