FROM python:3.10-alpine
# RUN apk add --no-cache bash
# RUN apk add --no-cache curl

WORKDIR /usr/src/

COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./orders/entrypoint.sh ./entrypoint.sh
RUN sed -i 's/\r$//g' entrypoint.sh
RUN chmod +x entrypoint.sh

COPY ./orders .

EXPOSE 8000

ENTRYPOINT ["/usr/src/entrypoint.sh"]
