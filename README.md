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


#### FILE - import i zapis obrazu

Opcja FILE udostępnia nam opcję importowania obrazu (.jpg, .bmp, .png) do programu. Po pomyślnym imporcie obraz otworzy się w programie w postaci odczepionego niezależnego okna.

Wartym zauważenia jest to, że w programie znajdują się **2 typy obrazu** - jeden jest to obraz natywny bądź edytowany - który można zapisać na dysk. Innym typem obrazu są obrazy wyniku analizy, które nie są możliwe do zapisania i służą tylko do wglądu informacji.
Ta różnica zostanie usunięta w kolejnych iteracjach.
Pliki zapisywane są w folderze projektowym.

#### ANALYZE - analiza obrazu

Opcja ANALYZE oferuje kilka pod-opcji:

-   hist plot - utworzenie graficznego przedstawienia histogramu obrazu.

-   hist array - utworzenie histogramu obrazu w postacji tekstowej.

-   plot profile - utworzenie linii profilu - by ta opcja zadziałała obraz musi byc kliknięty w dwóch punktach po kolei i będą to punkty to analizy.

-   find objects - uruchamienie algorytmu detekcji obiektów w obrazie razem z ich właściwościami.


#### PROCESS - przetworzenie obrazu

-   negation - tworzenie negatywu obrazu

-   threshold - progowanie z dwoma opcjami
    -   bins - ilość progów

    -   simple - wartość działu

-   posterize - posteryzacja z ilością progów

-   stretch - rozciąganie zakresu; z zakresu p1-p2 do zakresu q3-q4, w szczególności gdy q3=0, q4=Lmax. Wartości mogą zostać puste wtedy zostaną wypełnione wartościami automatycznie.


#### FILTER - zastosowanie filtrów na wybranym obrazie

-   blur - opcja wygładzania
    -   blur - prostego
    -   gaussian - gaussowskiego
-   detect_edge - detekcji krawędzi różnymi metodami (potrzebne argumenty są podane na przyciskach)
    -   sobel
    -   laplacian
    -   canny
    -   prewitt
-   sharpen - wyostrzania oparta na 3 maskach laplasjanowych
    -   A
    -   B
    -   C
-   custom_kernel - opcja wpisania własnego kernela 3x3!

-   median_filter - filtracja medianowa z opcjami wielkości kernela


#### TWO POINT - operacje na dwóch obrazach

Ta opcja umożliwia operacje na dwóch obrazach. Trzeba pamiętać, że obrazy muszą zostać kliknięte w wybranej przez siebie kolejności by opcja działała poprawnie.

-   add - odejmowanie

-   subtract - odejmowanie
-   blend - mieszanie z dwoma wartościami
-   operacje logiczne bitowe AND, OR, NOT, XOR

#### MORPH - operacje morfologiczne

Na początku wybieramy operację, którą chcemy wykonać

-   erosion - erozja

-   dilution - dylacja
-   open - otwórz
-   close - zamknij

Później wybieramy który kernel chcemy i na koniec wybieramy metodę paddingu krawędzi oraz rozmiar kernela.

#### MASK FILTER - filtry jedno i dwu etapowe

Mamy możliwość wybrania między jedno i dwu-stopniowym filtrowaniem.

W przypadku jednostopniowego filtrowania mamy możliwość wyboru kernela, wyostrz bądź zmiękcz i opcję paddingu krawędzi obrazu.

#### SKELETONIZE - szkieletyzacja

Tutaj mamy tylko opcję paddingu krawędzi obrazu.

#### SEGMENTATION - segmentacja

Mamy 4 opcje:

-   normal segmentation z wyznaczanym progiem
-   adaptive - adaptacyjne
-   otsu - metodą Otsu
-   watershedding - metodą wododziałową
