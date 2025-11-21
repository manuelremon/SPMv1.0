import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend_v2.core.config import Settings
from backend_v2.core.base import Base

config = context.config
# Guard logging config as our alembic.ini may not have logging sections
try:
    fileConfig(config.config_file_name)
except Exception:
    pass

target_metadata = Base.metadata


def run_migrations_offline():
    url = Settings.DB_URL
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = Settings.DB_URL
    connectable = engine_from_config(configuration, prefix='sqlalchemy.', poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
