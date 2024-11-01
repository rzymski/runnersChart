___
**Aplikacja webowa stworzona w Django do wyświetlania wyników biegaczy na wykresie i w tabelce**
___

## Zawartość REDME
1. :runner: [Funkcjonalność](#funkcjonalność)
2. :computer: [Uruchomienie lokalnie](#I=instrukcja-uruchomienia-lokalnie)
3. :wrench: [Konfiguracja lokalna](#konfiguracja-lokalna)
4. :satellite: [Wdrożenie na serwer pythonanywhere](#wdrozenie-na-serwer-pythonanywhere)
5. :globe_with_meridians: [Działanie aplikacji na serwerze](#dzialanie-aplikacji-na-serwerze)

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
W sekcji **`Consoles`**		  
Uruchamiamy konsole:

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

Przechodzimy do sekcji **`Web`**    
Add a new web app --> ... --> Manual Configuration --> Python 3.10 --> ...

Source code: /home/nazwaUzytkownika/runnersChart (nazwa głównego folderu projektu i nazwa repozytorium na github-ie)
Working directory: /home/nazwaUzytkownika

Virtualenv: /home/nazwaUzytkownika/.virtualenvs/venv  
Static files:    
$\quad$ URL: /static/	    
$\quad$ DIRECTORY: /home/nazwaUzytkownika/runnersChart/static

WSGI configuration file:
```sh
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

Polecenie do przeładowania plików statycznych:
```sh
python manage.py collectstatic
```

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
