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

Pod
A Kubernetes által menedzselhető legalsóbb szintű elem a Pod, mely egy vagy több konténer együttes futtatásáért felel. 
Pods are the smallest deployable units of computing that you can create and manage in Kubernetes.
A Pod is a group of one or more containers, with shared storage and network resources, and a specification for how to run the containers. A Pod's contents are always co-located and co-scheduled, and run in a shared context. A Pod models an application-specific "logical host": it contains one or more application containers which are relatively tightly coupled. In non-cloud contexts, applications executed on the same physical or virtual machine are analogous to cloud applications executed on the same logical host.

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

ReplicaSet
A ReplicaSet's purpose is to maintain a stable set of replica Pods running at any given time. As such, it is often used to guarantee the availability of a specified number of identical Pods.
However, a Deployment is a higher-level concept that manages ReplicaSets and provides declarative updates to Pods along with a lot of other useful features. Therefore, we recommend using Deployments instead of directly using ReplicaSets, unless you require custom update orchestration or don't require updates at all.
This actually means that you may never need to manipulate ReplicaSet objects: use a Deployment instead, and define your application in the spec section.

Deployment
A Deployment provides declarative updates for Pods and ReplicaSets.
You describe a desired state in a Deployment, and the Deployment Controller changes the actual state to the desired state at a controlled rate. You can define Deployments to create new ReplicaSets, or to remove existing Deployments and adopt all their resources with new Deployments.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
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
        
        
In this example:

    A Deployment named nginx-deployment is created, indicated by the .metadata.name field. This name will become the basis for the ReplicaSets and Pods which are created later. See Writing a Deployment Spec for more details.

    The Deployment creates a ReplicaSet that creates three replicated Pods, indicated by the .spec.replicas field.

    The .spec.selector field defines how the created ReplicaSet finds which Pods to manage. In this case, you select a label that is defined in the Pod template (app: nginx). However, more sophisticated selection rules are possible, as long as the Pod template itself satisfies the rule.
    Note: The .spec.selector.matchLabels field is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". All of the requirements, from both matchLabels and matchExpressions, must be satisfied in order to match.

    The template field contains the following sub-fields:
        The Pods are labeled app: nginxusing the .metadata.labels field.
        The Pod template's specification, or .template.spec field, indicates that the Pods run one container, nginx, which runs the nginx Docker Hub image at version 1.14.2.
        Create one container and name it nginx using the .spec.template.spec.containers[0].name field.



# Villany_Kubernetes_Labor

## Feladatok

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
