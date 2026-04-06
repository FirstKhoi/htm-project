"""Application configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hms-group03-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'hotel.db')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'test_hotel.db')


# Map config by name
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
