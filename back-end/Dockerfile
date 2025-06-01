# Oficjalny obraz Pythona
FROM python:3.11-slim

# Katalog roboczy w kontenerze
WORKDIR /app

# Kopiowanie plików projektu
COPY . .

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Zmienna środowiskowa - logowanie bez buforowania
ENV PYTHONUNBUFFERED=1

# Domyślna komenda uruchamiająca aplikację Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]