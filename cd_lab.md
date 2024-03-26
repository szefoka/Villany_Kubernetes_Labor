# CD Labor

A labor során a hallgatók megismerkednek egy rendszert készítenek, amely képes a GitHub-on tárolt forrásokat a Kubernetes Cluster-be telepíteni az ArgoCD modul segítségével.

## Előkészületek

A labor során a GitHub actions-t fogják a hallgatók használni és a Docker Hub-ra fogják a konténer image-eiket feltölteni. Ehhez szükség lesz egy GitHub és egy Docker Hub profilra. Előbbihez az előző laboron már regisztrálták magukat, viszont az utóbbihoz nem biztos, hogy mindenkinek van profilja regisztrálva. Ha ez így lenne, akkor regisztráljon egyet magának. https://hub.docker.com/ -> sign up gomb (jobb felső sarok)

### Minikube telepítése
A labort minikube környezetben végezzük. Ehhez szükség van a docker, a minikube és a kubectl csomagok telepítésére.

Docker telepítése a következő parancsokkal

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce
```

Minikube telepítése a következő linken érhető el:

https://minikube.sigs.k8s.io/docs/start/

A kubectl telepítése az alábbi linken érhető el:

https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

A minikube start parancsot kiadva elindul a helyi kubernetes példány.

### ArgoCD telepítése minikube-ra

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

kubectl -n argocd patch secret argocd-secret \
    -p '{"stringData": {"admin.password": "$2a$10$mivhwttXM0U5eBrZGtAG8.VSRL1l9cZNAmaSaqotIzXRBRwID1NT.",
        "admin.passwordMtime": "'$(date +%FT%T)'"
    }}'
```

Ezt követően kihozzuk a minikube-ból az argocd-re mutató portot és a linkre kattintva a böngészőben meg is nyílik az argocd felülete, ahol admin-admin párossal be is jelentkezhetünk.

```bash
minkube service -n argocd argocd-server
```

## Tesztalkalmazás elkészítése
A labor során a hallgatók egy Python alkalmazást fognak ArgoCD segítségével a Kubernetes cluster-ben elindítani. A minimum szükséges fájlok alább láthatóak. Ettől természetesen eltérhetnek a hallgatók, ha szeretnének valamilyen "izgalmasabb" alkalmazást megvalósítani.

A python program helye legyen a git repo gyökerében egy mappa, pl app/app.py, forrása:
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

Mivel a Kubernetes rendszer Docker image-ből példányosítja a pod-okban futó konténereket, így szükségünk lesz egy Dockerfile-ra ami alább látható, ez kerüljön az app.py fájllal egy könyvtárba
```Dockerfile
FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY app.py app.py
CMD python -u app.py
```

A Kubernetes-ben futtatott alkalmazásokhoz felveszünk egy deployment és egy service erőforrásleírót.
A deployment lehetővé teszi a pod-ok indítását és ezen felül figyel arra is, hogy ha esetleg egy pod valamilyen okoktól fogva megsemmisülnek, akkor azt újraindítsa.
A service erőforrás egy hálózati végpont (IP - Port) mögé rejti a választott deployment által indított pod-okat. Ezt a párosítást a metadata mezőkben megadott label értékekkel valósítjuk meg. 
A Kubernetes által használt yaml fájl-ok jól le tudják írni az erőforrásokat, viszont ezekben fix értékek szerepelnek, nem paraméterezhetőek egyszerűen. Emiatt a labor során ahelyett, hogy Kubernetes yaml fájlokat használnánk, inkább a Helm által paraméterezhető yaml fájlokat fogunk írni, így mindig a legújabb konténer image-et tudjuk letölteni.
Ezeknek a fájloknak készítsunk egy másik könyvtárat, pl helm néven. A helm könyvtáron belül legyen egy values.yaml fájl és egy template mappa. A template mappa tartalmazza a következőkben bemutatott két fájlt - deployment.yaml és service.yaml. A Helm egy Chart.yaml fájlt is definiál amiben a Chartról találhatók információk.
A deployment-et leíró yaml fájl. Figyeljük meg, ${{ .Values.env.APP_VERSION }} értéket. Ezt a helm values.yaml fájljából veszi. A values fájlba egyébként több értéket is beleírhatnánk és jobban is paraméterezhetnénk a yaml fájljainkat.
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
          image: szefoka/argo-test-app1:{{ .Values.env.APP_VERSION }}
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

