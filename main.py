import json
import tkinter as tk


COLOR_FONDO = "#5DCCFF"        
COLOR_LINEA = "#000000"       
COLOR_PAIS = "#FFFFFF"      
GROSOR_LINEA = 1

WIDTH, HEIGHT = 1280, 720
PADDING = 20

with open("countries.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

min_lon, min_lat = float("inf"), float("inf")
max_lon, max_lat = float("-inf"), float("-inf")

def update_bounds(coords):
    global min_lon, min_lat, max_lon, max_lat
    for lon, lat in coords:
        min_lon = min(min_lon, lon)
        min_lat = min(min_lat, lat)
        max_lon = max(max_lon, lon)
        max_lat = max(max_lat, lat)

for feature in data["features"]:
    geom = feature["geometry"]
    if geom["type"] == "Point":
        update_bounds([geom["coordinates"]])
    elif geom["type"] == "LineString":
        update_bounds(geom["coordinates"])
    elif geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            update_bounds(ring)
    elif geom["type"] == "MultiPolygon":
        for polygon in geom["coordinates"]:
            for ring in polygon:
                update_bounds(ring)

scale_x = (WIDTH - 2 * PADDING) / (max_lon - min_lon)
scale_y = (HEIGHT - 2 * PADDING) / (max_lat - min_lat)
scale = min(scale_x, scale_y)

def transform(lon, lat):
    x = (lon - min_lon) * scale + PADDING
    y = (max_lat - lat) * scale + PADDING
    return x, y

root = tk.Tk()
root.title("GeoJSON Viewer")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=COLOR_FONDO)
canvas.pack()

def draw_polygon(coords, fill_color, outline_color):
    points = []
    for lon, lat in coords:
        x, y = transform(lon, lat)
        points.extend([x, y])
    canvas.create_polygon(points, outline=outline_color, fill=fill_color, width=GROSOR_LINEA)

for feature in data["features"]:
    geom = feature["geometry"]

    if geom["type"] == "Point":
        lon, lat = geom["coordinates"]
        x, y = transform(lon, lat)
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                           fill=COLOR_PAIS, outline=COLOR_LINEA, width=GROSOR_LINEA)

    elif geom["type"] == "LineString":
        points = []
        for lon, lat in geom["coordinates"]:
            x, y = transform(lon, lat)
            points.extend([x, y])
        canvas.create_line(points, fill=COLOR_LINEA, width=GROSOR_LINEA)

    elif geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            draw_polygon(ring, fill_color=COLOR_PAIS, outline_color=COLOR_LINEA)

    elif geom["type"] == "MultiPolygon":
        for polygon in geom["coordinates"]:
            for ring in polygon:
                draw_polygon(ring, fill_color=COLOR_PAIS, outline_color=COLOR_LINEA)

root.mainloop()