FROM python:3.6
MAINTAINER Wenhui Zhou

RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \

ARG OPENCV_VERSION="4.4.0.44"
ARG SYSTEM_CORES="8"
RUN cp /usr/bin/make /usr/bin/make.bak && \
    echo "make.bak --jobs=${SYSTEM_CORES} \$@" > /usr/bin/make && \
    pip install -v opencv-python==${OPENCV_VERSION} && \
    mv /usr/bin/make.bak /usr/bin/make

COPY ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple



COPY generator.py generator_server.py log.py client.py  video_generator.py yaml_utils.py utils.py ./

CMD ["python3", "generator_server.py"]