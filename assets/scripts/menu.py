from maps import cargar_mapa, dibujar_mapa, limites_mapa, obtener_terremotos
import pygame
import sys
import webbrowser

pygame.init()

screen = pygame.display.set_mode((1366, 768))
pygame.display.set_caption("Maps")

logo_git = pygame.image.load("assets/images/github_logo.png").convert_alpha()
logo_maps = pygame.image.load("assets/images/maps_logo.png").convert_alpha()
logo = pygame.image.load("assets/images/logo.png").convert_alpha()

font = pygame.font.SysFont("ThisAppeal-FreeDemo", 40)

background_color = (128, 128, 128)

maps_button = pygame.Rect(375, 400, 200, 50)
api_button = pygame.Rect(827, 400, 200, 50)
exit_button = pygame.Rect(608, 600, 200, 50)
basket_button = pygame.Rect(5, 5, 50, 50)

estado = "menu"

data = cargar_mapa()

zoom = 1
MIN_ZOOM = 0.8
MAX_ZOOM = 6

offset_x = 0
offset_y = 0

dragging = False
last_mouse = (0, 0)

clock = pygame.time.Clock()

scroll_x = 0
speed = 1

def recolor_iconos(image, color):
    new_img = image.copy()
    new_img.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    new_img.fill(color + (0,), None, pygame.BLEND_RGBA_ADD)
    return new_img

icono_maps = recolor_iconos(logo_maps, (120, 120, 120))
icono_git = recolor_iconos(logo_git, (120, 120, 120))

icono_maps = pygame.transform.smoothscale(icono_maps, (100, 100))
icono_git = pygame.transform.smoothscale(icono_git, (100, 100))

def draw_button(rect, text):
    mouse_pos = pygame.mouse.get_pos()
    color = (100, 100, 100)
    if rect.collidepoint(mouse_pos):
        color = (60, 60, 60)
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, (200, 200, 200))
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if estado == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if maps_button.collidepoint(event.pos):
                    estado = "mapa"
                elif api_button.collidepoint(event.pos):
                    print("API")
                elif basket_button.collidepoint(event.pos):
                    webbrowser.open("https://poki.com/es/g/basketball-stars")
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        elif estado == "mapa":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    estado = "menu"

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom *= 1.1
                else:
                    zoom *= 0.9
                zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            if event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]

                offset_x += dx
                offset_y += dy

                min_x, max_x, min_y, max_y = limites_mapa(screen, data, zoom)

                offset_x = max(min_x, min(max_x, offset_x))
                offset_y = max(min_y, min(max_y, offset_y))

                last_mouse = event.pos

    if estado == "menu":
        screen.fill(background_color)

        scroll_x -= speed
        if scroll_x <= -200:
            scroll_x = 0

        for y in range(0, 768, 200):
            for x in range(-200, 1666, 200):
                x_pos = x + scroll_x

                if (y // 200) % 2 == 1:
                    x_pos += 100

                if ((x // 200) + (y // 200)) % 2 == 0:
                    screen.blit(icono_git, (x_pos, y))
                else:
                    screen.blit(icono_maps, (x_pos, y))

        draw_button(maps_button, "Maps")
        draw_button(api_button, "API")
        draw_button(exit_button, "Exit")
        draw_button(basket_button, "?")
        screen.blit(logo, (-50, -300))

    elif estado == "mapa":
        terremotos = obtener_terremotos()
        dibujar_mapa(screen, data, zoom, offset_x, offset_y, terremotos)

    pygame.display.flip()
    clock.tick(60)