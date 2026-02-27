import gpxpy
import googlemaps
from fpdf import FPDF
import json
import os

def get_gpx_info(filepath):
    with open(filepath, 'r') as f:
        gpx = gpxpy.parse(f)
        start = gpx.tracks[0].segments[0].points[0]
        end = gpx.tracks[0].segments[0].points[-1]
        dist = gpx.length_2d() / 1000
        return (start.latitude, start.longitude), (end.latitude, end.longitude), dist

def create_itinerary():
    with open('itinerario.json') as f:
        config = json.load(f)
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    gmaps = googlemaps.Client(key=api_key) if api_key else None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, config['titolo_viaggio'], align='C', new_x="LMARGIN", new_y="NEXT")
    
    prev_end_coords = None

    for tappa_file in config['tappe']:
        filepath = f"gpx/{tappa_file}"
        if not os.path.exists(filepath):
            continue

        start_coords, end_coords, dist = get_gpx_info(filepath)
        
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"Tappa: {tappa_file}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", '', 10)
        pdf.cell(0, 10, f"Distanza a piedi: {dist:.2f} km", new_x="LMARGIN", new_y="NEXT")

        if prev_end_coords and gmaps:
            directions = gmaps.directions(prev_end_coords, start_coords, mode="transit")
            if directions:
                pdf.set_text_color(0, 0, 255)
                pdf.cell(0, 10, "Spostamento con mezzi pubblici richiesto:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                duration = directions[0]['legs'][0]['duration']['text']
                pdf.cell(0, 10, f"Durata stimata: {duration}", new_x="LMARGIN", new_y="NEXT")
        
        prev_end_coords = end_coords

    pdf.output("Itinerario_Viaggio.pdf")

if __name__ == "__main__":
    create_itinerary()
