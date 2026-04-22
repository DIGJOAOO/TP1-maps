import pygame
import requests
import sys
import webbrowser
import datetime

pygame.init()

WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GitHub API")

clock = pygame.time.Clock()

font = pygame.font.Font("assets/font/ThisAppeal-FreeDemo.ttf", 22)
font_big = pygame.font.Font("assets/font/ThisAppeal-FreeDemo.ttf", 48)

colores = {
    "Python": (255, 215, 0),
    "JavaScript": (240, 230, 140),
    "TypeScript": (100, 149, 237),
    "C++": (70,130,180),
    "C": (120,120,120),
    "Java": (255,100,100),
}

def obtener_top_repos(modo="top"):
    if modo == "top":
        url = "https://api.github.com/search/repositories?q=stars:>50000&sort=stars&order=desc"
    else:
        fecha = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.github.com/search/repositories?q=created:>{fecha}&sort=stars&order=desc"

    data = requests.get(url).json()
    repos = []

    for repo in data.get("items", [])[:7]:
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"],
            "lang": repo["language"] or "Other"
        })

    return repos

def dibujar_barras(repos, anim, mouse):
    rects = []
    x = 100
    y_base = 620
    ancho = 110
    espacio = 40

    max_stars = max(r["stars"] for r in repos)

    for i, repo in enumerate(repos):
        altura_obj = int((repo["stars"] / max_stars) * 400)
        anim[i] += (altura_obj - anim[i]) * 0.1

        color = colores.get(repo["lang"], (200,200,200))

        rect = pygame.Rect(x, y_base - anim[i], ancho, anim[i])
        pygame.draw.rect(screen, color, rect)

        if rect.collidepoint(mouse):
            pygame.draw.rect(screen, (255,255,255), rect, 3)

        txt = font.render(repo["name"], True, (255,255,255))
        screen.blit(txt, (x, y_base + 10))

        stars = font.render(str(repo["stars"]), True, (255,255,255))
        screen.blit(stars, (x, y_base - anim[i] - 25))

        rects.append((rect, repo))
        x += ancho + espacio

    return rects

def main():
    modo = "top"
    repos = obtener_top_repos(modo)
    anim = [0]*10
    barras = []

    running = True

    while running:
        clock.tick(60)
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, repo in barras:
                    if rect.collidepoint(mouse):
                        webbrowser.open(repo["url"])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    modo = "trending" if modo == "top" else "top"
                    repos = obtener_top_repos(modo)
                    anim = [0]*10
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((128, 128, 128))

        titulo = font_big.render(f"GitHub {modo.upper()} REPOS", True, (114, 114, 114))
        screen.blit(titulo, (WIDTH//2 - 300, 40))

        ayuda = font.render("T = cambiar Top/Trending | Click = abrir repo | ESC = volver", True, (150,150,150))
        screen.blit(ayuda, (WIDTH//2 - 250, 100))

        barras = dibujar_barras(repos, anim, mouse)

        pygame.display.flip()

if __name__ == "__main__":
    main()