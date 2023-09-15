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
