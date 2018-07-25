FROM python:3
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y \
  python-dev zlib1g-dev poppler-utils pstotext \
  flac ffmpeg lame libmad0 libsox-fmt-mp3 \
  libjpeg-dev swig libxslt1-dev antiword unrtf libpulse-dev
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["server.py"]