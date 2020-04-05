import pygame
import os
import time
# Storing the different states of the plane through images
PLANE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane1.png")), (65, 65)),
              pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane2.png")), (65, 65)),
              pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane3.png")), (65, 65))]

PLANE_IMGSSMALL = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane1.png")), (25, 25)),
              pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane2.png")), (25, 25)),
              pygame.transform.scale(pygame.image.load(os.path.join("Images", "plane3.png")), (25, 25))]

PLANE_IMGS2 = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed1.png")), (65, 65)),
               pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed2.png")), (65, 65)),
               pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed3.png")), (65, 65))]

PLANE_IMGSSMALLRED = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed1.png")), (20, 20)),
               pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed2.png")), (20, 20)),
               pygame.transform.scale(pygame.image.load(os.path.join("Images", "planeRed3.png")), (20, 20))]


class AIPlane:
    # Holds all of the plane state images
    IMGS = PLANE_IMGS2
    # How much plane will tilt
    MAX_ROTATION = 25
    # How many frames the plane will rotate in each spin
    ROT_VEL = 20
    # Speed of which the plane will spin its propeller (change states)
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Starting x coordinate of the plane
        self.x = x
        # Starting y coordinate of the plane
        self.y = y
        # plane is initially looking straight so tilt is 0
        self.tilt = 0
        self.tick_count = 0
        # plane is not moving at the beginning
        self.vel = 0
        # Same value as y, but needs a separate variable to be held
        self.height = self.y
        # To keep track of which of the image states the plane is on
        self.img_count = 0
        # The initial starting image for a plane looking straight
        self.img = self.IMGS[0]
        # for tracking the spin of plane on start screen
        self.spin_count = 0

    # The animation of a plane "jumping" on the screen
    def jump(self):
        # Negative because the top left of the screen is 0x0 so a negative velocity
        # will go up. Going down would require a positive velocity
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # Every single frame this is called to move the plane
    def move(self):
        # A frame has just passed
        self.tick_count += 1
        # displacement in terms of pixels for each frame
        # Using physics equation (tick count is in seconds/time)
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        # Make sure the velocity is not too extreme (terminal velocity physics booyah)
        if d >= 16:
            d = 16
        # Make sure the movement upwards is big enough to be noticeable
        if d < 0:
            d -= 2

        self.y = self.y + d

        # IF we are moving upwards OR make sure it doesnt start tilting too early
        if d < 0 or self.y < self.height + 50:
            # Making sure plane doesnt tilt in a bad direction
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # Else if we are going downwards, the plane should be tilted in a downwards direction
        else:
            # Rotates the flappy plane completely 90 degrees so it appears to be nosediving
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # win is the window the plane is being drawn onto
    def draw(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        # Checking which image in the array needs to be shown based upon current image count
        # Basically this just simulates a plane flapping its wings
        # First time through it will display the init plane facing straight
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

        # This makes sure that the plane is not spinning propeller when it is going down
        # (plane propellers dont spin when they fail, they just die)
        if self.tilt <= -80:
            # Show the image when the plane is just level
            self.img = self.IMGS[1]
            # Keep the counter so that the plane wont skip a frame when it goes back up
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate an image around its center in Pygame (tilt the plane)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # Not sure how this works entirely, got motivation for it from stack overflow
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        # this is just doing the actually rotating of the image
        win.blit(rotated_image, new_rect.topleft)

    # This will detect if the plane collides with an object
    # It pretty much convex hulls an image to get every possible pixel collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    # title screen plane spinning
    def draw_spin(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        # Checking which image in the array needs to be shown based upon current image count
        # Basically this just simulates a plane flapping its wings
        # First time through it will display the init plane facing straight
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        # When the image count is less than 10 it will show the second image
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        # When the image count is less than 15, it will show the last image
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
            self.img_count = 0
        # # When the image count is less than 20, it will go back to image two
        # elif self.img_count < self.ANIMATION_TIME * 4:
        #     self.img = self.IMGS[1]
        # # Finally, when it hits 21, it will show the initial image and reset the counter
        # elif self.img_count == self.ANIMATION_TIME * 4 + 1:
        #     self.img = self.IMGS[0]
        #     self.img_count = 0

        # Rotate an image around its center in Pygame (tilt the plane)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)

        # # 500, 800
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


class UserPlane:
    # Holds all of the plane state images
    IMGS = PLANE_IMGS
    IMGSSMALL = PLANE_IMGSSMALL 
    IMGSSMALLRED = PLANE_IMGSSMALLRED
    # How much plane will tilt
    MAX_ROTATION = 25
    # How many frames the plane will rotate in each spin
    ROT_VEL = 20
    # Speed of which the plane will spin its propeller (change states)
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Starting x coordinate of the plane
        self.x = x
        # Starting y coordinate of the plane
        self.y = y
        # plane is initially looking straight so tilt is 0
        self.tilt = 0
        self.tick_count = 0
        # plane is not moving at the beginning
        self.vel = 0
        # Same value as y, but needs a separate variable to be held
        self.height = self.y
        # To keep track of which of the image states the plane is on
        self.img_count = 0
        # The initial starting image for a plane looking straight
        self.img = self.IMGS[0]
        # for tracking the spin of plane on start screen
        self.spin_count = 0

    # The animation of a plane "jumping" on the screen
    def jump(self):
        # Negative because the top left of the screen is 0x0 so a negative velocity
        # will go up. Going down would require a positive velocity
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # Every single frame this is called to move the plane
    def move(self):
        # A frame has just passed
        self.tick_count += 1
        # displacement in terms of pixels for each frame
        # Using physics equation (tick count is in seconds/time)
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        # Make sure the velocity is not too extreme (terminal velocity physics booyah)
        if d >= 16:
            d = 16
        # Make sure the movement upwards is big enough to be noticeable
        if d < 0:
            d -= 2

        self.y = self.y + d

        # IF we are moving upwards OR make sure it doesnt start tilting too early
        if d < 0 or self.y < self.height + 50:
            # Making sure plane doesnt tilt in a bad direction
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # Else if we are going downwards, the plane should be tilted in a downwards direction
        else:
            # Rotates the flappy plane completely 90 degrees so it appears to be nosediving
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw2(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGSSMALL[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGSSMALL[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGSSMALL[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGSSMALL[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGSSMALL[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGSSMALL[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def draw3(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGSSMALLRED[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGSSMALLRED[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGSSMALLRED[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGSSMALLRED[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGSSMALLRED[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGSSMALLRED[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # win is the window the plane is being drawn onto
    def draw(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        # Checking which image in the array needs to be shown based upon current image count
        # Basically this just simulates a plane flapping its wings
        # First time through it will display the init plane facing straight
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

        # Rotate an image around its center in Pygame (tilt the plane)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # Not sure how this works entirely, got motivation for it from stack overflow
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        # this is just doing the actually rotating of the image
        win.blit(rotated_image, new_rect.topleft)

    # This will detect if the plane collides with an object
    # It pretty much convex hulls an image to get every possible pixel collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    # title screen plane spinning
    def draw_spin(self, win):
        # How many times the image has been shown is being tracked
        self.img_count += 1

        # Checking which image in the array needs to be shown based upon current image count
        # Basically this just simulates a plane flapping its wings
        # First time through it will display the init plane facing straight
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        # When the image count is less than 10 it will show the second image
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        # When the image count is less than 15, it will show the last image
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
            self.img_count = 0
        # # When the image count is less than 20, it will go back to image two
        # elif self.img_count < self.ANIMATION_TIME * 4:
        #     self.img = self.IMGS[1]
        # # Finally, when it hits 21, it will show the initial image and reset the counter
        # elif self.img_count == self.ANIMATION_TIME * 4 + 1:
        #     self.img = self.IMGS[0]
        #     self.img_count = 0

        # Rotate an image around its center in Pygame (tilt the plane)
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)

        # # 500, 800
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
