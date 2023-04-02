FROM python:3.11-slim

LABEL maintainer="Max Mecklin <max@meckl.in>"

COPY . /bot

#COPY docker-entrypoint.sh /docker-entrypoint.sh
#RUN ["chmod", "+x", "/docker-entrypoint.sh"]

WORKDIR /bot

RUN pip3.11 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/bot"

#ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python3.11", "main.py"]