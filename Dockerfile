FROM python:3
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y \
  python-dev zlib1g-dev poppler-utils pstotext \
  flac ffmpeg lame libmad0 libsox-fmt-mp3 \
  libjpeg-dev swig libxslt1-dev antiword unrtf \
  libpulse-dev wkhtmltopdf xvfb python-pydot \
  python-pydot-ng graphviz
RUN pip install -r requirements.txt
ENTRYPOINT ["/bin/bash"]
CMD ["start.sh"]