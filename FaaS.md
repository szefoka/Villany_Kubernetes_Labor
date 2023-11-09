# Segédanyag a laborra való felkészüléshez
## FaaS/Serverless
A felhő-techonológiák esetén megfigyelhető, hogy a virtualizált környezetek és a bennük futó alkalmazáshalmazok egyre kisebb méretűek. A Function as a Service azaz a függvényszolgáltatás, vagy más néven Serverless computing egy újabb cloud computing implementáicó. Ebben az esetben a felhasználók apró programrészleteket futtatnak a felhőben, amiket függvényeknek nevezünk. Ezeket a függvényeket összekapcsolva kaphatunk különböző felhő-szolgáltatásokat. A serverless név ugyan utalhatna arra is, hogy nincsenek fizikai kiszolgálók/számítógépek, de valójában azt jelenti, hogy az alkamazásfejlesztők csak a kód implementálására kell koncentráljanak, az integrációs lépéseket a keretrendszer elvégzi helyettük.

## Nyílt forráskódú FaaS implementációk
A labor során az OpenFaaS nyílt forráskódú FaaS keretrendszerrel fogunk dolgozni. Nagyjából az összes nyílt forráskódú FaaS keretrendszerre jellemző, hogy valamilyen gateway komponensen keresztül hívhatók meg a futtatott függvények. A gateway komponens tehát egy proxyként szolgál a függvények felé.
A FaaS függvények futtatásához a keretrendszer egy runtime/wrapper komponenst biztosít amely futtatja a felhasználó által írt függvényt. A runtime komponens általában egy HTTP webszerver környezet, melynek segítségével könnyen átvihetók adatok és hívási paraméterek a függvénypéldányok között. A függvény runtime ezen kívül pedig egy helth-check mechanizmust is definiál, ezzel jelezve a keretrendszernek, hogy a futtatott függvény hibára futott-e.

## Függvényhívások
A függvényeket szinkron és aszinkron módon is meghívhatjuk. Szinkron módon a hívó fél addig várakozik amíg a meghívott függvény válasza vissza nem tér. Aszinkron esetben a hívó fél a hívás kiküldése után azonnal folytathatja a dolgát. Szinkron hívások esetén direkt http kapcsolatot épít fel a hívó a hívott között, míg aszinkron hívásoknál a hívó fél a gateway komponens aszinkron végpontjához fordul amelynek átadja a hívási paramétereit és egy azonnal kapott válasz után folytathatja a futását. A gateway a kapott hívási paramétereket egy üzenetsorba helyezi amiket egy központi szolgáltatás, az üzenetsor-kezelő továbbít a megfelelő függvénynek. Az üzenetsor-kezelő és a hívott függvény között egy HTTP kapcsolat épül fel a függvény futása idejére.

## Tracing és Profilozás
A függvényke futását különböző, úgynevezett tracing megoldással követhetjük nyomon. A labor sorána  Jaeger nyílt forráskódú függvény-monitorozó rendszerrel fogunk dolgozni.

# Feladatok
## VM előkészítése
1. Nyisd meg a virtualbox-ot
2. Kattints a csillagra az új VM létrehozásához

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_1.png)

3. Nevezd el Ubuntu-nak

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_2.png)

4. Állíts be 4 GB memóriát és 4 CPU magot

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_3.png)

5. A merevlemez beállításakor válaszd a már létező virtuális merevlemez használatát, a jobb oldali kis mappa ikonra kattintás után egy ablak jelenik meg

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_4.png)

6. A felugró ablakban az Add gombra kattints és válaszd ki a kitömörített vdi fájlt.

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_5.png)

7. Végül kattints a Finish gombra

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_6.png)

8. Ezt követően állítsd be VM-ed hálózati kártyáit, ehhez kattints először a fogaskerékre, majd válaszd a hálózati lehetőséget

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_7.png)

9. Állíts be egy NAT interfészt port forward-olással az ssh kapsolat létrehozására.

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_8.png)

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_9.png)

