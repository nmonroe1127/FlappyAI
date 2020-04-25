import pickle
import pygame
import os
import neat
import pygame.freetype

# Importing Objects from files
from neat.nn import FeedForwardNetwork

from Objects.plane import AIPlane
from Objects.plane import UserPlane
from Objects.rock import Rock
from Objects.base import Base

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))
menu = True

pygame.init()
pygame.font.init()
all_fonts = pygame.font.get_fonts()
font = pygame.font.SysFont(all_fonts[5], 32)

game_window = pygame.display.set_mode((500, 800))
current_generation = 0

userGen = 1
userPop = 2

userChoosing = True
userContinue = True

def ai_window(win, planes, rocks, base, score, high, current_generation, full_size):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    # Draw the multiple rocks that should be on the screen using ROCK class draw method
    for rock in rocks:
        rock.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = font.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (490 - high_score.get_width(), 10))
    # Render the score to the screen
    score = font.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (490 - score.get_width(), 45))
    # Render the generation number to the screen
    score = font.render("Gen: " + str(current_generation), 1, (0, 0, 0))
    win.blit(score, (10, 10))
    # Render the number of plane left alive
    score_label = font.render("Alive: " + str(len(planes)) + "/" + str(full_size), 1, (0, 0, 0))
    win.blit(score_label, (10, 50))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the plane
    for plane in planes:
        plane.draw(win)

    stop = pygame.Rect(10, 85, 90, 27)
    pygame.draw.rect(win, (30, 30, 30), stop)
    back = pygame.font.SysFont('Times New Roman', 19).render("Stop", 1, (255, 255, 255))
    win.blit(back, (37, 87))
    global menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if stop.collidepoint(event.pos):
                    menu = False
                    break

    # Updates the window with new visuals every frame
    pygame.display.update()


