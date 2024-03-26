# CD Labor

A labor során a hallgatók megismerkednek egy rendszert készítenek, amely képes a GitHub-on tárolt forrásokat a Kubernetes Cluster-be telepíteni az ArgoCD modul segítségével.

## Előkészületek
### Kubernetes telepítése VirtualBox VM-be

### ArgoCD telepítése Kubernetes-re

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
```yaml

```