10. Adj hozzá egy másik interfészt bridge üzemmódban arra a gépedben lévő hálózati kártyára amin az internetet is eléred

  ![Alt text](https://github.com/szefoka/Villany_Kubernetes_Labor/blob/main/VM_Creation_Steps_Images/create_vm_10.png)  

11. Végül indítsd el a VM-et. Jobb gombbal kattintva választhatsz hogy általános, vagy headless (nem jelenik meg a VM képernyője) módban indítod. Headless mód esetén SSH-val tudsz hozzáférni, ami sokszor kényelmesebb tud lenni.
12. Az ssh-hoz használd a következő parancsot, a VM felhasználója: labor, jelszava: labor.
  ```
  ssh labor@127.0.0.1 -p 10022
  ```  
## Környezet telepítése
1. Clone-ozd a VM-be ezt a git repo-t.
2. Másold a /home/labor mappába a repo-ban lévő function_runtime mappát functions néven.
3. Lépj be a Villany_Kubernetes_Labor/FaaS_Setup mappába.
  ```
  cp -r Villany_Kubernetes_Labor/function_runtime /home/labor/functions
  ```
4. Első alkalommal add ki a make install parancsot, ha valamilyen okból félbe kellett hagynod a labort és a VM-et leállítottad, akkor a make reset parancsot add ki.
5. A make futtatása után az ip a paranccsal kérd le a VM-ed enp0s8 interfész címét. Ezen az IP-n keresztül  fogod elérni a VM-ben futó
 szolgáltatásokat.
  ```
  ip a
  ```


## 1. Függvény létrehozása és használata
### 1.1 Python Hello függvény létrehozása
- Elsőként jelentkezz be az OpenFaaS rendszerbe a faas-cli alkalmazás használatával. A felhasználóneved az admin lesz, míg a jelszavad a Hello.
  ```
  faas-cli login -u admin -p Hello -g localhost:31112
  ```
- A faas-cli new paranccsal tudsz létrehozni új függvényt, melynek a --lang paraméterében megadva tudod kiválasztani a megfelelő nyelvet. A függvény nevének válassz egy alulvonásoktól mentes nevet, pl myfunc, vagy myfunc-1. A kubernetes által indított konténerek mellett egy docker registry konténer is fut. Ide fogod feltölteni a függvényed image-ét. Ezért a faas-cli parancshoz azt is add meg, hogy mely registry-be kerüljön a függvény a push parancs kiadására. Ehhez használd a --prefix 127.0.0.1:5000 lehetőséget.
  ```
  faas-cli new --lang python --prefix 127.0.0.1 myfunc1
  ```
- A parancs sikeres lefutására létrejön egy mappa és egy yml fájl, mindkettő a függvényed nevét viseli
- A létrejött mappában találsz egy handler.py fájlt, melyben a függvényedet tudod módosítani és egy requirements.txt fájlt amiben a függvényhez való függőségeket tudod megadni
- A függvényed az alább látható módon fog kinézni. Ez az egyszerű vüggvény a híváskor kapott értéket adja vissza. Nyugodtan módosítsd a függvényt, ha szeretnéd.
  ```
  from function import invoke

  def handle(req, context):
    """handle a request to the function
    Args:
        req (str): request body
    """

    return req
  ```
- Build-eld a függvényt a faas-cli parancs segítségével, ahol a -f kapcsolóval tudod megadni hogy melyik yml fájlból készüljön a FaaS keretrendszerben futtatható függvénypéldány
  ```
  faas-cli build -f myfunc1.yml
  ```
- Push-old a függvényt
  ```
  faas-cli push -f myfunc1.yml
  ```
- Deploy-old a függvényt, melynek hatására az elindul a FaaS keretrendszerben. Itt figyelj arra, hogy a -g kapcsolóval a FaaS keretrendszer gateway komponensét szólítsd meg, hiszen csak így fogja tudni a keretrendszer, hogy egy új függvényt kell indítania
  ```
  faas-cli deploy -f myfunc1.yml -g localhost:31112
  ```

### 1.2 Hívd meg a függvényt
A függvényt többféleképpen is meg tudod hívni.
1. faas-cli invoke, ilyenkor szabadon írhatsz egy szöveget, majd a CTRL+D kombinációval tudod elküldeni a szöveget a függvényednek.
    ```
    faas-cli invoke myfunc1 -g localhost:31112
    ```
3. curl - ebben az esetben ismerned kell a függvény elérési útját. Ehhez a kubectl get services -n openfaas parancsot add ki és keresd ki a gateway komponens belső IP címét és belső portját. Használhatod a kubernetes rendszer külső IP címét és a 31112 portot is. Ebben az esetben a függvény az < ip >:< port >/function/<függvényed neve> útvonalon érhető el
    ```
    curl localhost:31112/function/myfunc1  
    ```
4. webes felület segítségével az invoke gombra kattintva

### 1.3 A függvény kiskálázása
Terheld a függvényt a Hey programmal, 1 percig, nézd meg, hogy hány példányra skálázódik ki a függvény, ezt a webes felületen tudod a legkönnyebben nyomon követni a replicas felirat alatt látható a függvények aktuális példányszáma. hey -c 10 -z 60s <fuggveny eleresi utja>
```
hey -c 10 -z 60s http://localhost:31112/function/myfunc1
```

## 2. Függvények láncolása
1. Az előző feladat alapján hozz létre egy második python nyelvű függvényt ami hozzáfűzi a neptunkódod a bementi értékhez.
   ```
   faas-cli new --lang python --prefix 127.0.0.1 myfunc1
   ```
3. Módosítsd az első függvényt, hogy az hívja meg az újonnan létrehozott függvényt a Hello szöveggel és adja vissza eredményként az új függvény által visszaadott értékt.
4. A függvények hívását az invoke utasítás meghívásával teheted meg, aminek a paraméterei sorban a következők: 
    - funcname - a maghívni kívánt függvény neve
    - param - bemeneti paraméter(ek) json formátumban
    - context - kontextus (ezt csak add át, a függvényed fejlécében található)
    - asynch - aszinkron/szinkron hívás True=Aszinkron False=Szinkron
5. Hívd meg az első függvényt és nézd meg mi lesz az eredménye. Vizsgáld a Jaeger felületén a létrejött tracing idősorokat.
   - A láncban az első függvény
    ```
    from function import invoke

    def handle(req, context):
        """handle a request to the function
        Args:
            req (str): request body
        """

        return invoke.invoke("myfunc2", req, context, False)
    ```
    - A láncban a második függvény
    ```
    from function import invoke
    import time
    def handle(req, context):
        """handle a request to the function
        Args:
            req (str): request body
        """
        time.sleep(0.02)
        return req
    ```

## 3. Aszinkron függvényhívás
1. Alakítsd át az első függvényt, hogy aszinkron módon hívja meg a második függvényt.
    ```
    from function import invoke

    def handle(req, context):
        """handle a request to the function
        Args:
            req (str): request body
        """

        return invoke.invoke("myfunc2", req, context, True)
    ```
3. Hívd meg az első függvényt.
5. Vizsgáld a Jaeger felületén a létrejött tracing idősorokat. Miben különböznek ezek az előbbi esettől?

