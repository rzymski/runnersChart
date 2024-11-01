___
**Aplikacja webowa stworzona w Django 4.2.5 i pythonie 3.11.1**
___

## Zawartość REDME
1. :runner: [Cel aplikacji](#cel-aplikacji)
2. :scroll: [Funkcjonalność](#funkcjonalność)
3. :computer: [Uruchomienie aplikacji lokalnie](#Instrukcja-uruchomienia-aplikacji-lokalnie)
4. :wrench: [Konfiguracja](#konfiguracja)
5. :satellite: [Wdrożenie na serwer pythonanywhere](#wdrożenie-na-serwer-pythonanywhere)
6. :globe_with_meridians: [Działanie aplikacji na serwerze](#działanie-aplikacji-na-serwerze)

# Cel aplikacji
Aplikacja została stworzona na potrzeby wydarzenia dwudniowego biegu, zaczynającego się wieczorem i kończącego ranem następnego dnia.<br/>
Aplikacja umożliwia prezentacje wyników biegaczy w formie wykresu i tabeli.<br/>
Zarządzanie danymi biegów aplikacji odbywa się w dostosowanym panelu administracyjnym lub domyślnym panelu administracyjnym.

# Funkcjonalność
1) [x] Wykres z wynikami biegaczy
2) [x] Tabela z wynikami biegaczy
3) [x] Tabela z wynikami pojedyńczego biegacza
4) [x] Dostosowany panel administracyjny
5) [x] Strandardowy panel administracyjny Django


# Instrukcja uruchomienia aplikacji lokalnie:
Tworzymy wirtualne środowisko
```sh
python -m venv venv
```

Aktywujemy wirtualne środowisko
```sh
.\venv\Scripts\activate
```
Instalujemy wszystkie potrzebne biblioteki z pliku `requirements.txt`
```sh
pip install -r .\requirements.txt
```

Uruchomienie projektu Django
```sh
python manage.py runserver 'nrPortu opcjonalnie'
```

# Konfiguracja:

> [!Important]
> ### Ustawiamy datę biegu w:
> [runProject\settings.py](https://github.com/rzymski/runnersChart/blob/master/runProject/settings.py) ${\textsf{\color{gold}FIRST\\_DAY}}$ **`datetime(2024, 11, 2, 21, 30)`**

<details>
  <summary>Kod <b><code>FIRST_DAY</code></b> zawierający datę biegu <b>datetime(2024, 11, 2, 21, 30)</b></summary>

```python
from pathlib import Path

from datetime import datetime, timedelta
FIRST_DAY = datetime(2024, 11, 2, 21, 30)
SECOND_DAY = FIRST_DAY + timedelta(days=1)
```
<img src="readmeImages/settings.png?raw=true" alt="Wybranie daty biegu w ustawieniach kodu">
</details>

<h3>Przydatne polecenia:</h3>

Tworzenie super użytkownika
```sh
python manage.py createsuperuser
```

Tworzenie migracji po zmianie modelów
```sh
python manage.py makemigrations appName --name changeName
```

Zatwierdzenie migracji
```sh
python manage.py migrate  
```

# Wdrożenie na serwer pythonanywhere:
<details>
    <summary><h3>Uruchomienie konsoli w pythonanywhere:</h3></summary>
        W sekcji <code>Consoles</code><br/>
        Uruchamiamy konsole:        
        <img src="readmeImages/launchConsole.png?raw=true" alt="uruchomienie konsoli w pythonanywhere">
</details>

Klonujemy repozytorium:
```sh
git clone https://github.com/rzymski/runnersChart.git
```

Tworzymy wirtaulne środowisko:
```sh
mkvirtualenv --python=/usr/bin/python3.10 venv
```

Pobieramy wszystkie potrzebne pakiety z requirements.txt:
```sh
pip install -r ./runnersChart/requirements.txt
```

<h3><details>
    <summary>Dodanie aplikacji do serwera:</summary>
        Add a new web app --> ... --> Manual Configuration --> Python 3.10 --> ...<br/>
        <img src="readmeImages/addApplication.png?raw=true" alt="Dodanie aplikacji do serwera">
</details></h3>

<details>
<summary><h3>Ustawienia w sekcji Web:</h3></summary>
  <br/>Source code: /home/nazwaUzytkownika/runnersChart (nazwa głównego folderu projektu i nazwa repozytorium na github-ie) <br/>
  <br/>Working directory: /home/nazwaUzytkownika <br/>
  <br/>Virtualenv: /home/nazwaUzytkownika/.virtualenvs/venv <br/>
  <br/>Static files: <br/>
  &emsp; URL: /static/ <br/>
  &emsp; DIRECTORY: /home/nazwaUzytkownika/runnersChart/static <br/><br/>
    
WSGI configuration file:
```python
import os
import sys
path = os.path.expanduser('~/runnersChart')
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'runProject.settings'
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())
```
<img src="readmeImages/webSettings.png?raw=true" alt="Ustawienia aplikacji na serwerze">
</details>

Po skonfigurowaniu warto również dla pewności jeszcze raz upewnić się, że pliki statyczne są załadowane.<br/>
**Polecenie do przeładowania plików statycznych:**
```sh
python manage.py collectstatic
```

<h3><details>
    <summary>Przeładowanie aplikacji na serwerze:</summary>
        <img src="readmeImages/reloadSide.png?raw=true" alt="Przeladowanie aplikacji na serwerze">
</details></h3>

# Działanie aplikacji na serwerze
**Można sprawdzić działanie aplikacji w:**
 - https://ultradoba2024.pythonanywhere.com/

**Wykres:**
- https://ultradoba2024.pythonanywhere.com/chart/line
<img src="readmeImages/chart.png?raw=true" alt="Wykres biegów">

**Tabela z wynikami biegaczy:**
- https://ultradoba2024.pythonanywhere.com/table/result
<img src="readmeImages/resultsTable.png?raw=true" alt="Tabela wyników biegaczy">

**Tabela wyników pojedyńczego biegacza:**
- https://ultradoba2024.pythonanywhere.com/table/runnerResults/1 *id biegacza*
<img src="readmeImages/singleRunnerResultsTable.png?raw=true" alt="Tabela wyników pojedyńczego biegacza">

**Spersonalizowany panel administracyjny:**
- https://ultradoba2024.pythonanywhere.com/admin/customAdmin
<img src="readmeImages/customAdminPanel.png?raw=true" alt="Spersonalizowany panel administracyjny">

**Domyślny panel administracyjny:**
- https://ultradoba2024.pythonanywhere.com/admin
<img src="readmeImages/adminPanel.png?raw=true" alt="Domyślny panel administracyjny Django">
