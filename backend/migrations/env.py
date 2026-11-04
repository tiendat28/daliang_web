"""Alembic: moi module co schema Postgres rieng, so sanh voi model cua ca he thong."""
from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base
from app.modules import MODULES, load_all_modules

load_all_modules()
target_metadata = Base.metadata

config = context.config
# URL lay tu DATABASE_URL; test (tests/conftest.py) tu dat san URL cua DB _test
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.database_url)


def include_name(name, type_, parent_names):
    # Chi so sanh schema cua cac module (bo qua public va schema he thong)
    if type_ == "schema":
        return name in MODULES
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
        include_schemas=True, include_name=include_name, literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            include_schemas=True, include_name=include_name, compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
