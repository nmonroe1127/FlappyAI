import pygame
import neat
import time
import os
import random
import pickle
import pygame.freetype

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

#Got my images from this source
#https://github.com/odedw/elm-plane

# Storing the different states of the plane through images
PLANE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("imgs", "plane1.png")), (65, 65)),
              pygame.transform.scale(pygame.image.load(os.path.join("imgs", "plane2.png")), (65, 65)),
              pygame.transform.scale(pygame.image.load(os.path.join("imgs", "plane3.png")), (65, 65))]

FIRE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("imgs", "fire1.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("imgs", "fire2.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("imgs", "fire3.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("imgs", "fire4.png")), (80, 80))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bottomRock.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "ground.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "background.png")))
TITLE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "title.png")), (300, 150))

STAT_FONT = pygame.font.SysFont("comicsans", 50)
BUTTON_FONT = pygame.font.SysFont('Times New Roman', 15)


class Bird:
    # Holds all of the bird state images
    IMGS = PLANE_IMGS
    # How much bird will tilt
    MAX_ROTATION = 25
    # How many frames the bird will rotate in each spin
    ROT_VEL = 20
    # Speed of which the bird will flap its wings (change states)
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Starting x coordinate of the bird
        self.x = x
        # Starting y coordinate of the bird
        self.y = y
        # Bird is initially looking straight so tilt is 0
        self.tilt = 0
        self.tick_count = 0
        # Bird is not moving at the beginning
        self.vel = 0
        # Same value as y, but needs a separate variable to be held
        self.height = self.y
        # To keep track of which of the image states the bird is on
        self.img_count = 0
        # The initial starting image for a bird looking straight
        self.img = self.IMGS[0]
        # for tracking the spin of bird on start screen
        self.spin_count = 0

    # The animation of a bird "jumping" on the screen
    def jump(self):
        # Negative because the top left of the screen is 0x0 so a negative velocity
        # will go up. Going down would require a positive velocity
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # Every single frame this is called to move the board
    def move(self):
        # A frame has just passed
        self.tick_count += 1
        # displacement in terms of pixels for each frame
        # Using physics equation (tick count is in seconds/time)
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        # Make sure the velocity is not too extreme (terminal velocity physics booyah)
        if d >= 16:
            d = 12
        # Make sure the movement upwards is big enough to be noticeable
        if d < 0:
            d -= 1.8

        self.y = self.y + d

        # IF we are moving upwards OR make sure it doesnt start tilting too early
        if d < 0 or self.y < self.height + 50:
            # Making sure bird doesnt tilt in a bad direction
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # Else if we are going downwards, the bird should be tilted in a downwards direction
        else:
            # Rotates the flappy bird completely 90 degrees so it appears to be nosediving
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # win is the window the bird is being drawn onto
    def draw(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        ###Checking which image in the array needs to be shown based upon current image count
        ##Basically this just simulates a bird flapping its wings
        # First time through it will display the init bird facing straight
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        # When the image count is less than 10 it will show the second image
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        # When the image count is less than 15, it will show the last image
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        # When the image count is less than 20, it will go back to image two
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        # Finally, when it hits 21, it will show the initial image and reset the counter
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # This makes sure that the bird is not flapping when it is going down
        # (birds dont flap wings when they fail, they just die)
        if self.tilt <= -80:
            # Show the image when the bird is just level
            self.img = self.IMGS[1]
            # Keep the counter so that the bird wont skip a frame when it goes back up
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate an image around its center in Pygame (tilt the birdy)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # Not sure how this works entirely, got motivation for it from stack overflow
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        # this is just doing the actually rotating of the image
        win.blit(rotated_image, new_rect.topleft)

    # This will detect if the birdy collides with an object
    # It pretty much convex hulls an image to get every possible pixel collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    # title screen bird spinning
    def draw_spin(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        ###Checking which image in the array needs to be shown based upon current image count
        ##Basically this just simulates a bird flapping its wings
        # First time through it will display the init bird facing straight
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        # When the image count is less than 10 it will show the second image
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        # When the image count is less than 15, it will show the last image
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        # When the image count is less than 20, it will go back to image two
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        # Finally, when it hits 21, it will show the initial image and reset the counter
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # Rotate an image around its center in Pygame (tilt the birdy)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)

        #500, 800
        if self.spin_count < 4:
            self.x += 40
            self.tilt = 0
            self.spin_count += 1
        elif self.spin_count < 17:
            self.y -= 40
            self.tilt = 90
            self.spin_count += 1
        elif self.spin_count < 25:
            self.x -= 40
            self.tilt = -180
            self.spin_count += 1
        elif self.spin_count < 38:
            self.y += 40
            self.tilt = -90
            self.spin_count += 1
        if self.spin_count == 38:
            self.spin_count = -4

        # Not sure how this works entirely, got motivation for it from stack overflow
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        # this is just doing the actually rotating of the image
        win.blit(rotated_image, new_rect.topleft)


class Pipe:
    # Space between two pipes
    GAP = 200
    # Pipes move, not the bird
    VELOCITY = 5

    # Height of pipe is random so not passed in
    def __init__(self, x):
        self.x = x
        self.height = 0

        # This is so that it can be attached to top or bottom of frame and tracked easily
        # Where the top of the pipe will be drawn on the screen
        self.top = 0
        # Where the bottom of the pipe will be drawn on the screen
        self.bottom = 0
        # Image if pipe is attached to top of the screen, needs to be flipped
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        # Image if the pip is attached to bottom of screen
        self.PIPE_BOTTOM = PIPE_IMG

        # If the bird has already passed the pipe
        self.passed = False
        # Will define top, bottom, and length of pipes
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        # Drawing the pipe at a negative location so that there is room for bird to go through
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # Literally just moving it in x direction
    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Registering if the bird pixels collides with any of the pipe pixels
    def collide(self, bird):
        # Get the pixels that define a bird
        bird_mask = bird.get_mask()
        # Get the pixels that define the top pipe
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        # Get the pixels that define the bottom pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Define an offset to find the distance between the bird pixels and top pipe pixels
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        # Define an offset to find the distance between the bird pixels and bottom pipe pixels
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Finds the first point of collision between bottom pipe and offset distance
        # IF there is no overlap, it will return "NONE", otherwise it shows collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        # Finds the first point of collision between top pipe and offset distance
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Check to see if either choice is not NONE
        if t_point or b_point:
            # This is if there is a collision
            return True
        # This is if there is no collision
        return False

#The floor of the game screen
class Base:
    #How fast the floor is moving, will be same as velocity of the PIPES
    VEL = 5
    #The base will need to be rotated so we need to know its width
    WIDTH = BASE_IMG.get_width()
    #This is the literal image of the base being stored for later use
    IMG = BASE_IMG

    #x is changing so cant be defined
    def __init__(self, y):
        self.y = y
        #Making sure we have boundaries tracked to know when it needs to be reset
        self.x1 = 0
        self.x2 = self.WIDTH

    #called every single frame as the screen moves
    def move(self):
        #Both the left x and the right x boundary need to be seen as moving so they can be
        #Tracked. The importance of this comes into play later
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #Pretty much we will have two base images in the game at once.
        #This occurs when the first image leaves to the left of the screen, we will cycle it to the back
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        #This occurs when the second image leaves to the left of the screen, we will cycle it to the back
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        #Above is a repeated cycling so that there is always a base at the bottom of the screen

    def draw(self, win):
        #Drawing the two pipe images side by side to achieve rolling look
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, bird, pipes, base, score, high):
    #.blit() is basically just draw for pygame
    #Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    #Draw the multiple pipes that should be on the screen using PIPE class draw method
    for pipe in pipes:
        pipe.draw(win)
    #Render the high score to the screen that is pulled from a file
    high_score = STAT_FONT.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    #Render the score to the screen
    score = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    #call the method that will draw the ground into the game
    base.draw(win)
    #Calls the helper function to actually draw the birdy
    bird.draw(win)
    #Updates the window with new visuals every frame
    pygame.display.update()


def player_game(bird):
    base = Base(690)
    pipes = [Pipe(700)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    try:
        with open('highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Make the bird move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(30)
        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bird.jump()
                wait = False
        base.move()
        draw_window(win, bird, pipes, base, 0, high)

    # Keep track of how many pipes have been passed
    score = 0
    # will run until birdy dies by the pipe or the ground
    run = True
    while run:
        clock.tick(30)

        # Moving and jumping of the bird
        bird.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bird.jump()

        # Array to hold pipes that have left the screen and need to be removed
        rem = []
        # Only add passed pipes
        add_pipe = False
        for pipe in pipes:
            # If a bird pixels touches a pipe pixel the bird will die
            if pipe.collide(bird):
                run = False
            # If pipe is completely off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                # This will check if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()
        # For all the pipes that have been passed we need to regenerate new ones
        if add_pipe:
            # Signifies in the scoreboard that a pipe has been passed
            score += 1
            if score > high:
                high += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        # If the bird hits the ground
        if bird.y + bird.img.get_height() >= 730:
            run = False

        base.move()
        draw_window(win, bird, pipes, base, score, high)

    # Save the highest score of the session to file for later
    with open('highscores.dat', 'wb') as file:
        pickle.dump(high, file)


#Option button 1, regular game for the user to play
def option_one(win):
    bird = Bird(200, 350)
    player_game(bird)

    restart_game = pygame.Rect(192, 220, 117, 30)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), restart_game)
    # Give the button some text
    restart = BUTTON_FONT.render("Restart Game", 1, (255, 255, 255))
    win.blit(restart, (210, 225))

    back_to_menu = pygame.Rect(192, 320, 117, 30)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), back_to_menu)
    # Give the button some text
    back = BUTTON_FONT.render("Back To Menu", 1, (255, 255, 255))
    win.blit(back, (205, 325))

    clock = pygame.time.Clock()
    i = 0
    wait = True
    while wait:
        # Make the fire gif animation
        clock.tick(30)
        win.blit(FIRE_IMGS[i], (bird.x, bird.y))
        i += 1
        if i == 4:
            i = 0
        # Updates the window with new visuals every frame
        pygame.display.update()

        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        #Whenever just the player is playing
                        option_one(win)
                    elif back_to_menu.collidepoint(event.pos):
                        #Whenever you want to watch the AI learn
                        wait = False


