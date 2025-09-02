# Guia do Alembic

## O que é o Alembic

Alembic é uma ferramenta de migração de banco de dados para SQLAlchemy. Ela permite versionar e aplicar mudanças na estrutura do banco de dados de forma controlada e reversível.

## Configuração Inicial

### 1. Instalação

O Alembic já deve estar incluído nas dependências do projeto. Caso não esteja:

```bash
pip install alembic
```

### 2. Inicialização do Alembic

Se o Alembic ainda não foi configurado no projeto:

```bash
alembic init migrations
```

### 3. Configuração do arquivo `alembic.ini`

Exemplo de configuração da URL do banco de dados no arquivo `alembic.ini`:

```ini
[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
timezone = America/Sao_Paulo

# max length of characters to apply to the
# "slug" field
truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
sourceless = false

# version number format
version_num_format = %04d

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
version_path_separator = os

# the output encoding used when revision files
# are written from script.py.mako
output_encoding = utf-8

sqlalchemy.url = postgresql+asyncpg://user:password@localhost/database
```

### 4. Configuração do arquivo `env.py`

Edite o arquivo `alembic/env.py` para usar os modelos do projeto:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Importe seus modelos
from app.database.models.base import Base
from app.core.settings import get_settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    settings = get_settings()
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine and associate a connection with the context."""

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Comandos Básicos do Alembic

### 1. Criar uma nova migração

#### Migração automática (recomendado)

```bash
alembic revision --autogenerate -m "Descrição da migração"
```

#### Migração manual

```bash
alembic revision -m "Descrição da migração"
```

### 2. Aplicar migrações

#### Aplicar todas as migrações pendentes

```bash
alembic upgrade head
```

#### Aplicar migração específica

```bash
alembic upgrade <revision_id>
```

#### Reverter uma migração

```bash
alembic downgrade -1
```

#### Reverter para uma migração específica

```bash
alembic downgrade <revision_id>
```

### 3. Visualizar o estado das migrações

#### Ver histórico de migrações

```bash
alembic history
```

#### Ver migração atual

```bash
alembic current
```

#### Ver migrações pendentes

```bash
alembic show <revision_id>
```

## Exemplos de Uso no Projeto

### 1. Adicionando uma nova tabela

Após adicionar um novo modelo em `app/database/models/base.py`:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

Gere a migração:

```bash
alembic revision --autogenerate -m "Add users table"
```

### 2. Modificando uma tabela existente

Após modificar um modelo:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)  # Nova coluna
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

Gere a migração:

```bash
alembic revision --autogenerate -m "Add phone column to users table"
```

### 3. Aplicando migrações em desenvolvimento

```bash
# Aplicar todas as migrações
alembic upgrade head

# Verificar status
alembic current
```

### 4. Aplicando migrações em produção

```bash
# Sempre fazer backup antes!
# Ver quais migrações serão aplicadas
alembic history

# Aplicar migrações
alembic upgrade head
```

## Boas Práticas

### 1. Sempre revisar migrações autogenerate

- O Alembic pode não detectar todas as mudanças automaticamente
- Sempre revise o arquivo de migração gerado antes de aplicar
- Teste as migrações em ambiente de desenvolvimento primeiro

### 2. Nomenclatura de migrações

Use descrições claras e concisas:

```bash
alembic revision --autogenerate -m "Add user authentication tables"
alembic revision --autogenerate -m "Update job status enum values"
alembic revision --autogenerate -m "Create indexes for performance optimization"
```

### 3. Migrações de dados

Para migrações que envolvem transformação de dados, use migrações manuais:

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Estrutura
    op.add_column('users', sa.Column('full_name', sa.String(500)))

    # Dados
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = CONCAT(first_name, ' ', last_name)"
    )

    # Cleanup
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade():
    # Reverter mudanças
    op.add_column('users', sa.Column('first_name', sa.String(255)))
    op.add_column('users', sa.Column('last_name', sa.String(255)))

    connection = op.get_bind()
    connection.execute("""
        UPDATE users
        SET first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = SPLIT_PART(full_name, ' ', 2)
    """)

    op.drop_column('users', 'full_name')
```
