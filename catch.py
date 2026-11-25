import pygame
import random
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Catch Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 220, 60)

clock = pygame.time.Clock()
FPS = 60

# Spelaren: en blå platta längst ner
player_width = 80
player_height = 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 40
player_speed = 8

# Fallande objektet: en röd kvadrat
object_size = 30
object_x = random.randint(60, WIDTH - object_size - 60)
object_y = -object_size
object_speed = 4

# Poäng, liv och nivå
score = 0
lives = 3
level = 1

# Paus och state (menu, play, gameover)
paused = False
state = "menu"
new_best = False

font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 20)


# load_best() läser highscore från fil
def load_best():
    try:
        f = open("catch_best.txt")
        data = f.read()
        f.close()
        return int(data)
    except:
        return 0


# save_best(value) skriver nytt rekord till fil
def save_best(value):
    try:
        f = open("catch_best.txt", "w")
        f.write(str(value))
        f.close()
    except:
        pass


best = load_best()


# reset_object() slumpar ny position och hastighet åt objektet
def reset_object():
    global object_x
    global object_y
    global object_speed
    # Objektet spawnar alltid minst 60 pixlar från skärmkanterna
    # så plattan hinner dit oavsett var den står
    object_x = random.randint(60, WIDTH - object_size - 60)
    object_y = -object_size
    # Hastigheten ökar med nivån men maxas så det alltid går att fånga
    speed = random.randint(3, 5) + level
    if speed > 9:
        speed = 9
    object_speed = speed


# reset_game() nollställer allt inför en ny runda
def reset_game():
    global player_x
    global score
    global lives
    global level
    global object_y
    global new_best
    player_x = WIDTH // 2 - player_width // 2
    score = 0
    lives = 3
    level = 1
    object_y = -object_size
    new_best = False
    reset_object()


# LOOP: läser tangenter och uppdaterar spelet
running = True
while running:
    clock.tick(FPS)

    # Läs tangenter
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # ESC avslutar
            if event.key == pygame.K_ESCAPE:
                running = False

            # P växlar paus om state är "play"
            if event.key == pygame.K_p:
                if state == "play":
                    paused = not paused

            # SPACE startar ny runda från meny eller game over
            if event.key == pygame.K_SPACE:
                if state == "menu":
                    state = "play"
                    reset_game()
                elif state == "gameover":
                    state = "play"
                    reset_game()

            # M går till meny från game over
            if event.key == pygame.K_m:
                if state == "gameover":
                    state = "menu"

    # Om state är "play" och inte pausad: uppdatera spelet
    if state == "play":
        if not paused:
            keys = pygame.key.get_pressed()

            # Flytta spelaren med vänster och höger
            if keys[pygame.K_LEFT]:
                if player_x > 0:
                    player_x = player_x - player_speed

            if keys[pygame.K_RIGHT]:
                if player_x < WIDTH - player_width:
                    player_x = player_x + player_speed

            # Flytta objektet nedåt
            object_y = object_y + object_speed

            # Om spelaren fångar objektet: +1 poäng, kolla nivå, nytt objekt
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            object_rect = pygame.Rect(object_x, object_y, object_size, object_size)

            if player_rect.colliderect(object_rect):
                score = score + 1
                level = 1 + score // 5
                reset_object()

            # Om objektet når botten: tappa ett liv, eller game over om inga liv kvar
            if object_y > HEIGHT:
                lives = lives - 1

                if lives <= 0:
                    state = "gameover"

                    # Spara highscore om det är nytt rekord
                    if score > best:
                        best = score
                        new_best = True
                        save_best(best)
                else:
                    # Säkerställ att objektet alltid går att nå
                    if object_x < 0:
                        object_x = 0
                    if object_x > WIDTH - object_size:
                        object_x = WIDTH - object_size
                    reset_object()

    screen.fill(BLACK)

    # Rita skärmen beroende på state
    if state == "play":
        # Spelare och objekt
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
        pygame.draw.rect(screen, RED, (object_x, object_y, object_size, object_size))

        # Poäng, liv, nivå, highscore
        score_text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 10))

        lives_text = font.render("Lives: " + "O " * lives, True, WHITE)
        screen.blit(lives_text, (10, 45))

        level_text = font.render("Level: " + str(level), True, WHITE)
        screen.blit(level_text, (10, 80))

        best_text = font.render("Best: " + str(best), True, YELLOW)
        screen.blit(best_text, (WIDTH - 200, 10))

        # Om pausad: rita "PAUSED"
        if paused:
            pause_text = font.render("PAUSED", True, GREEN)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

            info_text = small_font.render("Tryck P for att fortsatta", True, WHITE)
            info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(info_text, info_rect)

    elif state == "menu":
        # Titel, styrning, "Tryck SPACE"
        title_text = font.render("SIMPLE CATCH", True, GREEN)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        info1 = small_font.render("Vanster / Hoger = flytta plattan", True, WHITE)
        screen.blit(info1, (WIDTH // 2 - 150, 220))

        info2 = small_font.render("P = paus", True, WHITE)
        screen.blit(info2, (WIDTH // 2 - 150, 250))

        info3 = small_font.render("SPACE = starta", True, WHITE)
        screen.blit(info3, (WIDTH // 2 - 150, 280))

        info4 = small_font.render("Fanga roda rutor = +1 poang", True, WHITE)
        screen.blit(info4, (WIDTH // 2 - 150, 310))

        start_text = font.render("Tryck SPACE for att borja", True, YELLOW)
        start_rect = start_text.get_rect(center=(WIDTH // 2, 480))
        screen.blit(start_text, start_rect)

    elif state == "gameover":
        # "GAME OVER" eller "NEW HIGH SCORE", poäng, "SPACE / M"
        if new_best == True:
            msg_text = font.render("NEW HIGH SCORE!", True, YELLOW)
        else:
            msg_text = font.render("GAME OVER!", True, GREEN)

        msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(msg_text, msg_rect)

        score_text = font.render("Score: " + str(score) + "  Best: " + str(best), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(score_text, score_rect)

        hint_text = small_font.render("SPACE = spela igen    M = meny", True, YELLOW)
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(hint_text, hint_rect)

    # Visa på skärmen och vänta till nästa bildruta
    pygame.display.flip()

pygame.quit()
sys.exit()