FROM python:3.6
MAINTAINER Wenhui Zhou

RUN pip install --upgrade pip setuptools wheel

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libtiff5-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    python3-opencv


COPY ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY generator.py generator_server.py log.py client.py  video_generator.py yaml_utils.py utils.py ./

CMD ["python3", "generator_server.py"]