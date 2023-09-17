# Segédanyag a laborra való felkészüléshez
## Docker
https://qosip.tmit.bme.hu/foswiki/bin/view/Meres/DockerMeresiSegedlet

### Dockerfile
A Docker image-eket egy Dockerfile alapján tudjuk elkészíteni. A Dockerfile-ok parancsok sorozatát tartalmazzák mellyel egy alapként használt Docker image-et testreszabhatunk. Alább egy példa Dockerfile látható.

```
FROM node:18-alpine		#base image
WORKDIR /app			#directory to use
COPY . .			#copy from host path to container path
RUN yarn install --production	#run arbitarary commands
CMD ["node", "src/index.js"]	#command to be executed on container startup
```

A Dockerfile-ból a következő parancsokkal tudunk image-eket készíteni és azokat egy repository-ba feltölteni:
docekr build -t <dockerhub_username>/<image_name> .	#this command builds the Dockerfile in the current (.) directory with the given name after the -t flag
docker push <dockerhub_username>/<image_name>		#this command uploads the image to dockerhub


## Kubernetes
A Kubernetes egy nyílt forráskódú, konténer-orkesztrációs rendszer, mely lehetővé teszi a konténerizált alkalmazások automatikus telepítését, skálázását és egyéb menedzselését.

### Namespace
A Kubernetes rendszer felhasználói a létrehozott erőforrásaikat különböző névterekben szeparálhatják el egymástól. Csak a névterekben belüli erőforrások elnevezései kell hogy egyediek legyenek. Így például több hallgató is a saját névterében létrehozhat ugyanolyan névvel szolgátatásokat.

### Pod
A Kubernetes által menedzselhető legalsóbb szintű elem a Pod, mely egy vagy több konténer együttes futtatásáért felel. A Pod-ban lévő konténerek megosztozva használják a Pod-hoz rendelt erőforrásokat. Egy Pod-ban lévő konténereket a Kubernetes közösen menedzsel, így a Pod-ok fizikai gépekre való ütemezésekor minden a Pod-ban lévő konténer egy Kobernetes worker node-ra kerül. Pod-okat a Kubernetes-ben legegyszerűbben egy-egy yaml fájl megadásával tudunk létrehozni. Az alábbi példa egy nginx konténert futtat egy Pod-ban, melynek a neve nginx lesz, a konténer listában láthatjuk, hogy az egyetlen konténer neve nginx lesz, melynek a verziója az 1.14.2, továbbá a konténer a 80-as port-on engedélyez hozzáférést.

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
```

### ReplicaSet és Deployment
Az egyforma típusú Pod-ok létrehozásáért és menedzseléséért a Kubernetes a ReplicaSet erőforrást használja. A ReplicaSet-ek segítségével a Kubernetes rendszer garantálni tudja, hogy bizonyos számú Pod az adott típusból mindig jelen legyen a rendszerben. Azonban ezt az erőforrástípust meglehetősen ritkán használjuk, mivel a Kubernetes a Deployment erőfforáss típusban számos más hasznos kiegészítést definiál a ReplicaSet-hez képest. Emiatt a labor során a ReplicaSet helyett a Deployment erőforrással fogunk dolgozni. Az alábbi yaml fájl egy Deployment-et ír le, mely 3 példányban futtatja az nginx Pod-ot. A podban lévő konténerleíró hasonló az előző példához. Azonban ebben az esetben további meta-adatokat adhatunk meg. Így például a selector:matchlabels:app segítségével a Deplyoment-et később más erőforrásokkal tudjuk összekötni.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

### Service

### Tárlók csatolása
A labor során megismerkedünk azzal is, hogy hogyan csatolhatunk külső tárolókat egy Pod-ban futó konténerhez. A labor során és az alábbi példában (az egyszerűség kedvéért) a Kubernetes HostMount megoldását szemléltetjük, ahol a konténert futtaó gép a saját fájlrendszeréből csatol egy könyvtárat a konténerhez. Ebben az esetben meg kell győződnünk, hogy minden worker node-on elérhető a csatolni kívánt adat. Ehhez a legegyszerűbb megoldás egy NFS kialakítása a szervereken. A példában a lényeges részek a spec:containrs:volumeMounts és a spec:volumes alatt láthatóak. A VolumeMounts alatt definiálhatjuk, hogy mely csatolmányokat akarjuk az adott konténerhez rendelni (a name mező egyezzen meg a csatolni kívánt volume nevével) és a konténeren belüli elérési útvonalat. A volumes alatt pedig definiálhatjuk a csatolni kívánt erőforrások nevét, azoknak a típusát és (jelen esetben) a fizikai tárolón lévő helyét és típusát (File(OrCreate) Directory(OrCreate)).

```
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: registry.k8s.io/test-webserver
    name: test-container
    volumeMounts:
    - mountPath: /test-pd
      name: test-volume
  volumes:
  - name: test-volume
    hostPath:
      # directory location on host
      path: /data
      # this field is optional
      type: Directory
