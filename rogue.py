import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import  SimpleControllerState

from objects import *
from states import *
from util import *
from mlp import brain

import pygame
import pickle

"""
Rogue Neurons by GooseFairy/ddthj
Prepared for Professor Stansbury, CS455 and the RLBot community

rogue.py - main file for the bot

"""



def savee(data): #takes any serializable object and writes it into data.dat
    pickle.dump(data, open("data.dat","wb"))
    print("saved")
    
class gui: #the gui used when the bot is creating training data
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('uh',30)
        self.window = pygame.display.set_mode((500,500))
        self.white = (255,255,255)
        self.cur = 2
        
    def update(self,agent): #returns the current state given by the user & updates the window
        self.window.fill(self.white)
        if self.cur == 1:
            msg = "shoot"
        elif self.cur == 2:
            msg = "contest"
        elif self.cur == 3:
            msg = "clear"
        elif self.cur == 4:
            msg = "retreat"
        elif self.cur == 5:
            msg = "recover"
        text = self.font.render(msg, False, (0,0,0))
        self.window.blit(text, (250,250))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.cur = 2
                    return 2 #contest
                elif event.key == pygame.K_w:
                    self.cur = 1
                    return 1 #shoot
                elif event.key == pygame.K_e:
                    self.cur = 3
                    return 3 #clear
                elif event.key == pygame.K_r:
                    self.cur = 4
                    return 4 #retreat
                elif event.key == pygame.K_t:
                    self.cur = 5
                    return 5 #recover
                elif event.key == pygame.K_p:
                    agent.save()
        return self.cur

class rogue(BaseAgent): #the bot
    def initialize_agent(self): #called by the RLBot Framework automatically after it __init__'s

        #objects to hold game information
        self.me = carObject(self.index) 
        self.enemy = carObject(not self.index)
        self.ball = ballObject()
        
        #states of our bot
        self.states = [atba(), shoot(), contest(), clear(), retreat(), recover()]
        self.state = self.states[2]

        #controller that will be returned to the framework
        self.c = SimpleControllerState()

        #Determines what model to use. 0=hardcoded, 1=training mode, 2=play from model
        #Currently configured to play a match with Keras model vs human-made conditional model
        if self.team == 1: 
            self.brain = 2 
        else:
            self.brain = 0

        #inits components as required
        if self.brain == 1:
            self.gui = gui()
        if self.brain == 2:
            self.model = brain()
            
        #keeps track of match time and time since last jump
        self.time = 0
        self.sinceJump = 9.9

        #this is where training data is managed
        self.active = False
        self.sinceSave = 0
        self.trainData = []
        
    def refresh(self): #re-init's our controller to reset all of it's values to defaults
        self.c.__init__()
        return self.c

    def save(self): #saves training data
        savee(self.trainData)

    def check_state(agent):#this is where the selected model chooses which state the bot (agent) will execute

        #the features
        my_time = cap((agent.me.location - agent.ball.location).magnitude() / cap((agent.ball.location - agent.me.location).normalize().dot(agent.me.velocity - agent.ball.velocity), 0.01, 6000),0.01, min(10, (agent.me.location-agent.ball.location).magnitude()/1050))
        enemy_time = cap((agent.enemy.location - agent.ball.location).magnitude() / cap((agent.ball.location - agent.enemy.location).normalize().dot(agent.enemy.velocity - agent.ball.velocity), 0.01, 6000),0.01,min(10, (agent.enemy.location-agent.ball.location).magnitude()/1050))
        my_defense = math.pi - math.acos((agent.ball.location - agent.me.location).normalize().dot((agent.ball.location - Vector3(0,5100*side(agent.team),0)).normalize()))
        enemy_defense = math.pi - math.acos((agent.ball.location - agent.enemy.location).normalize().dot((agent.ball.location - Vector3(0,5100*side(not agent.team),0)).normalize()))
        my_offense = math.pi - math.acos((agent.ball.location - agent.me.location).normalize().dot((Vector3(0,5100*-side(agent.team),0)-agent.ball.location).normalize()))
        enemy_offense = math.pi - math.acos((agent.ball.location - agent.enemy.location).normalize().dot((Vector3(0,5100*-side(not agent.team),0)-agent.ball.location).normalize()))
        ball_ready = True if agent.ball.location[2] < 150 and abs(agent.ball.velocity[2]) < 100 else False

        #conditional model 
        if agent.brain == 0:
            if agent.me.airborn and agent.sinceJump > 1.4:
                agent.state = agent.states[5] #recover
            elif ((my_time + 0.4 <= enemy_time or enemy_offense < 2.0) and my_offense > 0.75) and ball_ready == True:
                agent.state = agent.states[1] #shoot
            elif ((my_time - 1.0 <= enemy_time) or (enemy_offense < 1.57)) and my_offense > 1.57:
                agent.state = agent.states[2] #contest
            elif (my_offense < 1.57 and enemy_offense > 1.0) and abs(agent.ball.location[0]) < 2000:
                agent.state = agent.states[3] #clear
            else:
                agent.state = agent.states[4] #retreat/collect boost
        #training model
        elif agent.brain == 1:
            temp = agent.gui.update(agent)
            agent.state = agent.states[temp]
            if agent.active == True and agent.sinceSave >= 5: #only samples once every 5 frames
                agent.sinceSave = 0
                #all the sample data is divided by its maximum value so that they all land between 0 and 1
                pack = [my_time/10, enemy_time/10, my_defense/3.14, enemy_defense/3.14, my_offense/3.14, enemy_offense/3.14, int(ball_ready),int(agent.me.airborn),temp]
                agent.trainData.append(pack)
        #keras model
        else:
            pack = [my_time/10, enemy_time/10, my_defense/3.14, enemy_defense/3.14, my_offense/3.14, enemy_offense/3.14, int(ball_ready),int(agent.me.airborn)]
            agent.state = agent.states[agent.model.get_state(pack)]
        agent.sinceSave += 1
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState: #called by RLBot Framework every tick
        self.process(packet)
        self.check_state()
        return self.state.execute(self)

    def process(self,packet): #converts packet information into our internal objects for ease-of-use
        self.sinceJump += packet.game_info.seconds_elapsed-self.time
        self.time = packet.game_info.seconds_elapsed
        self.active = packet.game_info.is_round_active or packet.game_info.is_kickoff_pause
        self.ball.update(packet.game_ball)
        self.me.update(packet.game_cars[self.index])
        self.enemy.update(packet.game_cars[not self.index])
