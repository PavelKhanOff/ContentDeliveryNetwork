FROM python:3.8.5-slim-buster



ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN  apt-get update -y &&  apt-get install -y libvips-dev && apt-get install -y ffmpeg &&  apt-get install -y redis-server
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt



COPY . /eduone_cdn

ENV PATH=$PATH:/eduone_cdn/
ENV PYTHONPATH /eduone_cdn/

CMD ["gunicorn", "--workers=3", "-b 0.0.0.0:9000", "-k uvicorn.workers.UvicornWorker", "main:app"]
