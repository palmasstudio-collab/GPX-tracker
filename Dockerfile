# Usa una versione leggera di Python
FROM python:3.10-slim

# Imposta la cartella di lavoro
WORKDIR /app

# Copia e installa le librerie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice
COPY . .

# Comando per avviare il server web sulla porta 8080 (standard di Cloud Run)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
