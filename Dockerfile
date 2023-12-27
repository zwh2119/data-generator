FROM python:3.6
MAINTAINER Wenhui Zhou

COPY ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

#RUN pip install opencv-python==4.4.0.44
#RUN pip install Pillow==8.0.1

COPY generator.py generator_server.py log.py client.py  video_generator.py yaml_utils.py utils.py ./

CMD ["python3", "generator_server.py"]