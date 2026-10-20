FROM python:3.15-slim@sha256:2da676046630d7bf14c6764ae1143dc7fa0377a53f94bf5a642f0b214aca5bce
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 T2N_HOSTED=1 PORT=8080
WORKDIR /app
RUN --mount=type=bind,source=.,target=/context python -c 'from pathlib import Path; p=Path("/context"); forbidden=[p/"data",p/"funding",p/"tmp",p/".git",p/"admin/tests",*p.rglob(".env*")]; assert not any(f.exists() for f in forbidden), [str(f) for f in forbidden if f.exists()]; print("Build context excludes private files")'
COPY admin/requirements.lock /app/admin/requirements.lock
RUN pip install --no-cache-dir -r admin/requirements.lock
COPY admin/*.py /app/admin/
COPY admin/schema/*.sql /app/admin/schema/
COPY admin/ui/*.html admin/ui/*.css admin/ui/*.js /app/admin/ui/
COPY content/*.json /app/content/
COPY research/resources.json /app/research/resources.json
COPY talk2nature/*.py /app/talk2nature/
COPY LICENSE NOTICE /app/
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "admin.serve"]
