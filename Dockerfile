FROM python:3.6.8
RUN mkdir simpleweb
COPY . /simpleweb
WORKDIR /simpleweb
# 升级pip
RUN pip3 install --upgrade pip -i  https://mirrors.aliyun.com/pypi/simple

# pip读取requirements.txt内容安装所需的库
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
CMD ["gunicorn", "-b", ":5000", "-k", "gevent", "run:app"]
