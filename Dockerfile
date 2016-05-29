FROM  python:3.4

MAINTAINER valsdav valsdav@wikitolearn.org

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY journal-api.py .

ENTRYPOINT ["python"]
CMD ["journal-api.py"]
