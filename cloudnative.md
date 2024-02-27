# Konténerizáció labor
A labor során a hallgatók az alkalmazások konténerizációjával és a konténerek közötti kommunikációval ismerkednek meg.
Egy micro-service környezetben az alkalmazások különböző kommunikációs mintát alkalmazhatnak. A laboron a szinkron, aszinkron és eseményvezérelt mintákkal ismerkedünk meg.

## Előkészületek
A Labor elvégzéséhez (ha a példákat nem szeretnék módosítani) bármelyik Python3+ környezet és Docker telepítése szükséges a hallgatói gépekre.
A docker telepítését a következő linken található forrásból végezzük:
https://docs.docker.com/engine/install/

Ha esetleg valakinek már régebbről telepítve van a docker csomag, viszont még a compose parancs nem támogatott, akkor a következővel tudja telepíteni a szükséges modult:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
```

## Szinkron hívások
Szinkron hívások esetén a kezdeményező köteles megvárni a választ, ekkor előfordulhat, hogy a hívó fél idle állapotban várakozik a válaszra, viszont a számára allokált erőforrásokat fogva tartja. Ebben az esetben egy HTTP GET/POST kérés egyszerűen alkalmazható. Nézzünk erre egy példát ami két komponensből áll. A példák python nyelven kerültek implementálásra, és a Flask webes keretrendszert használják.

initiator.py
```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
    url = 'http://localhost:6000/'
    send_data = request.get_data(as_text=True)
    x = requests.post(url, data=send_data)
    print(x.text)
    return "OK from initiator" + x.text + "\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

receiver.py
``` python
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
    print(request.get_data(as_text=True)+"\n")
    return "OK from receiver"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
```

A kipróbáláshoz a következő parancsot futtassuk:
```bash
curl -d Hello http://localhost:5000/
```
Ezzel egy Hello üzenetet küldünk a szolgáltatásnak. A többi esetben is ezt a parancsot használjuk.

## Aszinkron hívások
Szinrkon hívásokkal ellentétben az aszinkron hívások használatakor a kezdeményező azonnal visszatérhet. Ilyenkor természetesen a választ valahonnan máshonnan kell megszerezni, erre lehetőség van egy külső adattároló/adatbázis használatával, de más megoldások is elképzelhetőek, mint egy e-mail kiküldése a válasszal. Ez a megoldás egy központi elemet igényel, ami valahogyan átveszi a kérést a hívó oldaltól és továbbítja a meghívott félnek. Általában üzenetsorokkal valósítjuk meg ezt a fajta kommunikácós modellt. A példában egy rabbitmq üzenetsorral kötjük össze a két modult. A kódrészletekben a hívó és fogadó felek között egy üzenetsort definiálunk az üzenetek küldésére. Ha több alkalmazás is ugyanazt az üzenetsort használja, akkor Round-Robin módon férnek hozzá az üzenetsorhoz.

Ehhez indítsunk egy Docker-ben futó rabbitmq üzenetsort, így legalább nem kell semmit sem telepíteni a számítógépre és minden használatra készen van.

```bash
docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq:3-management
```

async_initiator.py

```python
from flask import Flask, request
import requests
import pika


app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
    send_data = request.get_data(as_text=True)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=send_data)
    connection.close()
    return "OK" + "\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

async_receiver.py

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

result = channel.queue_declare(queue='hello')
queue_name = result.method.queue

def callback(ch, method, properties, body):
    print(f"{body}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
```

Itt érdemes lehet kipróbálni, hogy két példányt is indítunk az async_receiver.py-ból. Mit tapasztalunk?

## Eseményvezérelt tervezés
Az eddigiek során arra láttunk példát, hogy egy fél pontosan egy másikat megszólít meg. A következő példában arra mutatunk egy példát, hogy egy kezdeményező üzenetére egyszerre több szolgáltatás is elér. Ebben az esetben a rabbitmq-ban egy exchange-et definiálunk amely dönt arról, hogy az egyes üzenet mely üzenetsorokba kerüljön, mivel azt szeretnénk, hogy az üzenet minden feliratkozóhoz eljusson, így a fanout lehetőséget adtuk meg. Azt is láthatjuk az alkalmazásokban, hogy nem nevesített üzenetsort hoztunk létre, így mindenki egy véletlenül inicializált nevű üzenetsort fog használni, ezzel elérve, hogy semelyik alkalmazás ne használja ugyanazt az üzenetsort.

ed_initiator.py
```python
from flask import Flask, request
import requests
import pika


app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
    send_data = request.get_data(as_text=True)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='hello', exchange_type='fanout')
    channel.basic_publish(exchange='hello', routing_key='', body=send_data)
    #print(f" [x] Sent {message}")
    connection.close()
    return "OK" + "\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0')

```
ed_receiver.py
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='hello', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='hello', queue=queue_name)

