import os
from alembic.config import Config
from alembic import command

def run_migrations():
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, '..'))
    cfg_path = os.path.join(root, 'alembic.ini')
    alembic_cfg = Config(cfg_path)
    alembic_cfg.set_main_option('script_location', os.path.join(root, 'alembic'))
    # Use DB_URL from Settings
    from backend_v2.core.config import Settings
    alembic_cfg.set_main_option('sqlalchemy.url', Settings.DB_URL)
    command.upgrade(alembic_cfg, 'head')

if __name__ == '__main__':
    run_migrations()
