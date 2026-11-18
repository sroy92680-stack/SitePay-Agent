#Owner::ANIKET::ANHOTRA = MR.Panda
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml README.md /app/
COPY backend /app/backend
RUN python -m pip install --no-cache-dir --disable-pip-version-check .

RUN groupadd -r sitepay && useradd -r -g sitepay -u 10001 sitepay
USER sitepay
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
