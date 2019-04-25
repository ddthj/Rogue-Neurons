import math

'''
objects.py - contains data classes that make my life a lot easier

'''
        
class carObject: #holds most information about the state of the car
    def __init__(self, index, car=None):
        self.location = Vector3(0,0,0)
        self.velocity = Vector3(0,0,0)
        self.matrix = Matrix3([0,0,0])
        self.rvel = [0,0,0]
        self.team = 0
        self.boost= 0
        self.airborn = False
        self.index = index
        if car != None:
            self.update(car)

    def update(self,packet): #updates all vectors without creating new ones - much higher performance
        self.location.data = [packet.physics.location.x,packet.physics.location.y,packet.physics.location.z]
        self.velocity.data = [packet.physics.velocity.x,packet.physics.velocity.y,packet.physics.velocity.z]
        self.matrix = Matrix3( [packet.physics.rotation.pitch,packet.physics.rotation.yaw,packet.physics.rotation.roll])
        self.rvel = self.matrix.dot([packet.physics.angular_velocity.x,packet.physics.angular_velocity.y,packet.physics.angular_velocity.z])
        self.team = packet.team
        self.boost = packet.boost
        self.airborn = not packet.has_wheel_contact

class ballObject: #same as carObject 
    def __init__(self):
        self.location = Vector3(0,0,0)
        self.velocity = Vector3(0,0,0)
        
    def update(self,packet):
        self.location.data = [packet.physics.location.x,packet.physics.location.y,packet.physics.location.z]
        self.velocity.data = [packet.physics.velocity.x,packet.physics.velocity.y,packet.physics.velocity.z]

class Matrix3: #orientation matrix, can be dot'd with a relative distance to convert target from global to local coordinates
    def __init__(self,r):
        CR = math.cos(r[2])
        SR = math.sin(r[2])
        CP = math.cos(r[0])
        SP = math.sin(r[0])
        CY = math.cos(r[1])
        SY = math.sin(r[1])        
        self.data = [Vector3(CP*CY, CP*SY, SP),Vector3(CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR),Vector3(-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR)]

    def dot(self,vector): #dot product
        return Vector3(self.data[0].dot(vector),self.data[1].dot(vector),self.data[2].dot(vector))
    
class Vector3: #A vector class with most of the bells and whistles 
    def __init__(self, *args):
        self.data = args[0] if isinstance(args[0],list) else [x for x in args]
    def __getitem__(self,key):
        return self.data[key]
    def __str__(self):
        return str(self.data)
    def __add__(self,value):
        return Vector3(self[0]+value[0], self[1]+value[1], self[2]+value[2])
    def __sub__(self,value):
        return Vector3(self[0]-value[0],self[1]-value[1],self[2]-value[2])
    def __mul__(self,value):
        return Vector3(self[0]*value, self[1]*value, self[2]*value)
    __rmul__ = __mul__
    def __div__(self,value):
        return Vector3(self[0]/value, self[1]/value, self[2]/value)
    def magnitude(self):
        return math.sqrt((self[0]*self[0]) + (self[1] * self[1]) + (self[2]* self[2]))
    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            return Vector3(self[0]/mag, self[1]/mag, self[2]/mag)
        else:
            return Vector3(0,0,0)
    def dot(self,value):
        return self[0]*value[0] + self[1]*value[1] + self[2]*value[2]
    def cross(self,value):
        return Vector3((self[1]*value[2]) - (self[2]*value[1]),(self[2]*value[0]) - (self[0]*value[2]),(self[0]*value[1]) - (self[1]*value[0]))
    def flatten(self):
        return Vector3(self[0],self[1],0)
    def render(self):
        return [self[0],self[1]]

class Target: #the control() function in states.py accepts these as targets - allows more info about target to get passed around
    def __init__(self,point,velocity=Vector3(0,0,0)):
        self.location = point
        self.velocity = velocity
