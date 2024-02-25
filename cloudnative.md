# Konténerizáció labor
A labor során a hallgatók az alkalmazások konténerizációjával és a konténerek közötti kommunikációval ismerkednek meg.
Egy micro-service környezetben az alkalmazások különböző kommunikációs mintát alkalmazhatnak. A laboron a szinkron, aszinkron és eseményvezérelt mintákkal ismerkedünk meg.

##Szinkron hívások
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

##Aszinkron hívások
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

##Eseményvezérelt tervezés
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

