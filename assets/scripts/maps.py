import json
import pygame
import requests
import time

def cargar_mapa(ruta_geojson="assets/json/countries.geojson"):
    with open(ruta_geojson, "r", encoding="utf-8") as f:
        return json.load(f)

def obtener_terremotos():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    return requests.get(url).json()["features"]

def dibujar_mapa(screen, data, zoom, offset_x, offset_y, terremotos=None):
    WIDTH, HEIGHT = screen.get_size()

    COLOR_FONDO = (128, 128, 128)
    COLOR_LINEA = (114, 114, 114)
    COLOR_PAIS = (100, 100, 100)
    GROSOR_LINEA = 2
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

    if terremotos:
        for quake in terremotos:
            coords = quake["geometry"]["coordinates"]
            mag = quake["properties"]["mag"]

            if not mag or mag < 2:
                continue

            lon, lat = coords[0], coords[1]
            x, y = transform(lon, lat)

            if mag < 3:
                color = (255, 255, 0)
            elif mag < 5:
                color = (255, 140, 0)
            else:
                color = (255, 0, 0)

            size = max(2, int(mag * 1.5))
            pygame.draw.circle(screen, color, (x, y), size)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    font = pygame.font.SysFont("ThisAppeal-FreeDemo", 20)

    for quake in terremotos:
        coords = quake["geometry"]["coordinates"]
        mag = quake["properties"]["mag"]

        if not mag:
            continue

        lon, lat = coords[0], coords[1]
        x, y = transform(lon, lat)

        if mag < 3:
            color = (255, 255, 0)
        elif mag < 5:
            color = (255, 140, 0)
        else:
            color = (255, 0, 0)

        size = max(2, int(mag * 1.5))
        pygame.draw.circle(screen, color, (x, y), size)

        dx = mouse_x - x
        dy = mouse_y - y
        dist = (dx**2 + dy**2)**0.5

        if dist < size + 5:
            info = f"{quake['properties']['place']} | M{mag}"
            text = font.render(info, True, (0, 0, 0))
            screen.blit(text, (mouse_x + 10, mouse_y + 10))

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    mapa = cargar_mapa()
    terremotos = obtener_terremotos()
    ultimo_update = time.time()

    zoom = 1
    offset_x = 0
    offset_y = 0

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 0.1
                zoom = max(0.5, min(zoom, 5))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            offset_x += 10
        if keys[pygame.K_RIGHT]:
            offset_x -= 10
        if keys[pygame.K_UP]:
            offset_y += 10
        if keys[pygame.K_DOWN]:
            offset_y -= 10

        if time.time() - ultimo_update > 60:
            terremotos = obtener_terremotos()
            ultimo_update = time.time()

        min_x, max_x, min_y, max_y = limites_mapa(screen, mapa, zoom)
        offset_x = max(min_x, min(max_x, offset_x))
        offset_y = max(min_y, min(max_y, offset_y))

        dibujar_mapa(screen, mapa, zoom, offset_x, offset_y, terremotos)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()