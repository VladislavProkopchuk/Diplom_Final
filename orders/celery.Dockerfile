FROM python:3.11.4
RUN apt update && apt install -y build-essential gcc clang clang-tools cmake python3-dev cppcheck  \
    valgrind afl gcc-multilib

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6

WORKDIR /usr/src/

COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./orders/celery_app/run_celery.sh ./celery_app/run_celery.sh
RUN sed -i 's/\r$//g' ./celery_app/run_celery.sh
RUN chmod +x ./celery_app/run_celery.sh

COPY ./orders .

CMD bash ./celery_app/run_celery.sh