import json
import tkinter as tk

def mostrar_mapa(parent, ruta_geojson="assets/json/countries.geojson"):
    COLOR_FONDO = "#5DCCFF"        
    COLOR_LINEA = "#000000"       
    COLOR_PAIS = "#FFFFFF"      
    GROSOR_LINEA = 1
    PADDING = 20

    for widget in parent.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(parent, bg=COLOR_FONDO)
    canvas.pack(fill="both", expand=True)

    parent.update_idletasks()

    WIDTH = canvas.winfo_width()
    HEIGHT = canvas.winfo_height()

    with open(ruta_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)

    min_lon, min_lat = float("inf"), float("inf")
    max_lon, max_lat = float("-inf"), float("-inf")

    def update_bounds(coords):
        nonlocal min_lon, min_lat, max_lon, max_lat
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

    def draw_map():
        canvas.delete("all")

        def draw_polygon(coords):
            points = []
            for lon, lat in coords:
                x, y = transform(lon, lat)
                points.extend([x, y])
            canvas.create_polygon(points, outline=COLOR_LINEA, fill=COLOR_PAIS, width=GROSOR_LINEA)

        for feature in data["features"]:
            geom = feature["geometry"]

            if geom["type"] == "Point":
                lon, lat = geom["coordinates"]
                x, y = transform(lon, lat)
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                                   fill=COLOR_PAIS, outline=COLOR_LINEA)

            elif geom["type"] == "LineString":
                points = []
                for lon, lat in geom["coordinates"]:
                    x, y = transform(lon, lat)
                    points.extend([x, y])
                canvas.create_line(points, fill=COLOR_LINEA)

            elif geom["type"] == "Polygon":
                for ring in geom["coordinates"]:
                    draw_polygon(ring)

            elif geom["type"] == "MultiPolygon":
                for polygon in geom["coordinates"]:
                    for ring in polygon:
                        draw_polygon(ring)

    draw_map()

    zoom_level = 1

    def zoom(event):
        nonlocal zoom_level

        if event.delta > 0 and zoom_level < 5:
            factor = 1.1
            zoom_level *= factor
        elif event.delta < 0 and zoom_level > 0.5:
            factor = 0.9
            zoom_level *= factor
        else:
            return

        canvas.scale("all", event.x, event.y, factor, factor)

    canvas.bind("<MouseWheel>", zoom)

    def start_drag(event):
        canvas.scan_mark(event.x, event.y)

    def drag(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    canvas.bind("<Button-1>", start_drag)
    canvas.bind("<B1-Motion>", drag)