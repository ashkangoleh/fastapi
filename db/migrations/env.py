import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context
from decouple import config
from db.database import Base

DB_USER = config('POSTGRES_USER')
DB_PASSWORD = config('POSTGRES_PASSWORD')
DB_ADDRESS=config('POSTGRES_ADDRESS')
DB_NAME = config('POSTGRES_DB')

config = context.config

fileConfig(config.config_file_name)

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base_dir)


target_metadata = Base.metadata

def get_url():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}"

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def render_item(type_, obj, autogen_context):
    if type_ == 'type' and isinstance(obj, sqlalchemy_utils.types.choice.ChoiceType):
        autogen_context.imports.add("import sqlalchemy_utils")
        col_type = "sqlalchemy_utils.types.choice.ChoiceType({})"
        return col_type.format(obj.choices)
    return False

def run_migrations_online():
    connectable = create_engine(get_url())

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []


    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
            process_revision_directives=process_revision_directives,
            # **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()