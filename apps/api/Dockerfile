FROM python:3.11-slim

# Install system dependencies needed for scientific C-extensions, PyTorch, XGBoost, CatBoost and ReportLab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    "fastapi>=0.111.0" \
    "uvicorn[standard]>=0.30.0" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.3.0" \
    "sqlalchemy>=2.0.30" \
    "alembic>=1.13.0" \
    "psycopg2-binary>=2.9.9" \
    "redis>=5.0.0" \
    "python-jose[cryptography]>=3.3.0" \
    "bcrypt>=4.1.0" \
    "python-multipart>=0.0.9" \
    "numpy>=1.26.0,<2.0.0" \
    "pandas>=2.2.0" \
    "scipy>=1.13.0" \
    "scikit-learn>=1.4.0" \
    "xgboost>=2.0.3" \
    "catboost>=1.2.25" \
    "torch>=2.2.0" \
    "shap>=0.45.0" \
    "statsmodels>=0.14.2" \
    "openpyxl>=3.1.2" \
    "reportlab>=4.2.0" \
    "httpx>=0.27.0" \
    "pytest>=8.2.0"

# Copy application source
COPY app/ ./app/

# Create persistent storage directories
RUN mkdir -p /app/storage/artifacts /app/storage/cache /app/storage/reports

# Ensure non-root or standard environment permissions
ENV PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/app/storage/cache

EXPOSE 8000

# Run database initialization and startup
CMD ["sh", "-c", "python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

