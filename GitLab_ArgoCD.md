A labor során egy pici alkalmazást fogtok készíteni, ezt a laborkörnyezetben futtatott GitLab-on fogjátok létrehozni. Az alkalmazást a GitLab Workflow segítségével automatizált módon Docker image-ekbe fogjátok csomagolni és az image-et a saját DockerHub profilotokra fogjátok feltölteni. Az ArgoCD szolgáltatás segítségével pedig elindítjátok majd frissítitek az alkalmazást egy Kubernetes környezetben, ha az alkalmazás kódja megváltozik.

## Projekt létrehozása
A labor során egy közös GitLab runner-t fogtok használni, amit egy csoporton belül lehet megosztottan használni. A felhasználóitokat hozzáadtam a csoporthoz, így nektek már csak egy projektet kell létrehozni a csoporton belül. Owner jogosultságot kapott mindenki. Ennek tudatában kérlek ne rosszalkodjatok! :)

1. Jelentkezz be a GitLab-ra
2. A baloldali sávon kattints a Grups-ra
3. Válaszd ki a VillMScLab csoportot
4. Jobb felül kattints a New Project-re
5. Kattints a Create blank project lehetőségre
6. Add meg a projekt nevét és állíds publikusra az elérhetőségét
7. Végül kattints a Create project gombra.

## Alkalmazás létrehozása

Hozz létre a projekt gyökerében egy alkalmazást. Erre egy lehetőség ha mondjuk egy app.py fájlt készítesz, amibe az alábbi egyszerű webszerver kódját beilleszted. A lenti kód egy Flask szervert indít ami az 5000-es porton fog figyelni. A / útvonalon kiírja hogy "Hello World!!", a /health útvonal pedig esetleges healthcheck kérésekre válaszolhat.

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

Mivel az alkalmazás a Kubernetes rendszerben fog futni, ezért hozz létre egy Dockerfile-t amiből a GitLab CI workflow-ja egy Docker image-et fog készíteni. Az alábbi Dockerfile a fenti python szerver Docker konténerben való futtatásához szükséges lépéseket végzi el, így a függőségek telepítését és az app.py image-be való másolását.

```Dockerfile
FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY app.py app.py
CMD python -u app.py
```
## Runner csatolása
1. Kattints a bal sávin a settings-re majd a CI/CD-re
2. Nyisd le a Runners lehetőséget
3. Látni fogsz egy Other available runners feliratot, alatta találsz egy runner-t. Kattints az Enable for this project gombra

## Workflow létrehozása

Hozzunk létre egy kezdetleges workflow-t amely a Dockerfile-t felhasználva egy image-et build-el, majd azt egy tag-gel feltölti a Dockerhub profilodra.
Ha jobban megvizsgálod az alábbi fájl tartalmát, láthatod, hogy néhány változót használ.
* CI_REGISTRY_USER - A Dockerhub-os profilod felhasználóneve
* CI_REGISTRY_PASSWORD - A Dockerhub profilod jelszava

A DOCKER_IMAGE_NAME a CI_REGISTRY_USER és egy fixre választható, jelen esetben villabproject string összekötésével jön létre. Ahol a villabproject lesz az image-ed neve a saját Dockerhub profilodon. Persze ha úgy tetszik, a villabproject is helyettesíthető egy változóval.

Találsz egy CI_COMMIT_SHA változót is, amelyet a GitLab alapértelmezetten kezel, így ezt nem kell megadni. Ennek a változónak az értéke az adott push-hoz tartozó hash, amely egyedi, így ezzel fogjuk a Dockerhub-ra feltöltött image-eket verziózni.

### A változók beállítására a projekteden belül van lehetőséged. 
1. Kattints a bal sávban a Settings-re majd a CI/CD-re
2. Nyisd le a Variables szakaszt
3. Kattints az Add variable gombra, ami egy jobboldali sávot hoz fel
4. A key és value mezőket add meg
5. A key legyen a fenti CI_REGISTRY_USER, a value pedig a Dockerhub felhasználóneved, végül Add variable
6. Add hozzá a jelszót is, key: CI_REGISTRY_PASSWORD, value: a Dockerhub profilod jelszava, majd Add variable

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
Ha ezzel megvagyunk, akkor valahol jobb felül meg kell jelenjen egy kék karika és egy folyamatot ábrázoló belső kis kör amiből hiányzik egy darab. Erre kattintva át tudsz navigálni a Workflow felületére ahol találni fogysz egy test nevű dobozt, azon belül pedig egy build_image sort. A build_image-re kattintva meg tudod nézni, hogy milyen parancsok futottak le a build_image feladatban. Ha minden rendben akkor egy zöld pipa lesz az eredmény, ellenkező esetben egy piros X. Ez a Workflow minden push-ra le fog futni.

Ha sikeresen lefutott a Workflow, nézd meg a Dockerhub-on, hogy az image megjelent-e a profilod alatt, azt is figyeld meg, hogy az image-hez tartozó tag egy hash lesz ami éppen a CI_COMMIT_SHA változó értéke.

## Helm chart-ok létrehozása

