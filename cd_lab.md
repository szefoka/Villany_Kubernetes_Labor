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

## Tesztalkalmazás elkészítése
A labor során a hallgatók egy Python alkalmazást fognak ArgoCD segítségével a Kubernetes cluster-ben elindítani. A minimum szükséges fájlok alább láthatóak. Ettől természetesen eltérhetnek a hallgatók, ha szeretnének valamilyen "izgalmasabb" alkalmazást megvalósítani.

A python program forrása:
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

Mivel a Kubernetes rendszer Docker image-ből példányosítja a pod-okban futó konténereket, így szükségünk lesz egy Dockerfile-ra ami alább látható
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

### GitHub action létrehozása a konténer image build-eléséhez és docker hub-ba való feltöltéséhez.

```yaml
env:
  APP_VERSION: 9ef1ff41efd4f9b8e157fe9c7274c3b32101fea0
```
