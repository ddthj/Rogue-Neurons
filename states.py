import math
from objects import *
from util import *


'''
states.py - contains every state in the form of classes
plus the controller, which takes state output and converts it to something we can return to the framework

'''

class state: #all states inherit from this
    def __init__(self):
        self.expired = False
    def reset(self):
        self.expired = False
    def execute(self,agent):
        pass

class atba(state): #always towards ball agent
    def __init__(self):
        super().__init__()
    def execute(self,agent):
        #all states produce a target and target speed
        target = agent.ball.location
        speed = 2300
        return control(agent,target,speed)

class shoot(state):#takes shot on opponent goal
    def __init__(self):
        super().__init__()
    def execute(self,agent):
        goal = Vector3(0,5100*-side(agent.team),0)
        distance = (agent.ball.location - agent.me.location).magnitude() / 2.5
        goal_to_ball = (agent.ball.location- goal).normalize()

        target = agent.ball.location + distance * goal_to_ball

        perp = goal_to_ball.cross(Vector3(0,0,1))
        adjustment =  perp * cap(perp.dot(agent.ball.velocity), -distance/2.3, distance/2.3)
        target += adjustment     

        speed = 2300
        if distance > 2050:
            target, retarget = retarget_boost(agent,target) #it's bad to call this at close distances
        return control(agent,Target(target),speed,False)
    
class contest(state): #hits the ball asap, dodges into it.
    def __init__(self):
        super().__init__()
    def execute(self,agent):
        target,retarget = retarget_boost(agent,agent.ball.location)
        speed = 2300
        return control(agent,Target(target, agent.ball.velocity),speed,not retarget)

class clear(state): #hits ball to side of field
    def __init__(self):
        super().__init__()
    def execute(self,agent):
        distance = (agent.me.location - agent.ball.location).flatten().magnitude()

        goal_vector = Vector3(-sign(agent.ball.location[0],False),0,0)

        target = agent.ball.location + (goal_vector*(40+(distance/5)))
        target += Vector3(0,25*side(agent.team),0)
        speed = 2300 * cap(distance / (-180 + agent.ball.location[2]*2), 0.1, 1)
        return control(agent, Target(target), speed, False)

class retreat(state): #returns to goal and stops
    def __init__(self):
        super().__init__()
        
    def execute(self,agent):
        goal = Vector3(0,5100*side(agent.team),70)

        if (agent.me.location - goal).magnitude() < 500:
            speed = 30
            target = agent.ball.location
        else:
            speed = 1800

        target,retarget = retarget_boost(agent,goal)

        return control(agent, Target(target), speed, False)

class recover(state): #tries to land facing in the direction it's moving
    def __init__(self):
        super().__init__()
    def execute(self,agent):
        target = agent.me.location + agent.me.velocity.flatten()
        speed = 30
        return control(agent,Target(target), speed, False)
  
        
def control(agent,target, target_speed, f = False): #turns targets and speeds into controller outputes
    c = agent.refresh()
    local_target = agent.me.matrix.dot(target.location - agent.me.location)
    local_velocity = agent.me.matrix.dot(agent.me.velocity)[0]

    turn_radius = radius(local_velocity)
    turn_center = Vector3(0,sign(local_target[1])*(turn_radius + 70),0)
    slowdown = (turn_center - local_target.flatten()).magnitude() / cap(turn_radius * 1.5, 1, 1200)
    target_speed = cap(target_speed * slowdown, -abs(target_speed),abs(target_speed))
    c.handbrake = True if slowdown < 0.44 else False

    c.steer,c.yaw,c.pitch,c.roll,angle_to_target = defaultPD(agent, local_target, True)
    c.throttle,c.boost = throttle(target_speed, local_velocity, 1)
    if agent.me.airborn and (angle_to_target > 0.2 or (agent.me.location - target.location).magnitude() > 800):
        c.boost = False
    closing_vel = cap((target.location - agent.me.location).normalize().dot(agent.me.velocity-target.velocity),0.01, 2300)
    if agent.sinceJump < 1.5 or  (f == True and (target.location - agent.me.location).magnitude() / closing_vel < 0.38 and abs(angle_to_target) < 0.21):
        flip(agent,c,local_target,angle_to_target)
    return c
    
    
    