A Kubernetes-ben futtatott alkalmazásokhoz felveszünk egy deployment és egy service erőforrásleírót.

A deployment lehetővé teszi a pod-ok indítását és ezen felül figyel arra is, hogy ha esetleg egy pod valamilyen okoktól fogva megsemmisülnek, akkor azt újraindítsa.

A service erőforrás egy hálózati végpont (IP - Port) mögé rejti a választott deployment által indított pod-okat. Ezt a párosítást a metadata mezőkben megadott label értékekkel valósítjuk meg. 

A Kubernetes által használt yaml fájl-ok jól le tudják írni az erőforrásokat, viszont ezekben fix értékek szerepelnek, nem paraméterezhetőek egyszerűen. Emiatt a labor során ahelyett, hogy Kubernetes yaml fájlokat használnánk, inkább a Helm által paraméterezhető yaml fájlokat fogunk írni, így mindig a legújabb konténer image-et tudjuk letölteni.

Ezeknek a fájloknak készítsunk egy másik könyvtárat, helm néven. A helm könyvtáron belül legyen egy values.yaml fájl és egy templates mappa. A templates mappa tartalmazza a következőkben bemutatott két fájlt - deployment.yaml és service.yaml. A Helm egy Chart.yaml fájlt is definiál amiben a Chartról találhatók információk.

A deployment-et leíró yaml fájl. Figyeljük meg, a {{ .Values.env.DOCKER_REGISTRY }}, {{ .Values.env.IMAGE_NAME }}, {{ .Values.env.APP_VERSION }} értékeket. Ezeket a helm values.yaml fájljából veszi és ezzel adja meg, hogy melyik image-et töltse le a Dockerhub-ról.

Kezdetben a values.yaml fájlba csak valami töltelék értékeket adunk meg, mivel ezt majd a GitLab Workflow felül fogja írni.

deployment.yaml
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
service.yaml
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
values.yaml
```yaml
env:
  APP_VERSION: versionstring
  DOCKER_REGISTRY: registryusername
  IMAGE_NAME: imagename
```
Chart.yaml
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

Készítsünk egy újabb feladatot a Workflow-hoz. Az alábbi részt csak másold a már létrehozott .gitlab-ci.yml fájl tartalma alá.
Az alábbi yaml egy config_argo feladatot fog létrehozni és módosítja a /helm/values.yaml tartalmát egy-egy sed parancs segítségével.

Az APP_VERSION értékét átírja az aktuális COMMIT_SHA-ra,a DOCKER_REGISTRY értékét a tárolt változókból veszi át, az IMAGE_NAME értékét pedig villabproject-re állítja.

A values.yaml módosítása után egy commit és push parancsot kísérel meg, viszont ehhez szüksége van az adataidra. 
Emiatt szükségünk lesz még két változó létrehozására amit a már ismert módon tudunk a CI/CD Variables lehetőségen keresztül megadni.
1. GITLAB_USERNAME - A felhasználónév amivel regisztráltál a GitLab-ra
2. GITLAB_PASSWORD - A GitLab profilod jelszava
3. GITLAB_EMAIL - Az email címed amivel a GitLab-ra regisztráltál

Ha úgy tetszik, akkor az utolsó előtti sorban a myproject.git-ből a myproject is eltárolható egy váltázóban, akkor még rugalmasabb lesz ez a workflow szakasz és más projektekhez is könnyebben tudod illeszteni.

```yaml
config_argo:
  script:
    - cd helm
    - "sed -i 's|APP_VERSION:.*|APP_VERSION: '$CI_COMMIT_SHA'|' values.yaml"
    - "sed -i 's|DOCKER_REGISTRY:.*|DOCKER_REGISTRY: '$CI_REGISTRY_USER'|' values.yaml"
    - "sed -i 's|IMAGE_NAME:.*|IMAGE_NAME: 'villabproject'|' values.yaml"
    - git config --global user.name $GITLAB_USERNAME
    - git config --global user.email $GITLAB_EMAIL
    - git add values.yaml
    - git commit -m "Update values.yaml"
    - git remote set-url origin http://$GITLAB_USERNAME:$GITLAB_PASSWORD@128.105.146.171:8080/$GITLAB_USERNAME/myproject.git
    - git push origin $(git rev-parse HEAD):main

```
## ArgoCD beállítása a projekt figyelésére
Ha elvégeztük ezeket a lépéseket, akkor az ArgoCD felületén hozzunk létre egy új Applikációt, a new app gombra kattintva és adjuk meg a következőket:
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

## Az alkalmazás kódjának frissítése
Az app.py fájlban írjátok át a Hello World!! szöveget tetszőlegesen, én pl. 3 felkiáltójelet raktam a végére a 2 helyett. Push-oljátok a módosításokat és várjatok kb. 3-4 percet.

Várakozás közben figyeljétek az ArgoCD felületét és a Kubernetes pod-okat is, mondjuk a következő paranccsal:
```bash
kubectl get pods -n argo-test-ns -w
```
Frissült az alkalmazás? Próbáljátok ki.

