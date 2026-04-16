import json
import pygame
import requests
import threading
from functools import lru_cache

screen = pygame.display.set_mode((1366, 768))

esc_logo = pygame.image.load("assets/images/esc_button.png").convert_alpha()

screen.blit(esc_logo,(100, 100))
def cargar_mapa(ruta_geojson="assets/json/countries.geojson"):
    with open(ruta_geojson, "r", encoding="utf-8") as f:
        return json.load(f)

def obtener_terremotos():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        return requests.get(url, timeout=10).json()["features"]
    except Exception:
        return []

def preprocesar_mapa(data):
   
    min_lon, min_lat =  float("inf"),  float("inf")
    max_lon, max_lat = float("-inf"), float("-inf")

    poligonos = [] 

    for feature in data["features"]:
        geom   = feature["geometry"]
        nombre = feature["properties"].get("name", "")
        rings  = []

        if geom["type"] == "Polygon":
            rings = geom["coordinates"]
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                rings.extend(poly)

        for ring in rings:
            coords = [(lon, lat) for lon, lat, *_ in ring]  
            poligonos.append({"nombre": nombre, "coords": coords})

            for lon, lat in coords:
                if lon < min_lon: min_lon = lon
                if lat < min_lat: min_lat = lat
                if lon > max_lon: max_lon = lon
                if lat > max_lat: max_lat = lat

    return {
        "poligonos": poligonos,
        "bounds": (min_lon, min_lat, max_lon, max_lat),
    }

def limites_mapa(screen, mapa_pre, zoom):
    WIDTH, HEIGHT = screen.get_size()
    PADDING = 20
    min_lon, min_lat, max_lon, max_lat = mapa_pre["bounds"]

    scale   = min((WIDTH  - 2*PADDING) / (max_lon - min_lon),
                  (HEIGHT - 2*PADDING) / (max_lat - min_lat))
    map_w   = (max_lon - min_lon) * scale * zoom
    map_h   = (max_lat - min_lat) * scale * zoom

    return WIDTH - map_w - PADDING, PADDING, HEIGHT - map_h - PADDING, PADDING

_cache_poligonos: dict = {}   
_cache_key       = None

def _build_scale(screen, mapa_pre, zoom):
    WIDTH, HEIGHT = screen.get_size()
    PADDING = 20
    min_lon, min_lat, max_lon, max_lat = mapa_pre["bounds"]
    scale = min((WIDTH  - 2*PADDING) / (max_lon - min_lon),
                (HEIGHT - 2*PADDING) / (max_lat - min_lat))
    return scale, min_lon, max_lat

def _transform(lon, lat, scale, zoom, min_lon, max_lat, offset_x, offset_y, PADDING=20):
    x = (lon - min_lon) * scale * zoom + PADDING + offset_x
    y = (max_lat - lat) * scale * zoom + PADDING + offset_y
    return int(x), int(y)

def dibujar_mapa(screen, mapa_pre, zoom, offset_x, offset_y, terremotos=None):
    global _cache_key

    WIDTH, HEIGHT   = screen.get_size()
    COLOR_FONDO     = (128, 128, 128)
    COLOR_LINEA     = (114, 114, 114)
    COLOR_PAIS      = (100, 100, 100)
    PADDING         = 20

    scale, min_lon, max_lat = _build_scale(screen, mapa_pre, zoom)

    def transform(lon, lat):
        return _transform(lon, lat, scale, zoom, min_lon, max_lat,
                          offset_x, offset_y, PADDING)

    screen.fill(COLOR_FONDO)

    cache_key = (round(zoom, 2), round(offset_x), round(offset_y), WIDTH, HEIGHT)

    if cache_key != _cache_key or cache_key not in _cache_poligonos:
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

        for poly in mapa_pre["poligonos"]:
            points = [transform(lon, lat) for lon, lat in poly["coords"]]

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            poly_rect = pygame.Rect(min(xs), min(ys),
                                    max(xs)-min(xs), max(ys)-min(ys))
            if not screen_rect.colliderect(poly_rect):
                continue

            if len(points) >= 3:
                pygame.draw.polygon(surf, COLOR_PAIS,  points)
                pygame.draw.polygon(surf, COLOR_LINEA, points, 1)

        _cache_poligonos.clear()
        _cache_poligonos[cache_key] = surf
        _cache_key = cache_key

    screen.blit(_cache_poligonos[cache_key], (0, 0))

    font_cont  = pygame.font.SysFont("ThisAppeal-FreeDemo", 28)
    font_pais  = pygame.font.SysFont("ThisAppeal-FreeDemo", 14)
    font_quake = pygame.font.SysFont("ThisAppeal-FreeDemo", 20)
    t = max(0.0, min(1.0, (zoom - 1.5) / 1.5))
    alpha_cont = int(255 * (1 - t))
    alpha_pais = int(255 * t)

    continentes = [
        ("América del Norte", -100, 50),
        ("América del Sur",    -60, -20),
        ("Europa",              10,  50),
        ("África",              20,   0),
        ("Asia",                90,  40),
        ("Oceanía",            140, -25),
        ("Antártida",            0,  -80),
    ]

    if alpha_cont > 0:
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for nombre, lon, lat in continentes:
            x, y = transform(lon, lat)
            if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT):
                continue
            text = font_cont.render(nombre, True, (200, 200, 200, alpha_cont))
            surf.blit(text, text.get_rect(center=(x, y)))
        screen.blit(surf, (0, 0))

    if alpha_pais > 0:
        surf     = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dibujados = set()

        for poly in mapa_pre["poligonos"]:
            nombre = poly["nombre"]
            if nombre in dibujados:
                continue
            dibujados.add(nombre)

            coords = poly["coords"]
            n      = len(coords)
            if n == 0:
                continue
            cx = sum(transform(lon, lat)[0] for lon, lat in coords) // n
            cy = sum(transform(lon, lat)[1] for lon, lat in coords) // n

            if not (0 <= cx <= WIDTH and 0 <= cy <= HEIGHT):
                continue

            text = font_pais.render(nombre, True, (180, 180, 180, alpha_pais))
            surf.blit(text, (cx, cy))

        screen.blit(surf, (0, 0))

    if terremotos:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_info = None

        for quake in terremotos:
            coords = quake["geometry"]["coordinates"]
            mag    = quake["properties"].get("mag")
            if not mag or mag < 2:
                continue

            x, y = transform(coords[0], coords[1])

            if not (-10 <= x <= WIDTH+10 and -10 <= y <= HEIGHT+10):
                continue

            color = (255, 255, 0) if mag < 3 else (255, 140, 0) if mag < 5 else (255, 0, 0)
            size  = max(2, int(mag * 1.5))
            pygame.draw.circle(screen, color, (x, y), size)

            if hover_info is None:
                dist = ((mouse_x-x)**2 + (mouse_y-y)**2)**0.5
                if dist < size + 5:
                    hover_info = f"{quake['properties']['place']} | M{mag}"

        if hover_info:
            text = font_quake.render(hover_info, True, (0, 0, 0))
            screen.blit(text, (mouse_x + 10, mouse_y + 10))

_terremotos_cache = []
_lock             = threading.Lock()

def iniciar_descarga_terremotos():
    def _loop():
        import time
        while True:
            try:
                data = requests.get(
                    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
                    timeout=10
                ).json()["features"]
                with _lock:
                    _terremotos_cache.clear()
                    _terremotos_cache.extend(data)
            except Exception:
                pass
            time.sleep(300)  

    t = threading.Thread(target=_loop, daemon=True)
    t.start()

def get_terremotos():
    with _lock:
        return list(_terremotos_cache)