def AI_window(win, bird, pipes, base, score, high):
    #.blit() is basically just draw for pygame
    #Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    #Draw the multiple pipes that should be on the screen using PIPE class draw method
    for pipe in pipes:
        pipe.draw(win)
    #Render the high score to the screen that is pulled from a file
    high_score = STAT_FONT.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    #Render the score to the screen
    score = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    #call the method that will draw the ground into the game
    base.draw(win)
    #Calls the helper function to actually draw the birdy
    bird.draw(win)
    #Updates the window with new visuals every frame
    pygame.display.update()



#This will hold the code for watching the AI learn
def option_two(win):
    bird = Bird(200, 350)
    base = Base(690)
    pipes = [Pipe(700)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    try:
        with open('AI_highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Make the bird move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(30)
        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        base.move()
        AI_window(win, bird, pipes, base, 0, high)

    # Keep track of how many pipes have been passed
    score = 0
    # will run until birdy dies by the pipe or the ground
    run = True
    while run:
        clock.tick(30)
        # Moving and jumping of the bird
        bird.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


        # Array to hold pipes that have left the screen and need to be removed
        rem = []
        # Only add passed pipes
        add_pipe = False
        for pipe in pipes:
            # If a bird pixels touches a pipe pixel the bird will die
            if pipe.collide(bird):
                run = False
            # If pipe is completely off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                # This will check if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()
        # For all the pipes that have been passed we need to regenerate new ones
        if add_pipe:
            # Signifies in the scoreboard that a pipe has been passed
            score += 1
            if score > high:
                high += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        # If the bird hits the ground
        if bird.y + bird.img.get_height() >= 730:
            pass

        base.move()
        AI_window(win, bird, pipes, base, score, high)

    # Save the highest score of the session to file for later
    with open('AI_highscores.dat', 'wb') as file:
        pickle.dump(high, file)

    pygame.quit()
    quit()



#This will hold the code for watching the AI simulate a good run
def option_three(win):
    pass


def menu_window(win, bird, bird2, bird3, bird4, base, start_button1, start_button2, start_button3):
    #.blit() is basically just draw for pygame
    #Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    #call the method that will draw the ground into the game
    base.draw(win)
    #Calls the helper function to actually draw the birdy
    bird.draw_spin(win)
    # Calls the helper function to actually draw the birdy
    bird2.draw_spin(win)
    # Calls the helper function to actually draw the birdy
    bird3.draw_spin(win)
    # Calls the helper function to actually draw the birdy
    bird4.draw_spin(win)
    # Add Title Image to Game
    win.blit(TITLE_IMG, (100, 105))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button1)
    # Give the button some text
    start1 = BUTTON_FONT.render("Play Game", 1, (255, 255, 255))
    win.blit(start1, (217, 290))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button2)
    # Give the button some text
    start2 = BUTTON_FONT.render("Watch AI Play", 1, (255, 255, 255))
    win.blit(start2, (205, 390))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button3)
    # Give the button some text
    start3 = BUTTON_FONT.render("Watch Trained AI", 1, (255, 255, 255))
    win.blit(start3, (197, 490))
    #Updates the window with new visuals every frame
    pygame.display.update()


def main():
    bird = Bird(220, 570)
    bird2 = Bird(220, 50)
    bird3 = Bird(380, 330)
    bird4 = Bird(60, 290)
    bird2.spin_count = 21
    bird3.spin_count = 10
    bird4.spin_count = 31

    base = Base(690)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    start_button1 = pygame.Rect(192, 285, 117, 30)
    start_button2 = pygame.Rect(192, 385, 117, 30)
    start_button3 = pygame.Rect(192, 485, 117, 30)

    #Make the bird move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(15)
        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if start_button1.collidepoint(event.pos):
                        #Whenever just the player is playing
                        option_one(win)
                    elif start_button2.collidepoint(event.pos):
                        #Whenever you want to watch the AI learn
                        option_two(win)
                    elif start_button3.collidepoint(event.pos):
                        #Whenever you want to watch a near perfect version of the AI
                        #option_three(win)
                        pass

        base.move()
        menu_window(win, bird, bird2, bird3, bird4, base, start_button1, start_button2, start_button3)

    pygame.quit()
    quit()


main()