```     

# Feladatok

### 1. VLC Docker image létrehozása

Az alábbi Dockerfile-t egészítsd ki úgy, hogy egy VLC szerver fusson benne.

A következőkre figyelj
- A konténerben a default felhasználó ne a root legyen, ehhez hozz létre egyet
  - Hozz létre neki egy saját könyvtárat (-m)
  - A shell a bash legyen (-s /bin/bash)
  - Állítsd be az új felhasználót alapértelmezettként
- Állítsd az alapértemezett munkakönyvtárat a felhasználó alapértelmezett könyvtárára
- Másold be a konténerbe a szükséges fájlokat a létrehozott felhasználó könyvtárába
  - http_streaming.sh
  - streaming könyvtár
  - media könyvtár
  - Figyelj arra, hogy alapértelmezetten a másolás parancs csak a root felhasználónak ad jogosultságot a fájlok használatára
    - Ehhez a --chown=user:group paraméterezhető flag-et add meg a COPY vagy ADD parancsnál
- Állítsd be a konténer indulásakor futtatandó parancsot, úgy hogy a VLC HTTP streaming elinduljon a konténerrel együtt.

```
FROM debian:bookworm-slim
RUN ... && ... dbus-x11
RUN ...
WORKDIR ...
USER ...
COPY ...
COPY ...
COPY ...
ENV DISPLAY=:0
CMD ["..."]
```
Hozz létre egy docker image-et az elkészült Dockerfile-ból és töltsd fel a megadott Docker repository-ba.

Jegyzőkönyvbe: Az elkészült Dockerfile

### 2. Kubernetes
#### 1. Ismerkedés a Kubernetes rendszerrel
1. Milyen szolgáltatások alkotják az alap Kubernetes rendszert?
2. Mely szolgáltatás felel a Kubernetes logikai hálózatáért? Hány fut belőle? Miért annyi?
   
#### 2. Ismerkedés a Kubernetes alapelemeivel
1. Készíts egy névteret, lehetőleg az egyikőtök neptun kódja legyen - Jegyzőkönyvbe a létrejött névtér listázása
2. Készíts egy Pod-ot a létrehozott image-ből - Jegyzőkönyvbe: A pod listázása és a pod-ot létrehozó yaml fájl
3. Készíts egy Deploymentet is amely a létrehzott image-et futtatja egy Pod-ban - Jegyzőkönyvbe: A deployment lisázása, a deployment-et létrehozó yaml fájl
4. Töröld a két létrehozott podot. Mit tapasztalsz? Jegyzőkönyvbe: Tapasztalatok, újraindult-e a pod? Igen/nem? Miért?
5. Készíts egy Service-t amin keresztül távolról eléred a Deployment által felügyelt pod-ot. Csatlakozz VLC-vel a videó-streamhez. Kérj meg két mérőcsoportot, hogy csatlakozzanak a te service-edre. Vizsgáld a pod CPU és memória-használatát. Jegyzőkönyvbe: A service-t létrehozó yaml fájl, a service listázása, a VLC amin fut a videó, Pod CPU és memória-használata
6. Skálázd ki kézzel a VLC szolgáltatásod 2 elemre, itt is kérj meg két mérőcsoportot, hogy csatlakozzanak, hasonlóan az előző feladathoz, vizsgáld az erőforrás-használatot. Jegyzőkönyvbe: a pod-ok listázása, erőforráshasználata.

#### 3. Trükkös videószolgáltatás
1. Módosítsd a legelső feladatban létrehozott Dockerfile-t, úgy hogy a videófájlt ne másolja be automatikusan - Jegyzőkönyvbe: a Dockerfile tartalma
2. Készíts az előző feladatban létrehozott deployment fájlról két másolatot
    - Csatold a host gép /tmp/video/Nature.mp4 fájlját a /home/<felhasználónév a konténerben>/media/media.mp4 útvonalra az egyik podban
    - Csatold a host gép /tmp/video/big_buck_bunny.mp4 fájlját a /home/<felhasználónév a konténerben>/media/media.mp4 útvonalra a másik podban
    - Állítsd a két deployment labelselectorjait ugyanarra az értékre
    - Jegyzőkönyvbe: a két deployment yaml fájlja
3. Módosítsd az előző feladatban létrehozott service-t hogy a két deployment podjaiban futó videókhoz kívülről hozzá lehessen férni - Jegyzőkönyvbe a a service yaml fájlja
4. Csatlakozz a videószolgáltatáshoz VLC-vel. Nézd meg mi történik ha egymás után többször csatlakozol a videószolgáltatáshoz - Jegyzkőnyvbe: a tapasztalatok
