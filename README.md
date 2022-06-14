# RasterLab - dokumentacja

### Tomasz Michalski - ID06IO1 - 19012

Ostatnia aktualizacja 14.06.2022

## Instalacja

By uruchomić aplikację należy się upewnić, że repozytorium zostało ściągnięte w pełnej wersji.
Program używa kilku modułów, które należy zainstalować, ich lista jest umieszczona w `requirements.txt`.
Zalecane jest użycie wirtualnego środowiska, o module `venv` więcej [tutaj](https://docs.python.org/3/library/venv.html):

```sh
cd backend
python3 -m venv env
env\Scripts\activate
```

By upewnić się, że używasz wirtualnego środowiska użyj komendy: `which pip`. Powinna wyświetlić ścieżkę do lokalnego interpretera.

```sh
pip install -r requirements.txt
```

## Użytkowanie

### Start

Po instalacji uruchomienie programu jest dokonywane za pomocą jednej komendy. Upewnij się, że jesteś w wirtualnym środowisku.

```sh
python3 main.py
```

W konsoli powinienieś widzieć wszelkie outputy potrzebne do ew. zgłoszenia bugów.

### Główne okno aplikacji

Po uruchomeniu programu otworzy się główne okno aplikacji. Ważnym zaznaczenia jest to, że program nie będzie blokował opcji jeżeli dany obrazek jest niekompatybilny lub żaden obrazek nie został podany. (v.1.0.0)
![image](https://user-images.githubusercontent.com/34798378/173596967-aef5cb10-f228-409d-a435-8292a10c05cc.png)


#### FILE - import i zapis obrazu

Opcja FILE udostępnia nam opcję importowania obrazu (.jpg, .bmp, .png) do programu. Po pomyślnym imporcie obraz otworzy się w programie w postaci odczepionego niezależnego okna.
![image](https://user-images.githubusercontent.com/34798378/173597004-b0697eb2-9da8-41fa-88da-6669e2b4edae.png)
![image](https://user-images.githubusercontent.com/34798378/173597053-37a799b7-6f72-4263-a9e0-c669d6927520.png)
![image](https://user-images.githubusercontent.com/34798378/173597589-2f2d143a-6280-4f67-bd88-4db53b2ead93.png)

Wartym zauważenia jest to, że w programie znajdują się **2 typy obrazu** - jeden jest to obraz natywny bądź edytowany - który można zapisać na dysk. Innym typem obrazu są obrazy wyniku analizy, które nie są możliwe do zapisania i służą tylko do wglądu informacji.
Ta różnica zostanie usunięta w kolejnych iteracjach.
![image](https://user-images.githubusercontent.com/34798378/173597092-6aa3377e-8127-49c5-a4b4-22d23bf60425.png)
Pliki zapisywane są w folderze projektowym.

#### ANALYZE - analiza obrazu

Opcja ANALYZE oferuje kilka pod-opcji:
![image](https://user-images.githubusercontent.com/34798378/173597181-dcddf666-a518-47d1-9165-b673e04ae462.png)

-   hist plot - utworzenie graficznego przedstawienia histogramu obrazu.
-   ![image](https://user-images.githubusercontent.com/34798378/173597670-084c3670-6910-4f91-a936-adba8fb7d3ea.png)

-   hist array - utworzenie histogramu obrazu w postacji tekstowej.
-   ![image](https://user-images.githubusercontent.com/34798378/173597752-4f4c5ae6-32bf-433d-8ec9-6f563dd1c783.png)

-   plot profile - utworzenie linii profilu - by ta opcja zadziałała obraz musi byc kliknięty w dwóch punktach po kolei i będą to punkty to analizy.
-   ![image](https://user-images.githubusercontent.com/34798378/173597803-16d5fc04-5b79-41c8-acdc-8dd5706079ac.png)

-   find objects - uruchamienie algorytmu detekcji obiektów w obrazie razem z ich właściwościami.
-   ![image](https://user-images.githubusercontent.com/34798378/173597911-d23fb7c6-c57a-4b73-8d40-35f057e8d663.png)


#### PROCESS - przetworzenie obrazu
![image](https://user-images.githubusercontent.com/34798378/173597245-6e513458-764d-451f-8156-e452443336dd.png)

-   negation - tworzenie negatywu obrazu
![image](https://user-images.githubusercontent.com/34798378/173598019-71518084-5036-4b0a-a40d-fe5818f450c7.png)

-   threshold - progowanie z dwoma opcjami
    -   bins - ilość progów
    ![image](https://user-images.githubusercontent.com/34798378/173598185-f91c7d54-977c-4869-861d-022d8dc6ba01.png)

    -   simple - wartość działu
    ![image](https://user-images.githubusercontent.com/34798378/173598232-aac261ca-d54a-444c-af95-7a9f03c60089.png)

-   posterize - posteryzacja z ilością progów
![image](https://user-images.githubusercontent.com/34798378/173598294-348ba994-0834-4375-8dcf-1e1f2c7d299c.png)

-   stretch - rozciąganie zakresu; z zakresu p1-p2 do zakresu q3-q4, w szczególności gdy q3=0, q4=Lmax. Wartości mogą zostać puste wtedy zostaną wypełnione wartościami automatycznie.
![image](https://user-images.githubusercontent.com/34798378/173598444-1370bd5d-b81b-4440-bdf7-f4c7d5796233.png)


#### FILTER - zastosowanie filtrów na wybranym obrazie
![image](https://user-images.githubusercontent.com/34798378/173597269-2de49036-3ea8-4efd-bc85-d7f9e50127ca.png)

-   blur - opcja wygładzania
![image](https://user-images.githubusercontent.com/34798378/173598590-5a257e08-08cb-4fd2-a336-a1cd2a0308dc.png)
    -   blur - prostego
    -   gaussian - gaussowskiego
-   detect_edge - detekcji krawędzi różnymi metodami (potrzebne argumenty są podane na przyciskach)
![image](https://user-images.githubusercontent.com/34798378/173598686-eac982b0-4699-483b-bdf9-bb8839d3bbda.png)
    -   sobel
    -   laplacian
    -   canny
    -   prewitt
-   sharpen - wyostrzania oparta na 3 maskach laplasjanowych
![image](https://user-images.githubusercontent.com/34798378/173598816-5395ba0a-5cba-4296-b5e2-eebaa0ad01dc.png)
    -   A
    -   B
    -   C
-   custom_kernel - opcja wpisania własnego kernela 3x3!
[image](https://user-images.githubusercontent.com/34798378/173598951-f03a8999-09d1-4caa-a99d-3e34b30be8a1.png)

-   median_filter - filtracja medianowa z opcjami wielkości kernela
![image](https://user-images.githubusercontent.com/34798378/173599087-8aed790a-2bda-42e8-93f4-0a7456bbedc4.png)


#### TWO POINT - operacje na dwóch obrazach
![image](https://user-images.githubusercontent.com/34798378/173597305-4a78ac06-654c-426e-bcd2-fd902b41cc8f.png)

Ta opcja umożliwia operacje na dwóch obrazach. Trzeba pamiętać, że obrazy muszą zostać kliknięte w wybranej przez siebie kolejności by opcja działała poprawnie.

-   add - odejmowanie

![image](https://user-images.githubusercontent.com/34798378/173599353-1399c1bc-aeed-42b1-b4da-0905b674319f.png)
-   subtract - odejmowanie
-   blend - mieszanie z dwoma wartościami
-   operacje logiczne bitowe AND, OR, NOT, XOR

#### MORPH - operacje morfologiczne
![image](https://user-images.githubusercontent.com/34798378/173597337-47c996c6-5286-40bd-a789-0fdefd0e203e.png)

Na początku wybieramy operację, którą chcemy wykonać

-   erosion - erozja
-   ![image](https://user-images.githubusercontent.com/34798378/173599458-6f9f26d4-ac3b-4a53-a104-c4913e62e87e.png)

-   dilution - dylacja
-   open - otwórz
-   close - zamknij

Później wybieramy który kernel chcemy i na koniec wybieramy metodę paddingu krawędzi oraz rozmiar kernela.

#### MASK FILTER - filtry jedno i dwu etapowe
![image](https://user-images.githubusercontent.com/34798378/173597391-4663ef6f-537b-47e7-9d40-4bd088c7b3ad.png)

Mamy możliwość wybrania między jedno i dwu-stopniowym filtrowaniem.
![image](https://user-images.githubusercontent.com/34798378/173599648-ee2f57a5-24b5-40e0-abd0-5674d17fa16a.png)

W przypadku jednostopniowego filtrowania mamy możliwość wyboru kernela, wyostrz bądź zmiękcz i opcję paddingu krawędzi obrazu.

#### SKELETONIZE - szkieletyzacja
![image](https://user-images.githubusercontent.com/34798378/173597425-2840c006-2570-4914-b9f2-aaadeb77e318.png)
![image](https://user-images.githubusercontent.com/34798378/173599767-9430f4f2-50f7-4565-89b6-45894be475ff.png)

Tutaj mamy tylko opcję paddingu krawędzi obrazu.

#### SEGMENTATION - segmentacja
![image](https://user-images.githubusercontent.com/34798378/173597469-91c522e7-40de-45e7-9451-613e4a2c8461.png)
![image](https://user-images.githubusercontent.com/34798378/173600026-6cb5b8ed-0943-47f9-8902-f6b42eb6d40f.png)
![image](https://user-images.githubusercontent.com/34798378/173600082-c5e41959-724d-4dc8-8802-ca32b9bc04fc.png)

Mamy 4 opcje:

-   normal segmentation z wyznaczanym progiem
-   adaptive - adaptacyjne
-   otsu - metodą Otsu
-   watershedding - metodą wododziałową
