## Projekt létrehozása
1. Jelentkezz be a GitLab-ra
2. A balodali sávon kattints a Projects-re
3. Jobb felül kattints a New Project-re
4. 

## Alkalmazás létrehozása

```Python
from flask import Flask
 
app = Flask(__name__)

@app.route("/health")
def health():
    return "OK"

@app.route("/")
def hello_world():
    return "Hello, World!!"
 
if __name__ == '__main__':  
   app.run(host="0.0.0.0", port=5000)
```

## Dockerfile létrehozása

```Dockerfile
FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY app.py app.py
CMD python -u app.py
```

## Workflow létrehozása
```yaml
default:
  before_script:
    - docker info

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_IMAGE_NAME: $CI_REGISTRY_USER/villabproject

build_image:
  script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin
    - docker build -t $DOCKER_IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $DOCKER_IMAGE_NAME:$CI_COMMIT_SHA
```

## Helm chart-ok létrehozása

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argo-test-app1
spec:
  selector:
    matchLabels:
      app: argo-test-app1
  template:
    metadata:
      labels:
        app: argo-test-app1
    spec:
      containers:
        - name: argo-test-app1
          image: {{ .Values.env.DOCKER_REGISTRY }}/{{ .Values.env.IMAGE_NAME }}:{{ .Values.env.APP_VERSION }}
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          readinessProbe:
            httpGet:
                path: /health
                port: 5000
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            failureThreshold: 3
          livenessProbe:
            httpGet:
                path: /health
                port: 5000
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: argo-test-app1
spec:
  type: LoadBalancer
  ports:
    - port: 5000
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: argo-test-app1
```

```yaml
env:
  APP_VERSION: versionstring
  DOCKER_REGISTRY: registryusername
  IMAGE_NAME: imagename
```

```yaml
apiVersion: v2
name: argo-test-app
description: A Helm chart for Kubernetes

# A chart can be either an 'application' or a 'library' chart.
#
# Application charts are a collection of templates that can be packaged into versioned archives
# to be deployed.
#
# Library charts provide useful utilities or functions for the chart developer. They're included as
# a dependency of application charts to inject those utilities and functions into the rendering
# pipeline. Library charts do not define any templates and therefore cannot be deployed.
type: application

# This is the chart version. This version number should be incremented each time you make changes
# to the chart and its templates, including the app version.
# Versions are expected to follow Semantic Versioning (https://semver.org/)
version: 0.1.0

# This is the version number of the application being deployed. This version number should be
# incremented each time you make changes to the application. Versions are not expected to
# follow Semantic Versioning. They should reflect the version the application is using.
# It is recommended to use it with quotes.
appVersion: "1.16.0"

```

## Workflow kiegészítése a Helm chart módosításával


```yaml
config_argo:
  script:
    - cd helm
    - "sed -i 's|APP_VERSION:.*|APP_VERSION: '$CI_COMMIT_SHA'|' values.yaml"
    - "sed -i 's|DOCKER_REGISTRY:.*|DOCKER_REGISTRY: '$CI_REGISTRY_USER'|' values.yaml"
    - "sed -i 's|IMAGE_NAME:.*|IMAGE_NAME: 'villabproject'|' values.yaml"
    - git config --global user.name 'felhasznaloneved'
    - git config --global user.email '<email_amivel_regisztraltal>'
    - git add values.yaml
    - git commit -m "Update values.yaml"
    - git remote set-url origin http://$GITLAB_USERNAME:$GITLAB_PASSWORD@128.105.146.171:8080/$GITLAB_USERNAME/myproject.git
    - git push origin $(git rev-parse HEAD):main

```
## ArgoCD beállítása a projekt figyelésére
Ha elvégeztük ezeket a lépéseket, akkor az ArgoCD felületén hozzunk létre egy új Applikációt, a new app gombra kattintva és adjuk meg a következőekt:
- Application Name: argo-test-app (más is lehet)
- Project Name: default
- Sync Policy: Automatic (3 percenként ránéz a GitLab projektre és ha változást lát, módosít a lokális alkalmazáson)
- Prune resources és self heal -> pipa
- Autocreate namespace -> pipa
- Repository url: A GitLab projekthez tartozó url
- Path: helm/ (itt találhatóak az alkalmazás példányosításához a leírók)
- Cluster url: https://kubernetes.default.svc (ezt felajánlja)
- Namespace: argo-test-ns (vagy amit jónak látsz)
A create gombra kattintva elfogadtatjuk a beállításokat. Ennek hatására egy nagy négyzet meg is jelenik, amire rákattintva láthatjuk, a letöltött és telepített komponenseket.
