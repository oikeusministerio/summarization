FROM python:3
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y \
  poppler-utils
RUN pip install -r requirements.txt
ENTRYPOINT ["/bin/bash"]
CMD ["start.sh"]