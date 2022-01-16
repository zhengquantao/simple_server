# Flask简单部署至kubernetes

#### 安装Kubernetes、Docker

[Kubernetes、Docker安装教程](https://gitee.com/zhengquantao/golang/blob/main/k8s%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B/Kubernetes%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B.md)



#### 项目地址

[Github](https://github.com/zhengquantao/simple_server)



#### Flask

* **flask**

  > run.py

  ```python
  from flask import Flask
  import os
  
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
  
  if __name__ == '__main__':
      app.run(host="0.0.0.0", port=5000, debug=True)
  
  ```

  > requirements.txt

  ```txt
  Flask
  gunicorn
  gevent
  greenlet
  ```



#### Docker

* **编写dockerfile**

  > Dockerfile

  ```dockerfile
  FROM python:3.6.8
  RUN mkdir simpleweb
  COPY . /simpleweb
  WORKDIR /simpleweb
  # 升级pip
  RUN pip3 install --upgrade pip -i  https://mirrors.aliyun.com/pypi/simple
  
  # pip读取requirements.txt内容安装所需的库
  RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
  CMD ["gunicorn", "-b", ":5000", "-k", "gevent", "run:app"]
  ```

* **构建docker 镜像**

  ```bash
  docker build -t zhengquantao/simpleweb:latest .
  # 可选命令
  # docker run 执行容器
  # docker exec 进入容器
  # docker tag 重命名
  # docker login 登录
  # docker push 推送到远程仓库
  ```

  

#### Kubernetes

* **ConfigMap**

  **存放配置文件**

  > simpleweb-configmap.yaml  # 

  ```yaml
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: simpleweb-configmap
  data:
    env: "dev"
    webVersion: "v1"
  ```



* **Secret**

  **存放敏感信息，通过base64编码**

  > simpleweb-configmap.yaml

  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: db-user-pass
  type: Opaque
  data:
    username: YWRtaW4=
    password: MWYyZDFlMmU2N2Rm
  ```

* **Deployment**

  **编写pod**

  > simpleweb.yaml

  ```yaml
  apiVersion: apps/v1
  kind: Deployment # 采用deployment部署
  metadata:
    name: simpleweb
    namespace: default # 默认命名空间
    labels:
      app: simpleweb
  spec:
    replicas: 2 # 副本设置1个
    selector:
      matchLabels:
        app: simpleweb
    strategy: # 升级策略，这里副本是一个
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 0
      type: RollingUpdate
    template:
      metadata:
        labels:
          app: simpleweb
      spec:
        containers: #容器相关配置
          - args: # 启动命令
              - gunicorn 
              - -b
              - :5000
              - -k
              - gevent
              - run:app
            env: # 这里通过变量注入的方式配置相关参数，你也可以通过数据挂载的方式将配置挂载到容器指定目录下
              - name: USER
                valueFrom:
                  secretKeyRef:
                    name: db-user-pass
                    key: username
              - name: PASS
                valueFrom:
                  secretKeyRef:
                    name: db-user-pass
                    key: password
              - name: ENV
                valueFrom:
                  configMapKeyRef:
                    name: simpleweb-configmap
                    key: env
              - name: WEBVERSION
                valueFrom:
                  configMapKeyRef:
                    name: simpleweb-configmap
                    key: webVersion
            image: zhengquantao/simpleweb:lastest # 镜像地址
            imagePullPolicy: IfNotPresent  # （IfNotPresent、Never）本地模式有坑,有远程仓库建议使用
            name: simpleweb
            ports: # 暴漏端口
              - containerPort: 5000
                name: tcp5000
                protocol: TCP
            workingDir: /simpleweb
        restartPolicy: Always
        terminationGracePeriodSeconds: 5
  
  ```

  

* **Service**

  **编写service**

  > simplewebsvc.yaml

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: simplewebsvc
    namespace: default
    labels:
      app: simplewebsvc
  spec:
    ports:
      - name: tcp5000
        port: 5000
        protocol: TCP
        targetPort: 5000 # 容器端口
        nodePort: 31111  # 对外暴露端口
    selector:
      app: simpleweb # 指向pod
    type: NodePort
  
  ```

* **执行部署**

  ```bash
  kubectl apply -f simpleweb-secret.yaml
  kubectl apply -f simpleweb-configmap.yaml
  kubectl apply -f simpleweb.yaml
  kubectl apply -f simplewebsvc.yaml
  
  # kubectl get pods|svc 查看pod
  # kubectl create -f 构建pod
  # kubectl delete -f 删除pod
  # kubectl apply -f 存在更新pod,不存在构建pod
  # kubectl describe 查看详情pod
  # kubectl logs 查看pod日志
  # kubectl port-forward pod端口转发
  # kubectl exec 进入pod
  ```

* **验证**

  ``` bash
  curl http://127.0.0.1:31111/index/
  ```

  