FROM python:3
MAINTAINER icoz <icoz.vt@gmail.com>

RUN git clone https://github.com/icoz/habraparse.git && cd habraparse && pip install -r requirements.txt

ENTRYPOINT ["python3", "/habraparse/habraparse.py"]
CMD ["-h"]
