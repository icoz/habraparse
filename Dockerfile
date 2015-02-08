FROM python:3
MAINTAINER icoz <icoz.vt@gmail.com>

RUN pip install weasyprint
RUN pip install requests
RUN pip install docopt
RUN git clone https://github.com/icoz/habraparse.git

ENTRYPOINT ['python3', '/habraparse/habraparse.py']
CMD ['-h']