# This will hold the code for watching the AI learn
def run_neat(ANN, genotypes, planes_to_add):
    global game_window, current_generation
    current_generation += 1

    # Setup the base and initial single rock on the screen
    base = Base(670)
    rocks = [Rock(700)]
    # Set the user score to default of 0
    score = 0
    # Initialize a clock that will slow down the game speed
    clock = pygame.time.Clock()

    # Array to hold all of the planes in the population set
    planes = []
    # Initialize all the planes that we will need
    for x in range(planes_to_add):
        planes.append(AIPlane(230, 350))

    # Keep track of how many planes total there are
    full_size = planes_to_add

    # Load in the high score from previous users who have played the game
    try:
        with open('./HighScoreFiles/AI_highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Run the program until the entire population of planes has died
    while len(planes) > 0:
        clock.tick(30)
        if not menu:
            break

        for rock in rocks:
            rock.move_left()
            # Check to see if any collisions has occurred between rocks and planes
            for plane in planes:
                if rock.collision_occurence(
                        plane) or plane.y + plane.image_of_plane.get_height() - 10 >= 690 or plane.y < -50:
                    genotypes[planes.index(plane)].fitness -= 1
                    ANN.pop(planes.index(plane))
                    genotypes.pop(planes.index(plane))
                    planes.pop(planes.index(plane))
            # If a rock has left the screen then we can remove it from the array
            if rock.coordinate_pos + rock.ceiling_rock.get_width() < 0:
                rocks.remove(rock)

            # Check to see if we need to add a new rock. Occurs when plane passes one
            if not rock.finished and rock.coordinate_pos < plane.x:
                # This will ensure that only one "rock" is passed each iteration
                rock.finished = True
                # Add on a rock now that one has been passed
                rocks.append(Rock(600))
                # Pipe passed increment the score
                score += 1
                # Give the planes some points for passing a pipe as reward
                for genome in genotypes:
                    genome.fitness += 10

        indexer = 0
        if len(planes) > 0:
            if len(rocks) > 1 and planes[0].x > rocks[0].coordinate_pos + rocks[0].ceiling_rock.get_width():
                indexer = 1

        for x, plane in enumerate(planes):
            # Give each of the planes an award for not immediately suiciding
            genotypes[x].fitness += 0.1
            # Move the planes within each award and every plane
            plane.move()

            # The activation function for neat, when above 0.5, should trigger a jump of the plane
            if ANN[planes.index(plane)].activate(
                (plane.y, abs(plane.y - rocks[indexer].length), abs(plane.y - rocks[indexer].lower_bound)))[0] > 0.5:
                # Activation function passed so jump the plane
                plane.jump()

        base.move()
        # Draw the game window so the user can see what is going on. Blind training would not need this
        ai_window(game_window, planes, rocks, base, score, high, current_generation, full_size)

        # break if score gets large enough
        if score == 20:
            break

    # Save the highest score of the session to file for later
    if high < score:
        with open('./HighScoreFiles/AI_highscores.dat', 'wb') as file:
            pickle.dump(score, file)


def init_neural_network(genomes, config):
    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # plane object that uses that network to play
    # This while hold the Artificial Neural Network
    artificial_neural_network = []
    # This will hold the genotypes of the genetic algorithm
    genotypes = []
    planes_to_add = 0
    # Initialize the Artificial Neural Network
    for _, genome in genomes:
        planes_to_add += 1
        genome.fitness = 0  # start with fitness level of 0
        single_neuron = FeedForwardNetwork.create(genome, config)
        artificial_neural_network.append(single_neuron)
        genotypes.append(genome)

    run_neat(artificial_neural_network, genotypes, planes_to_add)


def run(config_path):
    global current_generation, userGen
    current_generation = 0
    # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Generate a population
    population = neat.Population(config)
    # This will run for however many generations we choose. This case is 50
    population.run(init_neural_network, userGen)


def configuration():
    global userPop
    # Finding the file that will hold the neural network and GA configurations
    config_path = "config-feedforward.txt"
    # Opening the file so that we can write to it
    config_file = open(config_path, "w+")

    # Setting up values for the neural network
    config_file.write("[NEAT]\n")
    # Possible config values for fitness criterion
    # fitness_criterion = 'min'
    # fitness_criterion = 'mean'
    fitness_criterion = 'max'
    # Using max because it seemed to work the best
    config_file.write("fitness_criterion     = " + fitness_criterion + "\n")
    # Fitness threshold determins when the evolutionary process will terminate.
    # I made it a large value because we let the user terminate manually when they want
    fitness_threshold = '100000'
    config_file.write("fitness_threshold     = " + fitness_threshold + "\n")
    # The population size is number of individuals in each generation.
    # I let the user pick this on the menu screen
    pop_size = str(userPop)
    config_file.write("pop_size              = " + pop_size + "\n")
    # Reset on Extinction has two values
    reset_on_extinction = 'False'
    # reset_on_extinction = True
    # I chose false because I dont want new species in a simulated setting such as this
    config_file.write("reset_on_extinction   = " + reset_on_extinction + "\n\n")

    # Setting up values for the Default Genome
    config_file.write("[DefaultGenome]\n")
    # Node activation is done first
    # There is a lot of choices with this one. Found the tanh as a good
    # choice from a textbook resource
    activation_default = 'tanh'
    config_file.write("activation_default      = " + activation_default + "\n")
    # This value is the probability that mutations will replace tanh, we dont
    # Want this to ever happen so we set the value to 0.0. the range possible is [0.0, 1.0]
    activation_mutate_rate = '0.0'
    config_file.write("activation_mutate_rate  = " + activation_mutate_rate + "\n")
    # This value is the list of activation functions that can be used by nodes.
    # Because we set default to tanh we might as well stay consistent across the board
    activation_options = 'tanh'
    config_file.write("activation_options      = " + activation_options + "\n")
    # Now Node Aggregation Options
    # This value is the default aggregation function attribute assigned to new nodes
    # sum seemed to work the best, there were a couple of other options that could be
    # interchanged with this one
    aggregation_default = 'sum'
    config_file.write("aggregation_default     = " + aggregation_default + "\n")
    # This value is the probability that mutation will replace nodes aggregation function
    # Once again we done want replacement to occur to keep simplicity so assign it 0.0
    aggregation_mutate_rate = '0.0'
    config_file.write("aggregation_mutate_rate = " + aggregation_mutate_rate + "\n")
    # This value is the list of aggregation functions that may be used by the nodes
    # Again we want to keep it consistent across the board so sum is used again
    aggregation_options = 'sum'
    config_file.write("aggregation_options     = " + aggregation_options + "\n")
    # Now node bias options
    # This value is the mean of the normal/gaussian distribution.
    # not really sure what that means so set it to 0.0 based upon textbook recs
    bias_init_mean = '0.0'
    config_file.write("bias_init_mean          = " + bias_init_mean + "\n")
    # This value will hold the standard deviation of the normal/gaussian distribution
    # again not really sure so set it to 1.0 based upon textbook recs
    bias_init_stdev = '1.0'
    config_file.write("bias_init_stdev         = " + bias_init_stdev + "\n")
    # This value will hold the maximum that the bias value can obtain
    # again not really sure so set it to 30.0 based upon textbook recs
    bias_max_value = '30.0'
    config_file.write("bias_max_value          = " + bias_max_value + "\n")
    # This value will hold the minimum that the bias value can obtain
    # again not really sure so set it to -30.0 based upon textbook recs
    bias_min_value = '-30.0'
    config_file.write("bias_min_value          = " + bias_min_value + "\n")
    # This value will hold the minimum that the bias value can mutate within power
    # again not really sure so set it to 0.5 based upon textbook recs
    bias_mutate_power = '0.5'
    config_file.write("bias_mutate_power       = " + bias_mutate_power + "\n")
    # This value will hold the minimum that the bias value can mutate
    # again not really sure so set it to 0.7 based upon textbook recs
    bias_mutate_rate = '0.7'
    config_file.write("bias_mutate_rate        = " + bias_mutate_rate + "\n")
    # This value will hold the rate at which bias can be replaced in the system
    # again not really sure so set it to 0.1 based upon textbook recs
    bias_replace_rate = '0.1'
    config_file.write("bias_replace_rate       = " + bias_replace_rate + "\n")
    # Now genome compatibility options
    # This value will hold the coefficient for the disjoint and excess
    # gene counts’ contribution to the genomic distance
    # played around with a couple of values and 1.0 worked the best
    compatibility_disjoint_coefficient = '1.0'
    config_file.write("compatibility_disjoint_coefficient = " + compatibility_disjoint_coefficient + "\n")
    # This value will hold the coefficient for each weight, bias, or response multiplier
    # difference’s contribution to the genomic distance
    # played around with a couple of values and 0.5 worked the best
    compatibility_weight_coefficient = '0.5'
    config_file.write("compatibility_weight_coefficient   = " + compatibility_weight_coefficient + "\n")
    # Connection add/remove rates
    # This value will hold the The probability that mutation will add
    # a connection between existing nodes. Range is [0.0 to 1.0]
    # Tested a couple of values in the range and midline 0.5 seemed to be the best
    conn_add_prob = '0.5'
    config_file.write("conn_add_prob           = " + conn_add_prob + "\n")
    # This value will hold the The probability that mutation will delete an existing connection.
    # Valid values are in [0.0, 1.0].
    # Tested a couple of values in the range and midline 0.5 seemed to be the best
    conn_delete_prob = '0.5'
    config_file.write("conn_delete_prob        = " + conn_delete_prob + "\n")
    # Connection enable options
    # This value will hold the default enabled attribute of newly created connections.
    # Possible values are True and False. Not sure what this means so went with True
    enabled_default = 'True'
    config_file.write("enabled_default         = " + enabled_default + "\n")
    # This value will hold the probability that mutation will replace (50/50 chance of True or False) the
    # enabled status of a connection. Valid values are in [0.0, 1.0].
    # Wasnt sure what to put here so got some guidance from textbook and used 0.01
    enabled_mutate_rate = '0.01'
    config_file.write("enabled_mutate_rate     = " + enabled_mutate_rate + "\n")
    # If this evaluates to True, generated networks will not be allowed to
    # have recurrent connections. Possible values true or false
    # we want the network to have recurrent connections so we assign it to True
    feed_forward = 'True'
    config_file.write("feed_forward            = " + feed_forward + "\n")
    # Specifies the initial connectivity of newly-created genomes
    # We assigned this full because the entire network should be interconnected
    initial_connection = 'full'
    config_file.write("initial_connection      = " + initial_connection + "\n")
    # Node add/remove rates
    # The probability that mutation will add a new node (essentially replacing an existing connection,
    # the enabled status of which will be set to False). Valid values are in [0.0, 1.0].
    # Wasnt sure what to put her so got some guidance from textbook and used 0.2
    node_add_prob = '0.2'
    config_file.write("node_add_prob           = " + node_add_prob + "\n")
    # The probability that mutation will delete an existing node (and all connections to it).
    # Valid values are in [0.0, 1.0].
    # Wasnt sure what to put her so got some guidance from textbook and used 0.2
    node_delete_prob = '0.2'
    config_file.write("node_delete_prob        = " + node_delete_prob + "\n")
    # Network Parameters
    # The number of hidden nodes to add to each genome in the initial population.
    # we dont want any of the nodes to be hidden in this system to we set this to 0
    num_hidden = '0'
    config_file.write("num_hidden              = " + num_hidden + "\n")
    # The number of input nodes, through which the network receives inputs.
    # The flappy plane game will have three inputs, defined in the paper
    num_inputs = '3'
    config_file.write("num_inputs              = " + num_inputs + "\n")
    # The number of output nodes, to which the network delivers outputs.
    # The flappy plane game will have one output, defined in the paper
    num_outputs = '1'
    config_file.write("num_outputs             = " + num_outputs + "\n")
    # Node Response Options (used similar values as made earlier for other section)
    # The mean of the normal/gaussian distribution, if it is used to select
    # response multiplier attribute values for new nodes.
    # Used a nice round value of 1.0
    response_init_mean = '1.0'
    config_file.write("response_init_mean      = " + response_init_mean + "\n")
    # The standard deviation of the normal/gaussian distribution, if it is used
    # to select response multipliers for new nodes.
    response_init_stdev = '0.0'
    config_file.write("response_init_stdev     = " + response_init_stdev + "\n")
    # The maximum allowed response multiplier. Response multipliers above this value
    # will be clamped to this value.
    response_max_value = '30.0'
    config_file.write("response_max_value      = " + response_max_value + "\n")
    # The minimum allowed response multiplier. Response multipliers below this value
    # will be clamped to this value.
    response_min_value = '-30.0'
    config_file.write("response_min_value      = " + response_min_value + "\n")
    # The standard deviation of the zero-centered normal/gaussian distribution from
    # which a response multiplier mutation is drawn.
    response_mutate_power = '0.0'
    config_file.write("response_mutate_power   = " + response_mutate_power + "\n")
    # The probability that mutation will change the response multiplier of a node by
    # adding a random value.
    response_mutate_rate = '0.0'
    config_file.write("response_mutate_rate    = " + response_mutate_rate + "\n")
    # The probability that mutation will replace the response multiplier of a node
    # with a newly chosen random value (as if it were a new node).
    response_replace_rate = '0.0'
    config_file.write("response_replace_rate   = " + response_replace_rate + "\n")
    # Connection Weight Options
    # The mean of the normal/gaussian distribution used to select weight attribute
    # values for new connections.
    weight_init_mean = '0.0'
    config_file.write("weight_init_mean        = " + weight_init_mean + "\n")
    # The standard deviation of the normal/gaussian distribution used to select weight
    # values for new connections.
    weight_init_stdev = '1.0'
    config_file.write("weight_init_stdev       = " + weight_init_stdev + "\n")
    # The maximum allowed weight value. Weights above this value will be clamped to this value.
    weight_max_value = '30.0'
    config_file.write("weight_max_value        = " + weight_max_value + "\n")
    # The minimum allowed weight value. Weights below this value will be clamped to this value.
    weight_min_value = '-30.0'
    config_file.write("weight_min_value        = " + weight_min_value + "\n")
    # The standard deviation of the zero-centered normal/gaussian distribution from which a
    # weight value mutation is drawn.
    weight_mutate_power = '0.5'
    config_file.write("weight_mutate_power     = " + weight_mutate_power + "\n")
    # The probability that mutation will change the weight of a connection by adding a random value.
    weight_mutate_rate = '0.8'
    config_file.write("weight_mutate_rate      = " + weight_mutate_rate + "\n")
    # The probability that mutation will replace the weight of a connection with a newly chosen random
    # value (as if it were a new connection).
    weight_replace_rate = '0.1'
    config_file.write("weight_replace_rate     = " + weight_replace_rate + "\n\n")
    # Setting up the Default Species Set
    config_file.write("[DefaultSpeciesSet]\n")
    compatibility_threshold = '3.0'
    config_file.write("compatibility_threshold = 3.0\n\n")

    # Setting up the Default Stagnation

    config_file.write("[DefaultStagnation]\n")
    # The function used to compute species fitness. This defaults to ``mean``.
    # Allowed values are: max, min, mean, and median
    species_fitness_func = 'max'
    config_file.write("species_fitness_func = " + species_fitness_func + "\n")
    # Species that have not shown improvement in more than this number of generations
    # will be considered stagnant and removed. This defaults to 15.
    max_stagnation = '20'
    config_file.write("max_stagnation       = " + max_stagnation + "\n")
    #The number of species that will be protected from stagnation; mainly intended to prevent
    # total extinctions caused by all species becoming stagnant before new species arise. For
    # example, a species_elitism setting of 3 will prevent the 3 species with the highest species
    # fitness from being removed for stagnation regardless of the amount of time they have not
    # shown improvement. This defaults to 0.
    species_elitism = '2'
    config_file.write("species_elitism      = " + species_elitism + "\n\n")

    # Setting up the Default Reproduction
    config_file.write("[DefaultReproduction]\n")
    # The number of most-fit individuals in each species that will be preserved as-is from one
    # generation to the next. This defaults to 0.
    elitism = '2'
    config_file.write("elitism            = " + elitism + "\n")
    # The fraction for each species allowed to reproduce each generation. This defaults to 0.2.
    survival_threshold = '0.2'
    config_file.write("survival_threshold = " + survival_threshold +"\n")

    # Close the file now that it has been changed
    config_file.close()

    # Run the file that contains the neural network configurations
    run(config_path)


def menu_window(win, plane, plane2, plane3, plane4, base):
    global userGen, userPop, userChoosing, userContinue
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png"))), (0, 0))

    # call the method that will draw the ground into the game
    base.draw(win)

    # Calls the helper function to actually draw the plane
    plane.draw_spin(win)
    plane2.draw_spin(win)
    plane3.draw_spin(win)
    plane4.draw_spin(win)

    # Add Title Image to Game
    win.blit(pygame.transform.scale(pygame.image.load(os.path.join("Images", "title.png")), (300, 150)), (100, 105))

    # Let the user increment the size of population to be used
    increment_pop = pygame.Rect(275, 265, 40, 40)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), increment_pop)
    # Give the button some text
    increment = font.render("+", 1, (255, 255, 255))
    win.blit(increment, (285, 265))

    decrement_pop = pygame.Rect(180, 265, 40, 40)
    pygame.draw.rect(win, (30, 30, 30), decrement_pop)
    decrement = font.render("-", 1, (255, 255, 255))
    win.blit(decrement, (195, 265))

    value = pygame.font.SysFont("Times New Roman", 32).render(str(userPop), 1, (0, 0, 0))
    if userPop < 10:
        win.blit(value, (241, 270))
    elif userPop >= 10:
        win.blit(value, (233, 270))
    title = pygame.font.SysFont('Times New Roman', 20).render("Population Size", 1, (0, 0, 0))
    win.blit(title, (187, 240))

    # Let the user increment the size of generations to be used
    increment_gen = pygame.Rect(275, 345, 40, 40)
    pygame.draw.rect(win, (30, 30, 30), increment_gen)
    increment2 = font.render("+", 1, (255, 255, 255))
    win.blit(increment2, (285, 345))

    decrement_gen = pygame.Rect(180, 345, 40, 40)
    pygame.draw.rect(win, (30, 30, 30), decrement_gen)
    decrement2 = font.render("-", 1, (255, 255, 255))
    win.blit(decrement2, (195, 345))

    value2 = pygame.font.SysFont("Times New Roman", 32).render(str(userGen), 1, (0, 0, 0))
    if userGen < 10:
        win.blit(value2, (241, 350))
    elif userGen >= 10:
        win.blit(value2, (233, 350))
    title2 = pygame.font.SysFont('Times New Roman', 20).render("Generation Size", 1, (0, 0, 0))
    win.blit(title2, (184, 320))


    start_game = pygame.Rect(180, 410, 134, 45)
    pygame.draw.rect(win, (30, 30, 30), start_game)
    start = pygame.font.SysFont('Times New Roman', 18).render("Start Game", 1, (255, 255, 255))
    win.blit(start, (205, 420))

    back_to_menu = pygame.Rect(180, 470, 134, 45)
    pygame.draw.rect(win, (30, 30, 30), back_to_menu)
    back = pygame.font.SysFont('Times New Roman', 18).render("Back To Menu", 1, (255, 255, 255))
    win.blit(back, (193, 480))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            userChoosing = False
            userContinue = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 1 is the left mouse button, 2 is middle, 3 is right.
            if event.button == 1:
                if increment_pop.collidepoint(event.pos):
                    userPop += 1
                elif decrement_pop.collidepoint(event.pos):
                    if userPop > 2:
                        userPop -= 1
                elif increment_gen.collidepoint(event.pos):
                    userGen += 1
                elif decrement_gen.collidepoint(event.pos):
                    if userGen > 1:
                        userGen -= 1
                elif start_game.collidepoint(event.pos):
                    configuration()
                    userContinue = False
                elif back_to_menu.collidepoint(event.pos):
                    userChoosing = False
                    userContinue = False
    # Updates the window with new visuals every frame
    pygame.display.update()


def user_inputs():
    global userGen, userPop, userChoosing, userContinue, game_window
    userGen = 5
    userPop = 10

    plane = UserPlane(220, 570)
    plane2 = UserPlane(220, 50)
    plane3 = UserPlane(380, 330)
    plane4 = UserPlane(60, 290)
    plane.spin_count = 0
    plane2.spin_count = 21
    plane3.spin_count = 10
    plane4.spin_count = 31

    base = Base(670)

    clock = pygame.time.Clock()

    # Make the plane move as it waits for the user to start the game
    userChoosing = True
    userContinue = True
    while userChoosing and userContinue:
        clock.tick(15)
        # Moving and jumping of the plane
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               userChoosing = False
               userContinue = False

        base.move()
        menu_window(game_window, plane, plane2, plane3, plane4, base)


# Option button 1, regular game for the user to play
def option_two(win):
    global menu, userChoosing, userContinue
    menu = True
    # Let user choose what they finnna do
    user_inputs()
    wait = True
    # Configuration(population, generations)
    # configuration(15, 5)
    if userChoosing or userContinue:
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
                            option_two(win)
                            wait = False
                        elif back_to_menu.collidepoint(event.pos):
                            # Whenever you want to watch the AI learn
                            wait = False
                            break

