from flask import Flask, render_template, request, send_file, jsonify
import os
import json
# Importa le funzioni dal tuo vecchio script (se lo tieni) o inserisci qui la logica PDF

app = Flask(__name__)

# Questa rotta carica la pagina principale
@app.route('/')
def index():
    return render_template('index.html')

# Questa rotta fornisce alla mappa la lista dei file GPX disponibili
@app.route('/api/gpx-files')
def get_gpx_files():
    gpx_dir = 'gpx'
    if not os.path.exists(gpx_dir):
        return jsonify([])
    files = [f for f in os.listdir(gpx_dir) if f.endswith('.gpx')]
    return jsonify(files)

# Questa rotta permette di scaricare il singolo file GPX per disegnarlo sulla mappa
@app.route('/gpx/<filename>')
def serve_gpx(filename):
    return send_file(os.path.join('gpx', filename))

# Qui riceveremo le tappe scelte e genereremo il PDF
@app.route('/generate', methods=['POST'])
def generate():
    dati = request.json
    tappe_selezionate = dati.get('tappe', [])
    
    # QUI ANDRA' INSERITA LA LOGICA DI GENERAZIONE PDF CHE GIA' HAI
    # ...
    # pdf.output("Itinerario.pdf")
    
    # Ritorna un messaggio di successo per ora
    return jsonify({"status": "success", "message": f"Ricevute {len(tappe_selezionate)} tappe. (Generazione PDF in lavorazione)"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
