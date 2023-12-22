"""
Models module for Planetoids

This module contains the model classes for the Planetoids game. Anything that you
interact with on the screen is model: the ship, the bullets, and the planetoids.

We need models for these objects because they contain information beyond the simple
shapes like GImage and GEllipse. In particular, ALL of these classes need a velocity
representing their movement direction and speed (and hence they all need an additional
attribute representing this fact). But for the most part, that is all they need. You
will only need more complex models if you are adding advanced features like scoring.

You are free to add even more models to this module. You may wish to do this when you
add new features to your game, such as power-ups. If you are unsure about whether to
make a new class or not, please ask on Ed Discussions.

Lucas Casas lcc79, Borjan Jovanov bj262
Dec 8, 2022
"""
from consts import *
from game2d import *
from introcs import *
import math

# PRIMARY RULE: Models are not allowed to access anything in any module other than
# consts.py. If you need extra information from Gameplay, then it should be a 
# parameter in your method, and Wave should pass it as a argument when it calls 
# the method.

def degToRad(deg):
    """
    Returns the radian value for the given number of degrees
    
    Parameter deg: The degrees to convert
    Precondition: deg is a float
    """
    return math.pi*deg/180


class Bullet(GEllipse):
    """
    A class representing a bullet from the ship
    
    Bullets are typically just white circles (ellipses). The size of the bullet is 
    determined by constants in consts.py. However, we MUST subclass GEllipse, because 
    we need to add an extra attribute for the velocity of the bullet.
    
    The class Wave will need to look at this velocity, so you will need getters for
    the velocity components. However, it is possible to write this assignment with no 
    setters for the velocities. That is because the velocity is fixed and cannot change 
    once the bolt is fired.
    
    In addition to the getters, you need to write the __init__ method to set the starting
    velocity. This __init__ method will need to call the __init__ from GEllipse as a
    helper. This init will need a parameter to set the direction of the velocity.
    
    You also want to create a method to update the bolt. You update the bolt by adding
    the velocity to the position. While it is okay to add a method to detect collisions
    in this class, you may find it easier to process collisions in wave.py.
    """
    #Attribute _velocity: Stores the velocity of the bullet
    #Invariant: _velocity is a Vector object that does not change once created
    
    def isOut(self):
        """
        Returns: True if bullet has gone too far, False otherwise
        """
        if self.x > GAME_WIDTH + DEAD_ZONE or self.y > GAME_HEIGHT + DEAD_ZONE:
            return True
        return False
    
    def getVelocity(self):
        """ 
        returns the velocity of the Bullet
        """
        return self._velocity
    
    def __init__(self, ship):
        super().__init__(fillcolor=BULLET_COLOR)
        temp = ship.getFacing()*SHIP_RADIUS
        temp2 = Vector(ship.x, ship.y)
        tip = temp + temp2
        self.x = tip.x
        self.y = tip.y
        self.width = BULLET_RADIUS*2
        self.height = BULLET_RADIUS*2
        self._velocity = ship.getFacing()*BULLET_SPEED
    
    def move(self): 
        """ 
        Helper function to move the object, meant to be called every frame. 
        """
        self.x = self._velocity.x +self.x
        self.y = self._velocity.y +self.y


class Ship(GImage):
    """
    A class to represent the game ship.
    
    This ship is represented by an image. The size of the ship is determined by constants 
    in consts.py. However, we MUST subclass GEllipse, because we need to add an extra 
    attribute for the velocity of the ship, as well as the facing vecotr (not the same)
    thing.
    
    The class Wave will need to access these two values, so you will need getters for 
    them. But per the instructions,these values are changed indirectly by applying thrust 
    or turning the ship. That means you won't want setters for these attributes, but you 
    will want methods to apply thrust or turn the ship.
    
    This class needs an __init__ method to set the position and initial facing angle.
    This information is provided by the wave JSON file. Ships should start with a shield
    enabled.
    
    Finally, you want a method to update the ship. When you update the ship, you apply
    the velocity to the position. While it is okay to add a method to detect collisions 
    in this class, you may find it easier to process collisions in wave.py.
    """
    #Attribute _velocity: stores the velocity vector of the ship
    #Invariant: _velocity is a Vector object

    #Attribute _facing: stores the heading of the ship
    #Invariant: _facing is a unit Vector
    
    def getFacing(self):
        """ 
        returns the facing of the Ship
        """
        return self._facing

    def getVelocity(self):
        """ 
        returns the velocity of the Ship
        """
        return self._velocity
    
    def __init__(self, data):
        super().__init__(source=SHIP_IMAGE)
        self.x = data["position"][0]
        self.y = data["position"][1]
        self.angle = data["angle"]
        self.width = SHIP_RADIUS*2
        self.height = SHIP_RADIUS*2

        self._velocity = Vector(0,0)
        rad = degToRad(self.angle)
        self._facing = Vector(math.cos(rad), math.sin(rad))
    
    def addAngle(self, angle):
        """ 
        Helper function which handles changing the _facing of the ship.
        Called when the user presses left or right on frame update
        """ 
        self.angle += angle
        rad = degToRad(self.angle)
        self._facing.x = math.cos(rad)
        self._facing.y = math.sin(rad)

    def move(self, pressed: bool = False): 
        """ 
        Helper function to move the object, meant to be called every frame. 
        Additionally checks for Dead_Zone, handling wrapping if necessary.
        """
        if pressed:
            if self._velocity.length() > SHIP_MAX_SPEED:
                self._velocity = self._velocity.normal() * SHIP_MAX_SPEED
            else:
                impulse = self._facing * SHIP_IMPULSE
                self._velocity = self._velocity + impulse
        self.x = self._velocity.x +self.x
        self.y = self._velocity.y +self.y

        if self.x < -abs(DEAD_ZONE):
            self.x = GAME_WIDTH + DEAD_ZONE
        elif self.x > GAME_WIDTH + DEAD_ZONE:
            self.x = -abs(DEAD_ZONE)
        if self.y < -abs(DEAD_ZONE):
            self.y = GAME_HEIGHT + DEAD_ZONE
        elif self.y > GAME_HEIGHT + DEAD_ZONE:
            self.y = -abs(DEAD_ZONE)


