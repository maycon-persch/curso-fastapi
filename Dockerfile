# Usa a imagem oficial e enxuta do Python 3.14
FROM python:3.14-slim

# Impede que o Python grave arquivos .pyc no disco e força o log no console
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Declaração das variáveis de ambiente (serão preenchidas via .env na execução)
ENV DATABASE_URL=""
ENV SECRET_KEY=""
ENV ALGORITHM=""
ENV ACCESS_TOKEN_EXPIRE_MINUTES=""

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o uv copiando o binário oficial (forma recomendada, segura e muito rápida)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copia os arquivos de gerenciamento de pacotes primeiro (aproveita o cache do Docker)
# Se você tiver um uv.lock, ele também será copiado
COPY pyproject.toml uv.lock* ./

# Instala as dependências do projeto. O `uv sync` criará a venv automaticamente.
RUN uv sync

# Copia o restante do código da sua aplicação (pasta app, etc)
COPY . .

# Expõe a porta 8000, que é a padrão do Uvicorn
EXPOSE 8000

# Executa o comando para subir a API utilizando o uv
# O parâmetro --host 0.0.0.0 é obrigatório no Docker para que a API seja acessível fora do container
CMD ["uv", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]