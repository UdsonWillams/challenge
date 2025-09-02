# Customer Management API - FastAPI

> Sistema de gerenciamento de clientes com autenticação JWT e favoritos de produtos

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0a9edc?logo=pytest&logoColor=white)](https://pytest.org/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-000000?logo=python&logoColor=white)](https://docs.astral.sh/ruff/)

API REST para gerenciamento de clientes com sistema de autenticação JWT, favoritos de produtos e integração com APIs externas.

## Funcionalidades

- 🔐 **Autenticação JWT** com roles (admin/user)
- 👥 **Gerenciamento de Clientes** (CRUD completo)
- ⭐ **Sistema de Favoritos** (produtos da API externa)
- 🛡️ **Autorização baseada em roles**
- 🧪 **Testes automatizados** com pytest
- 📦 **Containerização** com Docker
- 📚 **Documentação automática** com Swagger

## Requisitos

- Python 3.12
- Docker & Docker Compose
- **PostgreSQL** (necessário para executar testes localmente)

## Configuração Inicial

1. Clone o repositório:

   ```sh
   git clone https://github.com/udsonwillams/challenge
   cd challenge
   ```

2. Crie o arquivo `.env` com base no `.env.example`:

   ```sh
   cp .env.example .env
   ```

3. Configure as variáveis de ambiente necessárias no `.env`:
   ```env
   SECRET_KEY=sua-chave-secreta-aqui
   POSTGRES_USER=myuser
   POSTGRES_PASSWORD=mypassword
   POSTGRES_DB=challenger_db
   EXTERNAL_PRODUCTS_BASE_URL=https://serverest.dev
   ADMIN_DEFAULT_EMAIL=admin@mail.com
   ADMIN_DEFAULT_PASSWORD=pass@word
   ```

## Executando a Aplicação

### Com Docker (Recomendado)

1. Construa e inicie os contêineres:

   ```sh
   docker-compose up --build
   ```

2. Acesse a aplicação em `http://localhost:8000`

### Localmente (Desenvolvimento)

1. **Instale o PostgreSQL (obrigatório para testes):**

   **Ubuntu/Debian:**

   ```sh
   sudo apt update
   sudo apt install postgresql postgresql-contrib postgresql-client
   ```

   **macOS (com Homebrew):**

   ```sh
   brew install postgresql
   ```

   **Windows:**

   - Baixe e instale do [site oficial do PostgreSQL](https://www.postgresql.org/download/windows/)

2. **Verificar instalação do PostgreSQL:**

   ```sh
   pg_ctl --version
   # Deve retornar a versão instalada
   ```

3. Crie e ative o ambiente virtual:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

4. Instale as dependências:

   ```sh
   pip install -r requirements-dev.txt
   ```

5. Execute as migrações do banco:

   ```sh
   alembic upgrade head
   ```

6. Inicie o servidor:
   ```sh
   uvicorn app.main:app --reload
   # ou
   make runserver
   ```

## Usuário Administrador Padrão

Para criar o usuário administrador inicial, execute:

```sh
python scripts/create_admin.py
```

Credenciais padrão:

- **Email**: admin@mail.com
- **Senha**: pass@word

## Exemplos de Uso da API

### Autenticação

```sh
# Login e obter token JWT
POST /auth/token
{
  "email": "admin@mail.com",
  "password": "pass@word"
}
```

### Gerenciamento de Clientes

```sh
# Criar cliente (público)
POST /customers
{
  "email": "user@example.com",
  "password": "senha123",
  "name": "João Silva"
}

# Listar clientes (apenas admin)
GET /customers
Authorization: Bearer <token>

# Obter cliente específico (próprio usuário ou admin)
GET /customers/{customer_id}
Authorization: Bearer <token>

# Atualizar cliente (próprio usuário ou admin)
PUT /customers/{customer_id}
Authorization: Bearer <token>
{
  "name": "João Santos",
  "email": "joao.santos@example.com"
}

# Deletar cliente (apenas admin)
DELETE /customers/{customer_id}
Authorization: Bearer <token>
```

### Sistema de Favoritos

```sh
# Adicionar produto aos favoritos
POST /customers/{customer_id}/favorites
Authorization: Bearer <token>
{
  "external_id": "123"
}

# Remover produto dos favoritos
DELETE /customers/{customer_id}/favorites/{product_id}
Authorization: Bearer <token>

# Obter perfil com favoritos inclusos
GET /customers/{customer_id}
Authorization: Bearer <token>
```

## Documentação da API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Testes

**⚠️ IMPORTANTE:** Para executar testes, instale o PostgreSQL:

```sh
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-all

# Ou apenas o necessário:
sudo apt install postgresql postgresql-client-common postgresql-common

# Verificar se funcionou:
pg_ctl --version
```

### Executar todos os testes:

```sh
make coverage
```

### Executar com cobertura:

```sh
make coverage
# ou
pytest --cov=app --cov-report=html
```

### Executar testes específicos:

```sh
# Testes de integração
pytest tests/integration/

# Testes de clientes
pytest tests/integration/api/v1/customers/

# Teste específico
pytest tests/integration/api/v1/customers/test_customer.py::test_create_and_get_customer
```

## Estrutura do Projeto

```
app/
├── api/v1/                 # Endpoints da API
│   ├── auth/              # Rotas de autenticação
│   └── customers/         # Rotas de clientes
├── core/                  # Configurações centrais
├── database/              # Modelos e repositórios
│   ├── models/           # Modelos SQLAlchemy
│   └── repositories/     # Padrão Repository
├── schemas/               # Schemas Pydantic
│   ├── auth.py           # Schemas de autenticação
│   └── domain/           # Schemas de domínio
├── services/              # Lógica de negócio
│   ├── auth/             # Serviços de autenticação
│   ├── domain/           # Serviços de domínio
│   └── external/         # Integrações externas
└── exceptions/            # Exceções customizadas
```

## Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Banco de dados relacional
- **JWT** - Autenticação via tokens
- **Pydantic** - Validação de dados
- **pytest** - Framework de testes
- **Docker** - Containerização
- **Alembic** - Migrações de banco

## Ferramentas de Desenvolvimento

- **Ruff** - Linting e formatação
- **pre-commit** - Hooks de commit
- **ipdb** - Debugging
- **pytest-cov** - Cobertura de testes

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
