# Użyj oficjalnego obrazu Pythona
FROM python:3.11-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki projektu do kontenera
COPY . .

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Ustaw zmienną środowiskową (jeśli potrzebujesz)
ENV PYTHONUNBUFFERED=1

# Domyślna komenda (możesz ją nadpisać w docker-compose)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]