class Asteroid(GImage):
    """
    A class to represent a single asteroid.
    
    Asteroids are typically are represented by images. Asteroids come in three 
    different sizes (SMALL_ASTEROID, MEDIUM_ASTEROID, and LARGE_ASTEROID) that 
    determine the choice of image and asteroid radius. We MUST subclass GImage, because 
    we need extra attributes for both the size and the velocity of the asteroid.
    
    The class Wave will need to look at the size and velocity, so you will need getters 
    for them.  However, it is possible to write this assignment with no setters for 
    either of these. That is because they are fixed and cannot change when the planetoid 
    is created. 
    
    In addition to the getters, you need to write the __init__ method to set the size
    and starting velocity. Note that the SPEED of an asteroid is defined in const.py,
    so the only thing that differs is the velocity direction.
    
    You also want to create a method to update the asteroid. You update the asteroid 
    by adding the velocity to the position. While it is okay to add a method to detect 
    collisions in this class, you may find it easier to process collisions in wave.py.
    """
    #Attribute _size: stores the asteroid size
    #invariant: Must be a string "small", "medium", or "large"

    #Attribute _velocity: stores the velocity vector of the asteroid
    #Invariant: Must be a Vector object
    
    def getSize(self):
        """ 
        returns the size of the Asteroid, either "small", "medium", or "large"
        """
        return self._size

    def getRadius(self):
        """ 
        returns the radius of the Asteroid
        """
        return self.width/2

    def getVelocity(self):
        """ 
        returns the velocity of the Asteroid
        """
        return self._velocity 

    def __init__(self, data):
        super().__init__(source=SHIP_IMAGE)
        self.x = data["position"][0]
        self.y = data["position"][1]
        self._size = data["size"]
        temp = Vector2(data["direction"][0],data["direction"][1])
        if self._size == "small":
            self.width = SMALL_RADIUS*2
            self.height = SMALL_RADIUS*2
            self.source = SMALL_IMAGE
            try:
                self._velocity = temp.normal() * SMALL_SPEED
            except:
                self._velocity = temp * 0
        elif self._size == "medium":
            self.width = MEDIUM_RADIUS*2
            self.height = MEDIUM_RADIUS*2
            self.source = MEDIUM_IMAGE
            try:
                self._velocity = temp.normal() * MEDIUM_SPEED
            except:
                self._velocity = temp * 0
        elif self._size == "large":
            self.width = LARGE_RADIUS*2
            self.height = LARGE_RADIUS*2
            self.source = LARGE_IMAGE
            try:
                self._velocity = temp.normal() * LARGE_SPEED
            except:
                self._velocity = temp * 0

    def move(self): 
        """ 
        Helper function to move the object, meant to be called every frame. 
        Additionally checks for Dead_Zone, handling wrapping if necessary.
        """
        self.x = self._velocity.x +self.x
        self.y = self._velocity.y +self.y

        temp = DEAD_ZONE
        if self._size == "large":
            temp += 20
        if self.x < -abs(temp):
            self.x = GAME_WIDTH + temp
        elif self.x > GAME_WIDTH + temp:
            self.x = -abs(temp)
        if self.y < -abs(temp):
            self.y = GAME_HEIGHT + temp
        elif self.y > GAME_HEIGHT + temp:
            self.y = -abs(temp)
