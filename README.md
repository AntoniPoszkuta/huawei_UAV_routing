# Huawei UAV Routing

## Opis projektu
Projekt **Huawei UAV Routing** realizuje algorytm wyznaczania tras dla bezzałogowych statków powietrznych (UAV – *Unmanned Aerial Vehicles*).
System służy do obliczania optymalnych tras przelotu w oparciu o zdefiniowaną siatkę połączeń i dane wejściowe. Kod został napisany w języku **Python**.

## Struktura projektu
```
huawei_UAV_routing/
├── algorithm.py
├── decoding.py
├── main.py
├── siatka.py
├── test_input.txt
└── README.md
```

### Pliki
- **main.py** – punkt wejścia programu; odpowiada za wczytanie danych wejściowych, inicjalizację obiektów i uruchomienie algorytmu trasowania.
- **algorithm.py** – implementacja logiki obliczeniowej służącej do wyznaczania trasy UAV.
- **decoding.py** – moduł odpowiedzialny za przetwarzanie i interpretację wyników działania algorytmu.
- **siatka.py** – definicja siatki (grafu) połączeń między punktami, po których poruszają się UAV.
- **test_input.txt** – przykładowy plik wejściowy z danymi testowymi.

## Wymagania systemowe
- Python w wersji **3.8** lub nowszej
- System operacyjny: Windows / Linux / macOS
- Brak zewnętrznych zależności – projekt wykorzystuje wyłącznie standardową bibliotekę Pythona.

## Instalacja
Pobierz repozytorium:
```bash
git clone https://github.com/AntoniPoszkuta/huawei_UAV_routing.git
cd huawei_UAV_routing
```

## Uruchomienie programu
Aby uruchomić program z przykładowymi danymi:
```bash
python main.py
```

Domyślnie skrypt wczytuje dane z pliku `test_input.txt` i generuje wynik trasowania w konsoli lub w odpowiednim pliku wynikowym (zależnie od konfiguracji w kodzie).

## Format danych wejściowych
Plik `test_input.txt` zawiera dane opisujące strukturę siatki, punkty początkowe i docelowe UAV oraz ewentualne parametry misji.
Struktura danych powinna być zgodna z opisem w kodzie źródłowym modułów `main.py` i `siatka.py`.

## Wyniki działania
Po uruchomieniu programu generowany jest wynik zawierający:
- trasę lub zestaw tras UAV,
- koszt lub długość trasy (jeśli obliczany),
- ewentualne statystyki działania algorytmu.

Wyniki mogą być wyświetlane w konsoli lub zapisane do pliku, w zależności od konfiguracji w `main.py`.

## Architektura systemu
Proces działania programu przebiega w następujących etapach:
1. **Wczytanie danych** – program pobiera informacje o topologii siatki oraz parametrach misji.
2. **Budowa grafu** – na podstawie danych w `siatka.py` tworzona jest struktura połączeń.
3. **Uruchomienie algorytmu** – moduł `algorithm.py` wyznacza optymalną trasę.
4. **Dekodowanie wyniku** – `decoding.py` interpretuje i przygotowuje wynik do prezentacji.
5. **Prezentacja rezultatów** – wynik trasowania jest prezentowany użytkownikowi.

## Testowanie
Projekt zawiera przykładowe dane w pliku `test_input.txt`, które umożliwiają weryfikację poprawności działania programu.
Aby przetestować działanie algorytmu z własnymi danymi, należy przygotować plik wejściowy w analogicznym formacie.

## Autorzy
Projekt został opracowany przez:
- **Antoni Poszkuta**
- **Mateusz Szymkowiak**
- **Maksymilian Strzelecki**

## Licencja
Projekt udostępniany jest na warunkach licencji **MIT**.
Pełny tekst licencji znajduje się w pliku `LICENSE` (jeśli dostępny w repozytorium).
