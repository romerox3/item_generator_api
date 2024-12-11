import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db_game:5432/db_items'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DIFFUSION_MODEL = os.environ.get('DIFFUSION_MODEL', 'animate-diff') 