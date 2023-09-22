# Feladatok

## 1. Függvény létrehozása és használata
### 1.1 Python Hello függvény létrehozása
- A faas-cli new paranccsal tudsz létrehozni új függvényt, melynek a --lang paraméterében megadva tudod kiválasztani a megfelelő nyelvet. A függvény nevének válaszd a <neptun kód>-1 nevet.
- A parancs sikeres lefutására létrejön egy <neptun kód>-1 mappa és egy <neptun kód>-1.yml fájl
- A létrejött mappában találsz egy handler.py fájlt, melyben a függvényedet tudod módosítani és egy requirements.txt fájlt amiben a függvényhez való függőségeket tudod megadni
- A yml fájlban az image nevét egészítsd ki, hogy a szefoka repository-ba töltse fel
- Build-eld a függvényt a faas-cli parancs segítségével, ahol a -f kapcsolóval tudod megadni hogy melyik yml fájlból készüljön a FaaS keretrendszerben futtatható függvénypéldány
- Push-old a függvényt a docker hub-ra
- Deploy-old a függvényt, melynek hatására az elindul a FaaS keretrendszerben. Itt figyelj arra, hogy a -g kapcsolóval a FaaS keretrendszer gateway komponensét szólítsd meg, hiszen csak így fogja tudni a keretrendszer, hogy egy új függvényt kell indítania

### 1.2 Hívd meg a függvényt
A függvényt többféleképpen is meg tudod hívni.
1. faas-cli invoke
2. curl - ebben az esetben ismerned kell a függvény elérési útját. Ehhez a kubectl get services -n openfaas parancsot add ki és keresd ki a gateway komponens belső IP címét és belső portját. Használhatod a kubernetes rendszer külső IP címét és a 31112 portot is. Ebben az esetben a függvény az <ip>:<port>/function/<neptun kód>-1 útvonalon érhető el
3. webes felület segítségével az invoke gombra kattintva

### 1.3 A függvény kiskálázása
Terheld a függvényt a Hey programmal, 1 percig, nézd meg, hogy hány példányra skálázódik ki a függvény, ezt a webes felületen tudod a legkönnyebben nyomon követni a replicas felirat alatt látható a függvények aktuális példányszáma.

## 2. Függvények láncolása
1. Az előző feladat alapján hozz létre egy második python nyelvű függvényt ami hozzáfűzi a neptunkódod a bementi értékhez. A függvény neve legyen <neptun kód>-2
2. Módosítsd az első függvényt, hogy az hívja meg az újonnan létrehozott függvényt a Hello szöveggel és adja vissza eredményként az új függvény által visszaadott értékt.
3. A függvények hívását az invoke utasítás meghívásával teheted meg, aminek a paraméterei sorban a következők: 
    - funcname - a maghívni kívánt függvény neve
    - param - bemeneti paraméter(ek) json formátumban
    - context - kontextus (ezt csak add át, a függvényed fejlécében található)
    - asynch - aszinkron/szinkron hívás True=Aszinkron False=Szinkron
4. Hívd meg az első függvényt és nézd meg mi lesz az eredménye. Vizsgáld a Jaeger felületén a létrejött tracing idősorokat.

## 3. Aszinkron függvényhívás
1. Alakítsd át az első függvényt, hogy aszinkron módon hívja meg a második függvényt.
2. A második függvényt pedig írd át, hogy az eredményt a Redis tárolóba mentse el. A redis-be való beíráshoz a következő link alatt találsz információkat https://redis.io/docs/clients/python/
3. Egészítsd ki a második függvény requirements.txt fájlját úgy, hogy a függvény build-elése során a redis api-t is telepítse.
4. Hívd meg az első függvényt, majd nézd meg, hogy az eredmény bekerült-e a Redisbe. Ehhez használd a redis-cli parancsot a -h kapcsolóval ahol a redis szolgáltatás IP címét adod meg.
5. Vizsgáld a Jaeger felületén a létrejött tracing idősorokat. Miben különböznek ezek az előbbi esettől?

