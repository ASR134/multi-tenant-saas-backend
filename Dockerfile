FROM python:3.11-slim
# python:3.11-slim is a docker image that contains python 3.11
# start building my image from this existing image

WORKDIR /app
# from this point onward use this dir as the working dir inside the image/container

COPY requirements.txt .
# . is /app

RUN pip install --no-cache-dir -r requirements.txt
# install the packages from reading requirements.txt and don't keep
# pip's downloaded package cache after installation.

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# this command tells docker what to run when the container starts.
# 0.0.0.o means listen on all network interfaces inside the container
