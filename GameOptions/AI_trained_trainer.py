import pickle
import pygame
import os
import neat
import pygame.freetype

# Importing Objects from files
from neat.nn import FeedForwardNetwork

from Objects.plane import AIPlane
from Objects.rock import Rock
from Objects.base import Base

WIN_WIDTH = 500
WIN_HEIGHT = 800

gen = 0


# This will hold the code for watching the AI learn
def eval_genomes(genomes, config):
    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # plane object that uses that network to play
    nets = []
    planes = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = FeedForwardNetwork.create(genome, config)
        nets.append(net)
        planes.append(AIPlane(230, 350))
        ge.append(genome)

    score = 0

    base = Base(670)
    rocks = [Rock(700)]

    run = True
    while run and len(planes) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        rock_ind = 0
        if len(planes) > 0:
            if len(rocks) > 1 and planes[0].x > rocks[0].x + rocks[0].ROCK_TOP.get_width():  # determine whether to use the first or second
                rock_ind = 1  # rock on the screen for neural network input

        for x, plane in enumerate(planes):  # give each plane a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            plane.move()

            # send plane location, top rock location and bottom rock location and determine from network whether to jump or not
            output = nets[planes.index(plane)].activate(
                (plane.y, abs(plane.y - rocks[rock_ind].height), abs(plane.y - rocks[rock_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                plane.jump()

        base.move()

        rem = []
        add_rock = False
        for rock in rocks:
            rock.move()
            # check for collision
            for plane in planes:
                if rock.collide(plane):
                    ge[planes.index(plane)].fitness -= 1
                    nets.pop(planes.index(plane))
                    ge.pop(planes.index(plane))
                    planes.pop(planes.index(plane))

            if rock.x + rock.ROCK_TOP.get_width() < 0:
                rem.append(rock)

            if not rock.passed and rock.x < plane.x:
                rock.passed = True
                add_rock = True

        if add_rock:
            score += 1
            # can add this line to give more reward for passing through a rock (not required)
            for genome in ge:
                genome.fitness += 5
            rocks.append(Rock(600))

        for r in rem:
            rocks.remove(r)

        for plane in planes:
            if plane.y + plane.img.get_height() - 10 >= 690 or plane.y < -50:
                nets.pop(planes.index(plane))
                ge.pop(planes.index(plane))
                planes.pop(planes.index(plane))


        #During training if score reaches 100 go to next generation
        if score == 100:
            break


def run(config_path):
    # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Generate a population
    p = neat.Population(config)

    # This will print to the terminal some progress of the program each generation
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # This will run for however many generations we choose. This case is 50
    winner = p.run(eval_genomes, 50)
    # Dump the best genome to a file
    with open('./AIConfigurations/testing-trainer.txt', 'wb') as file:
        pickle.dump(winner, file)


# Change whatever values you want inside to change up the training.
def configuration(population_size):
    # Finding the file that will hold the neural network and GA configurations
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIConfigurations")
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    # Opening the file so that we can write to it
    config_file = open(config_path, "w+")
    # Setting up values for the neural network
    config_file.write("[NEAT]\n")
    config_file.write("fitness_criterion     = max\n")
    config_file.write("fitness_threshold     = 100000\n")
    config_file.write("pop_size              = " + str(population_size) + "\n")
    config_file.write("reset_on_extinction   = False\n\n")

    # Setting up values for the Default Genome
    config_file.write("[DefaultGenome]\n")
    # Node activation is done first
    config_file.write("activation_default      = tanh\n")
    config_file.write("activation_mutate_rate  = 0.0\n")
    config_file.write("activation_options      = tanh\n")
    # Now Node Aggregation Options
    config_file.write("aggregation_default     = sum\n")
    config_file.write("aggregation_mutate_rate = 0.0\n")
    config_file.write("aggregation_options     = sum\n")
    # Now node bias options
    config_file.write("bias_init_mean          = 0.0\n")
    config_file.write("bias_init_stdev         = 1.0\n")
    config_file.write("bias_max_value          = 30.0\n")
    config_file.write("bias_min_value          = -30.0\n")
    config_file.write("bias_mutate_power       = 0.5\n")
    config_file.write("bias_mutate_rate        = 0.7\n")
    config_file.write("bias_replace_rate       = 0.1\n")
    # Now genome compatibility options
    config_file.write("compatibility_disjoint_coefficient = 1.0\n")
    config_file.write("compatibility_weight_coefficient   = 0.5\n")
    # Connection add/remove rates
    config_file.write("conn_add_prob           = 0.5\n")
    config_file.write("conn_delete_prob        = 0.5\n")
    # Connection enable options
    config_file.write("enabled_default         = True\n")
    config_file.write("enabled_mutate_rate     = 0.01\n")
    config_file.write("feed_forward            = True\n")
    config_file.write("initial_connection      = full\n")
    # Node add/remove rates
    config_file.write("node_add_prob           = 0.2\n")
    config_file.write("node_delete_prob        = 0.2\n")
    # Network Parameters
    config_file.write("num_hidden              = 0\n")
    config_file.write("num_inputs              = 3\n")
    config_file.write("num_outputs             = 1\n")
    # Node Response Options
    config_file.write("response_init_mean      = 1.0\n")
    config_file.write("response_init_stdev     = 0.0\n")
    config_file.write("response_max_value      = 30.0\n")
    config_file.write("response_min_value      = -30.0\n")
    config_file.write("response_mutate_power   = 0.0\n")
    config_file.write("response_mutate_rate    = 0.0\n")
    config_file.write("response_replace_rate   = 0.0\n")
    # Connection Weight Options
    config_file.write("weight_init_mean        = 0.0\n")
    config_file.write("weight_init_stdev       = 1.0\n")
    config_file.write("weight_max_value        = 30\n")
    config_file.write("weight_min_value        = -30\n")
    config_file.write("weight_mutate_power     = 0.5\n")
    config_file.write("weight_mutate_rate      = 0.8\n")
    config_file.write("weight_replace_rate     = 0.1\n\n")

    # Setting up the Default Species Set
    config_file.write("[DefaultSpeciesSet]\n")
    config_file.write("compatibility_threshold = 3.0\n\n")

    # Setting up the Default Stagnation
    config_file.write("[DefaultStagnation]\n")
    config_file.write("species_fitness_func = max\n")
    config_file.write("max_stagnation       = 20\n")
    config_file.write("species_elitism      = 2\n\n")

    # Setting up the Default Reproduction
    config_file.write("[DefaultReproduction]\n")
    config_file.write("elitism            = 2\n")
    config_file.write("survival_threshold = 0.2\n")

    # Close the file now that it has been changed
    config_file.close()

    # Run the file that contains the neural network configurations
    run(config_path)


# Option button 1, regular game for the user to play
def option_two(win):
    #Assume population is of size 15
    configuration(15)

