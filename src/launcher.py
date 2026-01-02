import pygame
import subprocess
import sys
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = 500, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tileborn Launcher")

FONT = pygame.font.SysFont(None, 36)
SMALL = pygame.font.SysFont(None, 24)

BG_COLOR = (30, 30, 30)
BTN_COLOR = (70, 70, 70)
BTN_HOVER = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)

# Caminho do jogo
BASE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
GAME_EXE = BASE_DIR / "Tileborn.exe"

def draw_button(rect, text, mouse_pos):
    color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=6)

    txt = FONT.render(text, True, TEXT_COLOR)
    screen.blit(
        txt,
        (
            rect.centerx - txt.get_width() // 2,
            rect.centery - txt.get_height() // 2
        )
    )

def main():
    clock = pygame.time.Clock()

    play_btn = pygame.Rect(150, 80, 200, 50)
    quit_btn = pygame.Rect(150, 150, 200, 50)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(mouse_pos):
                    if GAME_EXE.exists():
                        subprocess.Popen([str(GAME_EXE)])
                    running = False

                elif quit_btn.collidepoint(mouse_pos):
                    running = False

        screen.fill(BG_COLOR)

        title = FONT.render("Tileborn", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        draw_button(play_btn, "Play", mouse_pos)
        draw_button(quit_btn, "Quit", mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
