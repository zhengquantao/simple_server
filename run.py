from flask import Flask, request
import os
import requests
import redis
import psutil
import datetime


app = Flask(__name__)


@app.route("/index/")
def index():
    user = os.environ.get("USER")
    password = os.environ.get("PASS")
    return f"{user}_{password}"


@app.route("/version/")
def version():
    env = os.environ.get("ENV")
    version = os.environ.get("WEBVERSION")
    return f"{env}_{version}"


@app.route("/get_url/")
def get_url():
    url = request.args.get("url", "https://www.baidu.com")
    cnt = request.args.get("cnt", 10)
    start_cpu = get_mem_cpu()
    count = get_request_data(url, cnt=int(cnt))
    end_cpu = get_mem_cpu()
    netstat = get_netstat()

    return f"请求成功数量：{count} | 当前网络连接数：{netstat} | 开始CPU: {start_cpu} 结束CPU: {end_cpu}"


def get_request_data(url: str, cnt=10) -> int:
    count = 0
    for i in range(cnt):
        r = requests.get(url)
        if r.status_code == 200:
            count += 1
    return count


@app.route("/get_redis/")
def get_redis():
    redis_url = request.args.get("url", "https://www.baidu.com")
    cnt = request.args.get("cnt", 10000)
    key = request.args.get("key", "key")
    start_cpu = get_mem_cpu()
    count = get_redis_data(redis_url, key, cnt=int(cnt))
    end_cpu = get_mem_cpu()
    netstat = get_netstat()
    return f"请求成功数量：{count} | 当前网络连接数：{netstat} | 开始CPU: {start_cpu} 结束CPU: {end_cpu}"


def get_redis_data(redis_url: str, key: str, cnt=10000) -> int:
    count = 0
    rc = redis_conn(redis_url)
    rc.set(key, 1)
    for i in range(cnt):
        r = rc.get(key)
        if r:
            count += 1
    return count


def get_mem_cpu() -> str:
    data = psutil.virtual_memory()
    total = data.total #总内存,单位为byte
    free = data.available #可以内存
    memory = "Memory:%d"%(int(round(data.percent)))+"%"+" "
    cpu = "CPU:%0.2f"%psutil.cpu_percent(interval=1)+"%"
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + memory + cpu


def get_netstat() -> str:
    netstat = psutil.net_connections()
    ESTABLISHED = 0
    TIME_WAIT = 0
    CLOSE_WAIT = 0
    for sconn in netstat:
        if sconn.status == 'ESTABLISHED':
            ESTABLISHED += 1
        elif sconn.status == 'TIME_WAIT':
            TIME_WAIT += 1
        elif sconn.status == 'CLOSE_WAIT':
            CLOSE_WAIT += 1

    return f"ESTABLISHED:{ESTABLISHED} TIME_WAIT:{TIME_WAIT} CLOSE_WAIT:{CLOSE_WAIT}"


def redis_conn(redis_url: str) -> object:
    obj_conn = redis.StrictRedis().from_url(redis_url)
    return obj_conn

    
if __name__ == '__main__':
    app.run(port=5001, debug=True)