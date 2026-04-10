from maps import cargar_mapa, dibujar_mapa, limites_mapa
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Maps")

font = pygame.font.SysFont("ThisAppeal-FreeDemo", 40)

background_color = (128, 128, 128)
button_color = (100, 100, 100)

maps_button = pygame.Rect(422, 300, 200, 50)
api_button = pygame.Rect(844, 300, 200, 50)
exit_button = pygame.Rect(640, 500, 200, 50) 

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

def draw_button(rect, text):
    pygame.draw.rect(screen, button_color, rect)
    text_surf = font.render(text, True, (128, 128, 128))
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
        draw_button(maps_button, "Maps")
        draw_button(api_button, "API")
        draw_button(exit_button, "Exit")

    elif estado == "mapa":
        dibujar_mapa(screen, data, zoom, offset_x, offset_y)

    pygame.display.flip()
    clock.tick(60)