def callback(ch, method, properties, body):
    print(f"{body}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
```

Itt is érdemes kipróbálni két példányban indítani az ed_receiver.py programot. Mi a tapasztalat? Mi a különbség az async verzióhoz képest?

## Alkalmazások konténerizálása
Ebben a feladatrészben az elkészült alkalmazásokat Docker konténerekben fogjuk futtatni. Ehhez először készítenünk kell néhány Docker image-et, amelyekből a konténereket fogjuk példányosítani.
Egy Docker image-et egy Dockerfile segítségével tudunk létrehozni. Esetünkben a Flask, requests, és Pika csomagokat fogjuk telepíteni. A python környezetet nem fogjuk, ugyanis egy python image-ből indulunk ki. Telepítéshez a python csomagkezelőjét, a pip-et használjuk.
Az alkalmazásokon viszont szükséges lesz megváltoztatni a csatlakozási pontot, mivel a localhost elérési út már nem fog működni. A docker konténerek viszont név szerint elérik egymást ha egy saját hálózatot hozunk létre számukra. Így csak a megfelelő nevet kell beilleszteni a kapcsolódási parancsok paramétereként.

Egy docker hálózat létrehozása a következő paranccsal történhet

```bash
docker network create -d bridge mynet
```

Az első példábna ismertetett initiator.py-hoz tartozó Dockerfile a következőképpen néz ki.
- FROM - melyik image-ből indulunk ki.
- RUN - parancs kiadása
- WORKDIR - Aktuális mappa kiválasztása
- USER - Konténerben a parancsok futtatását végző felhasználó, alapból amit az alap image megad, vagy root
- COPY - fájl bemásolása a host-ról a konténerbe, megadott útvonalre
- CMD - egy lista amiből a parancs összeáll

Mivel a logok között nem fognak megjelenni a print-elt szövegek, ezért adjuk meg a -u kapcsolót a program futtatásakor, ezzel ezek a sorok is megjelennek.

```Dockerfile
FROM python:3.6.15-slim-buster
RUN pip3 install flask requests pika
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY initiator.py initiator.py
CMD ["python", "-u" "initiator.py"]
```

Az image létrehozása a Dockerfile-ból a következő paranccsal lehetésges, ahol a konténer nevét a -t kapcsoló után adjuk meg
```bash
docker build -t flask_initiator .
```
A konténer futtatásához a következő parancsot adjuk ki, a --network kapcsolóval tudjuk kiválasztani a hálózatot amihez csatlakoztatni szeretnénk a konténert, a -p kapcsoló adja meg hogy a konténer belső portját melyik külső portra továbbítsuk, az -d kapcsoló pedig azt teszi lehetővé, hogy a konténer a háttérben fusson, tehát ne írja tele a képernyőnket.
```bash
docker run -d -p 5000:5000 --name initiator --network mynet flask_initiator
```


Fontos, hogy ne felejtsük el áttenni a rabbitmq konténerünket az újonnan létrehzott hálózatra.
Ehhez törölhetjük és újraindíthatjuk a konténert az új hálózattal

```bash
docker rm -f some-rabbitmq
docker run docker run -d --hostname my-rabbit --name some-rabbit --network mynet -p 5672:5672 rabbitmq:3-management
```
Ha egszerűbben szeretnénk, akkor pedig csak a létező konténert átmozgatjuk az új hálózatra
```bash
docker network connect mynet somerabbit
```
A többi példát is futtassuk konténerekben. Ehhez a fenti parancsokra támaszkodjunk.
A konténerben való futtatáskor nem fogjuk látni a programok kimenetét, ehhez használjuk a docker logs parancsát a következőképpen:

```bash
docker logs <konténernév>
```
## Indítás automatizálása

Hogy ne kelljen mindig a konténereket külön külön kézzel indítanunk, meg aztán le is törölnünk, a Docker egy compose paranccsal is rendelkezik, amely egy yaml fájlt olvas be és az alapján elindítja a konténereket, létrehozza és csatolja a hálózatot.

A szinkron megoldást leíró docker compose yaml a következő:
sync_compose.yaml:
```yaml
networks:
  sync_network:
    driver: bridge

services:
  sync_sender:
    image: flask_initiator
    container_name: initiator
    depends_on:
      - sync_receiver
    ports:
      - 5000:5000
    networks:
      - sync_network
  sync_receiver:
    image: flask_receiver
    container_name: receiver
    networks:
      - sync_network
```

A fenti yaml fájlban egyrészt egy hálózatot hozunk létre, aminek a neve sync_network lesz és egy linux bridge komponensen keresztül valósítja meg a konténerek kommunikációját.
Másrészt a services kulcs alatt a futtatandó konténereket határozzuk meg. Ahol egy nevet tudunk nekik választani, viszont ez nem lesz azonos a konténer nevével, viszont alapesetben ebből származtatja a példányosított konténerek neiveit. A  konténernél adjuk meg az image-et, a konténer nevét, a szükséges belső portok külső láthatóságát, ahol kell, és a használni kívánt hálózatot. A depends_on lehetőség ebben a feladatban nem igazán szükséges, viszont a másik két példa esetén érdemes lehet, hogy először a message queue induljon el és csak azt követően a rajta keresztül kommunikáló podok.

Hozzunk létre mindhárom példához egy-egy docker compose yaml fájlt és próbáljuk is ki őket.
Az elkészült fájlokból a környezet példányosítása a következő paranccsal történhet, ahol -d a háttérben való futtatást jelenti:

```bash
docker-compose -f sync_compose.yaml up -d
```

A környezet törléséhez pedig az alábbi parancs kiadása szükséges:

```bash
docker-compose -f sync_compose.yaml down
```
Nézzük meg hogy a depends_on lehetőséggel és anélkül milyen sorrendben jönnek létre és törlődnek a konténerek.

## Források

https://www.rabbitmq.com/tutorials/tutorial-one-python

https://www.rabbitmq.com/tutorials/tutorial-three-python#exchanges

https://docs.docker.com/reference/dockerfile/

https://docs.docker.com/compose/compose-file/compose-file-v3/#network-configuration-reference
