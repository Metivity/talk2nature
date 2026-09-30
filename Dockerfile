FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 T2N_HOSTED=1 PORT=8080
WORKDIR /app
COPY admin/requirements.lock /app/admin/requirements.lock
RUN pip install --no-cache-dir -r admin/requirements.lock
COPY admin /app/admin
COPY content /app/content
COPY research/resources.json /app/research/resources.json
COPY talk2nature /app/talk2nature
COPY LICENSE NOTICE /app/
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "admin.serve"]
