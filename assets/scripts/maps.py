import json
import pygame

def cargar_mapa(ruta_geojson="assets/json/countries.geojson"):
    with open(ruta_geojson, "r", encoding="utf-8") as f:
        return json.load(f)


def dibujar_mapa(screen, data, zoom, offset_x, offset_y):
    WIDTH, HEIGHT = screen.get_size()

    COLOR_FONDO = (128, 128, 128)
    COLOR_LINEA = (100, 100, 100)
    COLOR_PAIS = (128, 128, 128)
    GROSOR_LINEA = 3
    PADDING = 20

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
        if geom["type"] == "Polygon":
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
        x = (lon - min_lon) * scale * zoom + PADDING + offset_x
        y = (max_lat - lat) * scale * zoom + PADDING + offset_y
        return int(x), int(y)

    screen.fill(COLOR_FONDO)

    for feature in data["features"]:
        geom = feature["geometry"]

        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                points = [transform(lon, lat) for lon, lat in ring]
                pygame.draw.polygon(screen, COLOR_PAIS, points)
                pygame.draw.polygon(screen, COLOR_LINEA, points, GROSOR_LINEA)

        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for ring in polygon:
                    points = [transform(lon, lat) for lon, lat in ring]
                    pygame.draw.polygon(screen, COLOR_PAIS, points)
                    pygame.draw.polygon(screen, COLOR_LINEA, points, GROSOR_LINEA)


def limites_mapa(screen, data, zoom):
    WIDTH, HEIGHT = screen.get_size()
    PADDING = 20

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
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                update_bounds(ring)
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for ring in polygon:
                    update_bounds(ring)

    scale_x = (WIDTH - 2 * PADDING) / (max_lon - min_lon)
    scale_y = (HEIGHT - 2 * PADDING) / (max_lat - min_lat)
    scale = min(scale_x, scale_y)

    map_width = (max_lon - min_lon) * scale * zoom
    map_height = (max_lat - min_lat) * scale * zoom

    min_offset_x = WIDTH - map_width - PADDING
    max_offset_x = PADDING
    min_offset_y = HEIGHT - map_height - PADDING
    max_offset_y = PADDING

    return min_offset_x, max_offset_x, min_offset_y, max_offset_y