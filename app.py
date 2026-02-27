import os
import tempfile
import gpxpy
import googlemaps
from fpdf import FPDF
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

# Funzione per analizzare il file GPX
def get_gpx_info(filepath):
    with open(filepath, 'r') as f:
        gpx = gpxpy.parse(f)
        start = gpx.tracks[0].segments[0].points[0]
        end = gpx.tracks[0].segments[0].points[-1]
        dist = gpx.length_2d() / 1000
        return (start.latitude, start.longitude), (end.latitude, end.longitude), dist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gpx-files')
def get_gpx_files():
    gpx_dir = 'gpx'
    if not os.path.exists(gpx_dir):
        return jsonify([])
    # Restituisce i file in ordine alfabetico
    files = sorted([f for f in os.listdir(gpx_dir) if f.endswith('.gpx')])
    return jsonify(files)

@app.route('/gpx/<filename>')
def serve_gpx(filename):
    return send_file(os.path.join('gpx', filename))

@app.route('/generate', methods=['POST'])
def generate():
    dati = request.json
    tappe = dati.get('tappe', [])
    
    if not tappe:
        return jsonify({"error": "Nessuna tappa selezionata"}), 400

    # Recupera la chiave API dalle variabili di ambiente di Cloud Run
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    gmaps = googlemaps.Client(key=api_key) if api_key else None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Il mio Cammino", align='C', new_x="LMARGIN", new_y="NEXT")
    
    prev_end_coords = None

    for tappa_file in tappe:
        filepath = os.path.join('gpx', tappa_file)
        if not os.path.exists(filepath):
            continue

        start_coords, end_coords, dist = get_gpx_info(filepath)
        
        # Stampa i dati della tappa sul PDF
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"Tappa: {tappa_file}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 10, f"Distanza a piedi: {dist:.2f} km", new_x="LMARGIN", new_y="NEXT")

        # Se c'è un salto tra le tappe, cerca i mezzi pubblici
        if prev_end_coords and gmaps:
            directions = gmaps.directions(prev_end_coords, start_coords, mode="transit")
            if directions:
                pdf.set_text_color(0, 0, 255)
                pdf.cell(0, 10, "Spostamento con mezzi pubblici richiesto:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                duration = directions[0]['legs'][0]['duration']['text']
                pdf.cell(0, 10, f"Durata stimata: {duration}", new_x="LMARGIN", new_y="NEXT")
                # Qui potresti estrarre e aggiungere anche le istruzioni dettagliate (es. "Prendi bus X")
        
        prev_end_coords = end_coords

    # Salva temporaneamente il PDF e invialo all'utente
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, "Itinerario_Generato.pdf")
    pdf.output(pdf_path)
    
    return send_file(pdf_path, as_attachment=True, download_name="Itinerario_Viaggio.pdf")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
