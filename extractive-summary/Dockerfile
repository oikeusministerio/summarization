FROM python:3
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["./server.py"]
