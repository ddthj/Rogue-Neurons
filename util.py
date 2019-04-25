import math
from objects import Vector3

'''
util.py - collection of math/logic utilities

'''

#some of the boost pads
FULL_BOOST = [Vector3(-3072.0, -4096.0, 73.0), Vector3(3072.0, -4096.0, 73.0), Vector3(-3584.0, 0.0, 73.0), Vector3(3584.0, 0.0, 73.0), Vector3(-3072.0,  4096.0, 73.0), Vector3(3072.0,  4096.0, 73.0)]
SMALL_BOOST = [Vector3(0.0,  2816.0, 70.0),Vector3(0.0,  1024.0, 70.0),Vector3(0.0, -1024.0, 70.0),Vector3(0.0, -2816.0, 70.0)]

def cap(x, low, high):#caps/clams a value between a min and max
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def retarget_boost(agent,target): #adjusts our target so that we may pick up boost along the way provided it isn't much of a deviation
    vector = (target - agent.me.location).normalize()
    best_large = FULL_BOOST[0]
    best_small = SMALL_BOOST[0]
    need = (100 - agent.me.boost) ** 1.5
    for item in FULL_BOOST:
        me_to_pad = (agent.me.location-item).magnitude()
        pad_to_target = (item - target).magnitude()
        me_to_target = (target-agent.me.location).magnitude()
        if me_to_pad + pad_to_target < me_to_target + need and me_to_pad + 200 < me_to_target:
            agent.renderer.begin_rendering("boost")
            agent.renderer.draw_rect_3d(item, 10,10,True, agent.renderer.create_color(255,0,0,255))
            agent.renderer.end_rendering()
            return item,True
        
    need = (100 - agent.me.boost) ** 1.2
    for item in SMALL_BOOST:
        me_to_pad = (agent.me.location-item).magnitude()
        pad_to_target = (item - target).magnitude()
        me_to_target = (target-agent.me.location).magnitude()
        if me_to_pad + pad_to_target < me_to_target + need and me_to_pad + 200 < me_to_target:
            agent.renderer.begin_rendering("boost")
            agent.renderer.draw_rect_3d(item, 10,10,True, agent.renderer.create_color(255,0,0,255))
            agent.renderer.end_rendering()
            return item,True
    return target,False

def defaultPD(agent, local, angle = False): #A bunch of PD loops trying to point the bot in the right direction (towards a local coordinate)
    up = agent.me.matrix.dot(agent.me.location + Vector3(0,0,100))
    turn = math.atan2(local[1],local[0])
    steer = steerPD(turn,0)
    yaw = steerPD(turn,-agent.me.rvel[2]/5)
    pitch = steerPD(math.atan2(local[2],local[0]),agent.me.rvel[1]/5)
    roll = steerPD(math.atan2(local[1],local[2]),agent.me.rvel[0]/5)
    if angle == False:
        return steer,yaw,pitch,roll
    else:
        return steer,yaw,pitch,roll,turn

def field(point,radius): #determines if a point is withing the field - although this is kinda untested
    point = Vector3(abs(point[0]),abs(point[1]),abs(point[2]))
    if point[0] > 3860 - radius:
        return False
    elif point[1] > 5800 - radius:
        return False
    elif point[0] > 820 - radius and point[1] > 4950 - radius:
        return False
    elif point[0] > 2800 - radius and point[1] > -point[0] + 7750 - radius:
        return False
    return True

def flip(agent,c,local,angle): #times out a dodge maneuver but doesn't handle the recovery
    pitch = -sign(local[0])
    yaw = angle if angle > 0.25 else 0.0
    if not agent.me.airborn:
        c.jump = True
        agent.sinceJump = 0
    if agent.sinceJump <= 0.06:
        c.jump = True
        c.pitch = pitch
    elif agent.sinceJump > 0.06 and agent.sinceJump <= 0.08:
        c.jump = False
        c.pitch = pitch
    elif agent.sinceJump > 0.08 and agent.sinceJump <= 0.13:
        c.jump = True
        c.pitch = pitch
        c.roll = 0
        c.yaw = cap(yaw, -1, 1)
    else:
        c.pitch = cap(agent.me.rvel[0],-1,1)

def future(obj, time): #finds the future position of an object assuming it follow's a projectile's trajectory
    temp = obj.location + (obj.velocity * time)
    temp.data[2] -= (325 * time * time)
    return temp

def quadratic(a,b,c): #quadratic formula
    inside = (b**2) - (4*a*c)
    if inside < 0 or a == 0:
        return 0.01
    else:
        n = ((-b - math.sqrt(inside))/(2*a))
        p = ((-b + math.sqrt(inside))/(2*a))
    if p > n:
        return p
    return n

def radius(v): #returns the turn radius of the bot given the velocity
    return 139.059 + (0.1539 * v) + (0.0001267716565 * v * v)

def side(x): # use:   my_goal = Vector3(0, 5100 * side(agent.team), 0)
    if x <= 0:
        return -1
    return 1

def sign(x, f = True): #returns sign of number
    if x < 0:
        return -1
    elif x == 0 and f == True:
        return 0
    else:
        return 1

def steerPD(angle,rate): # a baby PD controller in its natural habitat. Takes a target angle and the current rotational velocity and produces a controller output
    final = ((35*(angle+rate))**3)/20
    return cap(final,-1,1)

def throttle(target_speed, agent_speed, direction = 1): #P loop for throttle control
    final = ((abs(target_speed) - abs(agent_speed))/100) * direction
    if final > 1.5:
        boost = True
    else:
        boost = False
    if final > 0 and target_speed > 1400:
        final = 1
    return cap(final,-1,1),boost

def location_at_ground_impact(obj,obj_radius): #determines location of an object at the moment it lands on the ground
    time = quadratic(-325, obj.velocity[2], obj.location[2]-obj_radius)
    if time <= 0:
        return obj.location
    return future(obj,time)
    
