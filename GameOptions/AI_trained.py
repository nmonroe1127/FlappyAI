import pickle
import pygame
import os
import neat
import pygame.freetype

pygame.init()
pygame.font.init()
all_fonts = pygame.font.get_fonts()
font = pygame.font.SysFont(all_fonts[5], 32)

# Importing Objects from files
from neat.nn import FeedForwardNetwork
from Objects.plane import AIPlane
from Objects.rock import Rock
from Objects.base import Base

# This is a boolean value to ensure smooth transitions of menu screen
menu = True
# This is just a holder for the background image
background = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))

def ai_window(win, plane, rocks, base, score, high, full_size, alive):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(background, (0, 0))
    # Draw the multiple rocks that should be on the screen using ROCK class draw method
    for rock in rocks:
        rock.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = font.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (490 - high_score.get_width(), 10))
    # Render the score to the screen
    score = font.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (490 - score.get_width(), 45))
    # Render the number of plane left alive
    score_label = font.render("Alive: " + str(alive) + "/" + str(full_size), 1, (0, 0, 0))
    win.blit(score_label, (10, 10))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the plane
    plane.draw(win)

    stop = pygame.Rect(10, 45, 90, 27)
    pygame.draw.rect(win, (30, 30, 30), stop)
    back = pygame.font.SysFont('Times New Roman', 19).render("Stop", 1, (255, 255, 255))
    win.blit(back, (37, 47))

    # Updates the window with new visuals every frame
    pygame.display.update()

# This will hold the code for watching the AI learn
def eval_genomes(config):
    global menu
    # Declare the game window
    win = pygame.display.set_mode((500, 800))
    alive = 1
    with open('./AIConfigurations/config-best.txt', 'rb') as f:
        c = pickle.load(f)

    # Only need a singular plane because this is the best genome
    plane = AIPlane(200, 350)
    # Only need to make a singular neuron in the ANN
    neuron = FeedForwardNetwork.create(c, config)

    # The size of the plane set is only 1 that needs to be displayed
    full_size = 1

    # Intilize the background, rocks, and score
    base = Base(670)
    rocks = [Rock(700)]
    score = 0

    # This will make sure the game doesnt move to fast for the site of the viewer
    clock = pygame.time.Clock()

    # Pull down the high score from the trained AI
    try:
        with open('./HighScoreFiles/AI_highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # This will allow the user to stop watching the AI at any point
    stop = pygame.Rect(10, 45, 90, 27)
    pygame.draw.rect(win, (30, 30, 30), stop)
    back = pygame.font.SysFont('Times New Roman', 19).render("Stop", 1, (255, 255, 255))
    win.blit(back, (37, 47))


    run = True
    while run:
        clock.tick(30)
        if not menu:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if stop.collidepoint(event.pos):
                    menu = False
                    break

        add_rock = False
        for rock in rocks:
            # Keep checking to see if the plane ever collides with a rock
            if rock.collision_occurence(plane) or plane.y + plane.image_of_plane.get_height() - 10 >= 690 or plane.y < -50:
                # If it ever does than the run should end because there is only one plane
                run = False
                # Also decrement the number of planes alive to show 0/1 are alive
                alive = alive - 1
            # Once a rock passes the end of the screen we can remove it
            if rock.coordinate_pos + rock.ceiling_rock.get_width() < 0:
                rocks.remove(rock)
            # See when we need to add another rock to the screen
            if not rock.finished and rock.coordinate_pos < plane.x:
                rock.finished = True
                add_rock = True
            rock.move_left()
        # Every time a rock is passed we can increment the score by 1
        if add_rock:
            score += 1
            rocks.append(Rock(600))

        indexer = 0
        if len(rocks) > 1 and plane.x > rocks[0].coordinate_pos + rocks[
            0].ceiling_rock.get_width():
            indexer = 1

        # The plane will always move even if jump does not occur
        plane.move()

        # The activation function for neat, when above 0.5, should trigger a jump of the plane
        if neuron.activate(
                (plane.y, abs(plane.y - rocks[indexer].length), abs(plane.y - rocks[indexer].lower_bound)))[0] > 0.5:
            # Activation function passed so jump the plane
            plane.jump()

        base.move()

        ai_window(win, plane, rocks, base, score, high, full_size, alive)

    # Save the highest score of the session to file for later
    if high < score:
        with open('./HighScoreFiles/AI_highscores.dat', 'wb') as file:
            pickle.dump(score, file)


def run(config_path):
    # Setting up the ANN to be inline with the config file that is passed in
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    eval_genomes(config)


def configuration():
    # Finding the file that will hold the neural network and GA configurations
    config_path = "AIConfigurations/config-single.txt"
    # Run the file that contains the neural network configurations
    run(config_path)


# Option button 1, regular game for the user to play
def option_three(win):
    global menu
    menu = True
    # Give user the ability to choose the number of generations and population size
    configuration()

    restart_game = pygame.Rect(180, 265, 134, 45)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), restart_game)
    # Give the button some text
    restart = pygame.font.SysFont('Times New Roman', 18).render("Restart Game", 1, (255, 255, 255))
    win.blit(restart, (200, 275))

    back_to_menu = pygame.Rect(180, 345, 134, 45)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), back_to_menu)
    # Give the button some text
    back = pygame.font.SysFont('Times New Roman', 18).render("Back To Menu", 1, (255, 255, 255))
    win.blit(back, (195, 355))
    # Updates the window with new visuals every frame
    pygame.display.update()

    wait = True
    while wait:

        # Moving and jumping of the plane
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                wait = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_three(win)
                        menu = True
                        wait = False
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False
                        break



