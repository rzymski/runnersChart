___
**Aplikacja webowa stworzona w Django do wyświetlania wyników biegaczy na wykresie i w tabelce**
___

## Zawartość REDME
1. :runner: [Funkcjonalność](#funkcjonalność)
2. :computer: [Uruchomienie lokalnie](#Instrukcja-uruchomienia-lokalnie)
3. :wrench: [Konfiguracja lokalna](#konfiguracja-lokalna)
4. :satellite: [Wdrożenie na serwer pythonanywhere](#wdrożenie-na-serwer-pythonanywhere)
5. :globe_with_meridians: [Działanie aplikacji na serwerze](#działanie-aplikacji-na-serwerze)

# Funkcjonalność
1) [x] Wykres z wynikami biegaczy
2) [x] Tabelka z wynikami biegaczy
3) [x] Dostosowany panel administracyjny


# Instrukcja uruchomienia lokalnie:
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

# Konfiguracja lokalna:
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
        <img src="redmeImages/launchConsole.png?raw=true" alt="uruchomienie konsoli w pythonanywhere">
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
        <img src="redmeImages/addApplication.png?raw=true" alt="Dodanie aplikacji do serwera">
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
<br/><img src="redmeImages/webSettings.png?raw=true" alt="Ustawienia aplikacji na serwerze">
</details>

Po skonfigurowaniu warto również dla pewności jeszcze raz upewnić się, że pliki statyczne są załadowane.<br/>
**Polecenie do przeładowania plików statycznych:**
```sh
python manage.py collectstatic
```

<h3><details>
    <summary>Przeładowanie aplikacji na serwerze:</summary>
        <img src="redmeImages/reloadSide.png?raw=true" alt="Przeladowanie aplikacji na serwerze">
</details></h3>

# Działanie aplikacji na serwerze
Można sprawdzić działanie aplikacji w:  
- https://ultradoba2024.pythonanywhere.com/

Wykres:
- https://ultradoba2024.pythonanywhere.com/chart/line

Tabelka z wynikami biegaczy:
- https://ultradoba2024.pythonanywhere.com/table/result

Spersonalizowany panel administracyjny:
- https://ultradoba2024.pythonanywhere.com/admin/customAdmin

Domyślny panel administracyjny:
- https://ultradoba2024.pythonanywhere.com/admin
