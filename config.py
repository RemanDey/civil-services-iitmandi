import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'iit_mandi_csc_secret_2026'
    DEBUG = True