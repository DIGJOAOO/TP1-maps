import json
import pygame
import requests

pygame.init()

screen = pygame.display.set_mode((1366, 768))
pygame.display.set_caption("Maps")

clock = pygame.time.Clock()

def cargar_mapa(ruta_geojson="assets/json/countries.geojson"):
    with open(ruta_geojson, "r", encoding="utf-8") as f:
        return json.load(f)

def obtener_terremotos():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    return requests.get(url).json()["features"]


def buscar_pais(data, nombre):
    nombre = nombre.lower()
    for feature in data["features"]:
        if nombre in feature["properties"].get("name", "").lower():
            return feature
    return None

def centro_pais(feature):
    geom = feature["geometry"]
    coords = geom["coordinates"]
    puntos = []

    if geom["type"] == "Polygon":
        for ring in coords:
            for lon, lat in ring:
                puntos.append((lon, lat))

    elif geom["type"] == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                for lon, lat in ring:
                    puntos.append((lon, lat))

    if not puntos:
        return None

    cx = sum(p[0] for p in puntos) / len(puntos)
    cy = sum(p[1] for p in puntos) / len(puntos)

    return cx, cy

def centrar_en_pais(screen, data, zoom, lon, lat):
    WIDTH, HEIGHT = screen.get_size()
    PADDING = 20

    min_lon, min_lat = float("inf"), float("inf")
    max_lon, max_lat = float("-inf"), float("-inf")

    def update_bounds(coords):
        nonlocal min_lon, min_lat, max_lon, max_lat
        for lo, la in coords:
            min_lon = min(min_lon, lo)
            min_lat = min(min_lat, la)
            max_lon = max(max_lon, lo)
            max_lat = max(max_lat, la)

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

    x = (lon - min_lon) * scale * zoom + PADDING
    y = (max_lat - lat) * scale * zoom + PADDING

    offset_x = WIDTH // 2 - x
    offset_y = HEIGHT // 2 - y

    return offset_x, offset_y

def dibujar_mapa(screen, data, zoom, offset_x, offset_y, terremotos=None):
    WIDTH, HEIGHT = screen.get_size()

    COLOR_FONDO = (128, 128, 128)
    COLOR_LINEA = (114, 114, 114)
    COLOR_PAIS = (100, 100, 100)

    PADDING = 20

    font_pais = pygame.font.SysFont("ThisAppeal-FreeDemo", 14)
    font_cont = pygame.font.SysFont("ThisAppeal-FreeDemo", 28)
    font_quake = pygame.font.SysFont("ThisAppeal-FreeDemo", 20)

    continentes = [
        ("América del Norte", -100, 50),
        ("América del Sur", -60, -20),
        ("Europa", 10, 50),
        ("África", 20, 0),
        ("Asia", 90, 40),
        ("Oceanía", 140, -25),
        ("Antártida", 0, -45)
    ]

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
                pygame.draw.polygon(screen, COLOR_LINEA, points, 1)

        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for ring in polygon:
                    points = [transform(lon, lat) for lon, lat in ring]
                    pygame.draw.polygon(screen, COLOR_PAIS, points)
                    pygame.draw.polygon(screen, COLOR_LINEA, points, 1)

    t = max(0, min(1, (zoom - 1.5) / 1.5))
    alpha_cont = int(255 * (1 - t))
    alpha_pais = int(255 * t)

    if alpha_cont > 0:
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for nombre, lon, lat in continentes:
            x, y = transform(lon, lat)
            text = font_cont.render(nombre, True, (200, 200, 200))
            text.set_alpha(alpha_cont)
            surface.blit(text, text.get_rect(center=(x, y)))

        screen.blit(surface, (0, 0))

    if alpha_pais > 0:
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dibujados = set()

        for feature in data["features"]:
            nombre = feature["properties"].get("name", "")
            if nombre in dibujados:
                continue
            dibujados.add(nombre)

            geom = feature["geometry"]
            puntos = []

            if geom["type"] == "Polygon":
                for ring in geom["coordinates"]:
                    for lon, lat in ring:
                        puntos.append(transform(lon, lat))

            elif geom["type"] == "MultiPolygon":
                for polygon in geom["coordinates"]:
                    for ring in polygon:
                        for lon, lat in ring:
                            puntos.append(transform(lon, lat))

            if not puntos:
                continue

            cx = sum(p[0] for p in puntos) // len(puntos)
            cy = sum(p[1] for p in puntos) // len(puntos)

            text = font_pais.render(nombre, True, (180, 180, 180))
            text.set_alpha(alpha_pais)
            surface.blit(text, (cx, cy))

        screen.blit(surface, (0, 0))

    if terremotos:
        mouse_x, mouse_y = pygame.mouse.get_pos()

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

            if ((mouse_x - x)**2 + (mouse_y - y)**2)**0.5 < size + 5:
                info = f"{quake['properties']['place']} | M{mag}"
                text = font_quake.render(info, True, (0, 0, 0))
                screen.blit(text, (mouse_x + 10, mouse_y + 10))

data = cargar_mapa()
terremotos = obtener_terremotos()

zoom = 1
offset_x = 0
offset_y = 0

dragging = False
last_mouse = (0, 0)

buscando = False
texto_busqueda = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse = pygame.mouse.get_pos()

            elif event.button == 4:
                zoom *= 1.1
            elif event.button == 5:
                zoom /= 1.1

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            mx, my = pygame.mouse.get_pos()
            dx = mx - last_mouse[0]
            dy = my - last_mouse[1]
            offset_x += dx
            offset_y += dy
            last_mouse = (mx, my)

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_f:
                buscando = True
                texto_busqueda = ""

            elif buscando:
                if event.key == pygame.K_RETURN:
                    pais = buscar_pais(data, texto_busqueda)

                    if pais:
                        centro = centro_pais(pais)
                        if centro:
                            lon, lat = centro
                            offset_x, offset_y = centrar_en_pais(screen, data, zoom, lon, lat)

                    buscando = False

                elif event.key == pygame.K_BACKSPACE:
                    texto_busqueda = texto_busqueda[:-1]

                else:
                    texto_busqueda += event.unicode

    dibujar_mapa(screen, data, zoom, offset_x, offset_y, terremotos)

    if buscando:
        font_ui = pygame.font.SysFont("ThisAppeal-FreeDemo", 30)
        texto = font_ui.render("Buscar: " + texto_busqueda, True, (255,255,255))
        pygame.draw.rect(screen, (0,0,0), (10, 10, 400, 50))
        screen.blit(texto, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()