A service.yaml fájl forrása

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

A paraméterezéshez szükséges values.yaml fájl forrása, ahol az APP_VERSION a push-olásokat követően változni fog.

```yaml
env:
  APP_VERSION: 9ef1ff41efd4f9b8e157fe9c7274c3b32101fea0
```

A Chart.yaml tartalma

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

### GitHub action létrehozása a konténer image build-eléséhez és docker hub-ba való feltöltéséhez.

Hozzunk létre a .github/workflows/ könyvtár alatt egy cd.yaml fájlt aminek a tartalma alább olvasható, láthatjuk, hogy egy docker image-et build-el, majd pushol a dockerhub-ra, amikhez különbözöő titkosított információkat használ. Ezek a   DOCKERHUB_USERNAME és DOCKERHUB_KEY változókban vannak eltárolva. Ezeket a settings->secrets&variables (bal oldalon) -> actions alatt érjük el. A két változót külön adjuk hozzá. Felül írjuk be a változó nevét, alul az értékét. A DOCKERHUB_KEY-hez a dockerhub-on kapott token-t adjuk meg, amit a felhasználói ikonra kattintva majd a my account lehetőséget választva a security fül alatt generálhatunk.

```yaml
name: CD

on:
  push:
    branches:
      - master
      - main
  workflow_dispatch:

env:
  DOCKERHUB_USERNAME: ${{ secrets.DOCKER_USERNAME }}
  DOCKERHUB_KEY: ${{ secrets.DOCKER_KEY }}
  IMAGE_NAME: argo-test-app1

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ env.DOCKERHUB_USERNAME }}
          password: ${{ env.DOCKERHUB_KEY }}

      - name: Build Docker image
        run: cd ./app1 && docker build -t ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .

      - name: Push Docker image
        run: docker push ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Update values.yaml
        run: |
          cd helm
          sed -i 's|APP_VERSION:.*|APP_VERSION: '${{ github.sha }}'|' values.yaml 
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add values.yaml
          git commit -m "Update values.yaml"
          git push
```

Ha elvégeztük ezeket a lépéseket, akkor az ArgoCD felületén hozzunk létre egy új Applikációt, a new app gombra kattintva és adjuk meg a következőekt:
- Application Name: argo-test-app (más is lehet)
- Project Name: default
- Sync Policy: Automatic (3 percenként ránéz a githubra és ha változást lát, módosít a lokális alkalmazáson)
- Prune resources és self heal -> pipa
- Autocreate namespace -> pipa
- Repository url: A git-es repo-dhoz tartozó url
- Path: helm/ (vagy amibe raktad a helm-hez tartozó yaml fájlokat)
- Cluster url: https://kubernetes.default.svc (ezt felajánlja)
- Namespace: argo-test-ns (vagy amit jónak látsz)
A create gombra kattintva elfogadtatjuk a beállításokat. Ennek hatására egy nagy négyzet meg is jelenik, amire rákattintva láthatjuk, a letöltött és telepített komponenseket.

Próbáljuk ki a python alkalmazást.

```bash
minikube service list
minikube service -n argo-test-app argo-test-app1
```
Nyissuk meg a böngészőben a visszaadott url-t és nézzük meg hogy kiírta-e amire vártunk (Hello World!!)

Próbáljunk valamit változtatni a python webalkalmazáson, pl. a / útvonal visszatérési értékét. Várjunk kb. 3 percet és nézzük meg hogy frissült-e a kubernetes-ben futó alkalmazás.
Próbáljuk meg újra elérni az alkalmazásunkat és nézzük meg, hogy történt-e változás. Egyúttal azt is nézzük meg, hogy az ArgoCD mikor frissítette utoljára az alkalmazásunkat.

## Mi kerüljön a jegyzőkönyvbe?

A jegyzőkönyvbe a fontosabb lépések utáni részekről várok képernyőképeket, esetleg egy-két soros magyarázatot. Így tehát a github actions fülön a sikeres futásról, a Dockerhub-on a feltöltött image-ről, az argocd-ben a futó alkalmazásról és komponensekről, a böngészőben az alkalmazás kimenetéről.

