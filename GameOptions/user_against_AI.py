import os
import pickle
import pygame
import neat
import pygame.freetype

pygame.init()
pygame.font.init()
all_fonts = pygame.font.get_fonts()
font = pygame.font.SysFont(all_fonts[5], 40)

#Importing objects from files
from Objects.plane import UserPlane
from Objects.rock import Rock
from Objects.base import Base
from Objects.plane import AIPlane
from neat.nn import FeedForwardNetwork

background = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))

FIRE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire1.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire2.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire3.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire4.png")), (80, 80))]


def ai_window(win, planeAI, plane, rocks, base, score, high):
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
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the planeAI
    planeAI.draw(win)
    plane.draw(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


def draw_window(win, plane, plane2, plane3, plane4, planeAI, rocks, base, score, high):
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
    # call the method that will draw the ground into the game
    base.draw(win)
    # Draw the AI
    planeAI.draw(win)
    # Calls the helper function to actually draw the planeAI
    plane.draw(win)
    plane2.moving(win)
    plane2.draw2(win)
    plane3.moving(win)
    plane3.draw2(win)
    plane4.moving(win)
    plane4.draw3(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


# This will hold the code for watching the AI learn
def user_vs_AI(config, plane, plane2, plane3, plane4):
    base = Base(670)
    rocks = [Rock(700)]

    # Setup the AI plane
    with open('./AIConfigurations/config-best.txt', 'rb') as f:
        c = pickle.load(f)

    # Make the plane that the user will be playing with
    planeAI = AIPlane(200, 350)
    # Create the ANN for the singular AI plane
    net = FeedForwardNetwork.create(c, config)

    # Create the gamescreen and then start a clock so that screen speed is controlled
    win = pygame.display.set_mode((500, 800))
    clock = pygame.time.Clock()

    # Try to load the high score from previous games that were played by the user
    try:
        with open('./HighScoreFiles/highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Make the planeAI move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(30)
        # Moving and jumping of the planeAI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                wait = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()
                wait = False
        base.move()
        draw_window(win, plane, plane2, plane3, plane4, planeAI, rocks, base, 0, high)

    # Keep track of how many rocks have been passed
    score = 0
    # will run until planeAI dies by the rock or the ground
    run = True
    fall = True
    while run:
        clock.tick(30)

        # Moving and jumping of the planeAI
        plane.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()

        # Only add passed rocks
        add_rock = False
        for rock in rocks:
            # Always move that little rocky to the left of the screen
            rock.move_left()
            # If a planeAI pixels touches a rock pixel the planeAI will die
            if rock.collision_occurence(plane) or plane.y + plane.img.get_height() >= 730 or plane.y + plane.img.get_height() < -50:
                run = False
            # We are also checking to make sure that the plane does not touch the ground or the ceiling
            if rock.collision_occurence(planeAI) or planeAI.y + planeAI.image_of_plane.get_height() >= 730 or planeAI.y + planeAI.image_of_plane.get_height() < -50:
                run = False
            # If rock is completely off the screen
            if rock.coordinate_pos + rock.ceiling_rock.get_width() < 0:
                rocks.remove(rock)
            # This will check if the planeAI has passed the rock
            if not rock.finished and rock.coordinate_pos < plane.x:
                rock.finished = True
                add_rock = True

        # For all the rocks that have been passed we need to regenerate new ones
        if add_rock:
            # Signifies in the scoreboard that a rock has been passed
            score += 1
            if score > high:
                high += 1
            rocks.append(Rock(600))

        indexer = 0
        if len(rocks) > 1 and planeAI.x > rocks[0].coordinate_pos + rocks[0].ceiling_rock.get_width():
            indexer = 1

        # Plane will move regardless of what happens
        planeAI.move()

        # The activation function for neat, when above 0.5, should trigger a jump of the plane
        # 0.5 was defined in the config file as the boundary value where a jump should occur
        if net.activate(
                (planeAI.y, abs(planeAI.y - rocks[indexer].length), abs(planeAI.y - rocks[indexer].lower_bound)))[
            0] > 0.5:
            # Activation function passed so jump the plane
            planeAI.jump()

        # This section shows a flaming plane falling to the ground to mimic a realistic environment
        if run == False:
            while fall == True:
                clock.tick(30)
                # Checking to see if the plane has hit the ceiling
                if plane.y + plane.img.get_height() >= 780:
                    fall = False
                # IF below ceiling and above ground run this section
                elif plane.y + plane.img.get_height() < 780:
                    plane.move()
                    i = 0
                    # Show the fire animation gif on the front of the plane
                    win.blit(FIRE_IMGS[i], (plane.x, plane.y))
                    i += 1
                    if i == 4:
                        i = 0
                    pygame.display.update()
                    draw_window(win, plane, plane2, plane3, plane4, planeAI, rocks, base, score, high)
                # If AI is below ceiling and above ground mimic a falling motion
                elif planeAI.y + planeAI.img.get_height() < 780:
                    planeAI.move()
                    i = 0
                    # Show the fire animation gif on the front of the plane
                    win.blit(FIRE_IMGS[i], (planeAI.x, planeAI.y))
                    i += 1
                    if i == 4:
                        i = 0
                    pygame.display.update()
                    draw_window(win, plane, plane2, plane3, plane4, planeAI, rocks, base, score, high)
        base.move()
        draw_window(win, plane, plane2, plane3, plane4, planeAI, rocks, base, score, high)

    # Save the highest score of the session to file for later
    with open('./HighScoreFiles/highscores.dat', 'wb') as file:
        pickle.dump(high, file)


def run(config_path, plane, plane2, plane3 ,plane4):
    # # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    user_vs_AI(config, plane, plane2, plane3, plane4)


def configuration(plane, plane2, plane3, plane4):
    # Finding the file that will hold the neural network and GA configurations
    config_path = "config-single.txt"
    # Run the file that contains the neural network configurations
    run(config_path, plane, plane2, plane3, plane4)


# Option button 1, regular game for the user to play
def option_four(win):
    plane = UserPlane(200, 350)
    plane2 = UserPlane(30, 30)
    plane4 = UserPlane(65, 50)
    plane3 = UserPlane(100, 90)
    plane2.moves = 1
    plane3.moves = 1
    plane4.moves = 0
    
    configuration(plane, plane2, plane3, plane4)

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

    clock = pygame.time.Clock()
    i = 0
    wait = True
    while wait:
        # Make the fire gif animation
        clock.tick(30)
        win.blit(FIRE_IMGS[i], (plane.x, plane.y))
        i += 1
        if i == 4:
            i = 0
        # Updates the window with new visuals every frame
        pygame.display.update()

        # Moving and jumping of the planeAI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                wait = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_four(win)
                        wait = False
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False
                        break
