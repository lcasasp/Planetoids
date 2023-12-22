"""
Subcontroller module for Planetoids

This module contains the subcontroller to manage a single level (or wave) in the 
Planetoids game.  Instances of Wave represent a single level, and should correspond
to a JSON file in the Data directory. Whenever you move to a new level, you are 
expected to make a new instance of the class.

The subcontroller Wave manages the ship, the asteroids, and any bullets on screen. These 
are model objects. Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Ed Discussions and we will answer.

Lucas Casas lcc79, Borjan Jovanov bj262
Dec 8, 2022
"""
from game2d import *
from consts import *
from models import *
import random
import datetime

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Level is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)

class Wave(object):
    """
    This class controls a single level or wave of Planetoids.
    
    This subcontroller has a reference to the ship, asteroids, and any bullets on screen.
    It animates all of these by adding the velocity to the position at each step. It
    checks for collisions between bullets and asteroids or asteroids and the ship 
    (asteroids can safely pass through each other). A bullet collision either breaks
    up or removes a asteroid. A ship collision kills the player. 
    
    The player wins once all asteroids are destroyed.  The player loses if they run out
    of lives. When the wave is complete, you should create a NEW instance of Wave 
    (in Planetoids) if you want to make a new wave of asteroids.
    
    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 25 for an example.  This class will be similar to
    than one in many ways.
    
    All attributes of this class are to be hidden. No attribute should be accessed 
    without going through a getter/setter first. However, just because you have an
    attribute does not mean that you have to have a getter for it. For example, the
    Planetoids app probably never needs to access the attribute for the bullets, so 
    there is no need for a getter there. But at a minimum, you need getters indicating
    whether you one or lost the game.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # THE ATTRIBUTES LISTED ARE SUGGESTIONS ONLY AND CAN BE CHANGED AS YOU SEE FIT
    # Attribute _data: The data from the wave JSON, for reloading 
    # Invariant: _data is a dict loaded from a JSON file
    #
    # Attribute _ship: The player ship to control 
    # Invariant: _ship is a Ship object
    #
    # Attribute _asteroids: the asteroids on screen 
    # Invariant: _asteroids is a list of Asteroid, possibly empty
    #
    # Attribute _bullets: the bullets currently on screen 
    # Invariant: _bullets is a list of Bullet, possibly empty
    #
    # Attribute _lives: the number of lives left 
    # Invariant: _lives is an int >= 0
    #
    # Attribute _firerate: the number of frames until the player can fire again 
    # Invariant: _firerate is an int >= 0
    #
    # Attribute _score: the users current score
    # Invarient: _score is an int >= 0
    
    def resetShip(self):
        """ 
        Creates a new ship object. This helper is called when
        app state continues after a death if lives remain.
        """
        self._ship = Ship(self._data["ship"])
    
    def getLives(self):
        """ 
        returns the remaining lives of the player
        """
        return self._lives
    
    def getScore(self):
        """ 
        returns the current game score
        """
        return self._score
    
    def __init__(self, level):
        self._data = level
        self._ship = Ship(self._data["ship"])
        self._asteroids = []
        for i in range(len(self._data["asteroids"])):
            asteroid = Asteroid(self._data["asteroids"][i])
            self._asteroids.append(asteroid)
        self._bullets = []
        self._firerate = 0
        self._lives = SHIP_LIVES
        self._score = 0
    
    def update(self, input):
        """ 
        updates the Wave object every frame when called to move objects.
        handles user input and checks for collisions and game endings 
        every frame.
        """
        if self._ship is None:
            return
        if self._firerate > 0:
            self._firerate -= 1
        if input.is_key_down('left'):
            self._ship.addAngle(SHIP_TURN_RATE)
        if input.is_key_down('right'):
            self._ship.addAngle(-abs(SHIP_TURN_RATE))
        if input.is_key_down('up'):
            self._ship.move(True)
        else:
            self._ship.move(False)
        for i in self._asteroids:
            i.move()
        
        if input.is_key_down('spacebar'):
            if self._firerate == 0:
                newbullet = Bullet(self._ship)
                self._bullets.append(newbullet)
                self._firerate = BULLET_RATE
        
        for i in self._bullets:
            i.move()
        i = 0
        while i < len(self._bullets):
            if self._bullets[i].isOut():
                del self._bullets[i]
            else:
                i += 1

        self.checkBulletCollision()
        self.checkShipCollision()
        self.endCheck()
        self.pauseCheck()
    
    def draw(self, view):
        """ 
        Draws the wave objects to view
        """
        if self._ship is None:
            return
        self._ship.draw(view)
        for i in self._asteroids:
            i.draw(view)
        for i in self._bullets:
            i.draw(view)
    
    def checkShipCollision(self):
        """ 
        Helper function to check if the ship has collided with an asteroid.
        If so, handles image removal and lives.
        """
        shipPoint = Point2(self._ship.x, self._ship.y)
        for i in self._asteroids:
            other = Point2(i.x, i.y)
            distance = shipPoint.distance(other)
            if distance < SHIP_RADIUS + i.getRadius():
                if self._ship.getVelocity().x == 0 and self._ship.getVelocity().y == 0:
                    collision = self._ship.getFacing()
                else:
                    collision = self._ship.getVelocity().normal()
                self.breakUp(shipPoint, collision, i.getSize())
                self._asteroids.remove(i)
                self._ship = None
                self._lives -=1
                return

    def checkBulletCollision(self):
        """ 
        Helper function to check if a bullet has collided with an asteroid.
        If so, deletes both images.
        """
        for i in self._bullets:
            bulletPoint = Point2(i.x, i.y)
            for j in self._asteroids:
                other = Point2(j.x, j.y)
                distance = bulletPoint.distance(other)
                if distance < BULLET_RADIUS + j.getRadius():
                    collision = i.getVelocity().normal()
                    self.breakUp(other, collision, j.getSize())
                    self._asteroids.remove(j)
                    self._bullets.remove(i)
                    return

    def breakUp(self, point, collision, size):
        """ 
        Helper to checkBulletCollision(). handles score and breaking up
        larger asteroids into smaller counterparts.
        """
        if size == "small":
            self._score += 20
            return
        rad = degToRad(120)
        vector1 = Vector2(collision.x*math.cos(rad) - collision.y*math.sin(rad), 
            collision.x*math.sin(rad) + collision.y*math.cos(rad))
        rad = degToRad(240)
        vector2 = Vector2(collision.x*math.cos(rad) - collision.y*math.sin(rad), 
            collision.x*math.sin(rad) + collision.y*math.cos(rad))
        if size == "medium":
            self._score += 10
            a1 = Asteroid({"size": "small", "position": [point.x, point.y], "direction": [collision.x, collision.y]})
            a2 = Asteroid({"size": "small", "position": [point.x, point.y], "direction": [vector1.x, vector1.y]})
            a3 = Asteroid({"size": "small", "position": [point.x, point.y], "direction": [vector2.x, vector2.y]})
            self._asteroids = self._asteroids + [a1, a2, a3]

        if size == "large":
            self._score += 5
            a1 = Asteroid({"size": "medium", "position": [point.x, point.y], "direction": [collision.x, collision.y]})
            a2 = Asteroid({"size": "medium", "position": [point.x, point.y], "direction": [vector1.x, vector1.y]})
            a3 = Asteroid({"size": "medium", "position": [point.x, point.y], "direction": [vector2.x, vector2.y]})
            self._asteroids = self._asteroids + [a1, a2, a3]

    def pauseCheck(self):
        """ 
        Helper for the game to check if the user has died
        """
        if self._ship is None:
            return True
        return False

    def endCheck(self):
        """ 
        Helper for the game to check if the user has died
        and no remaining lives are left, or if all asteroids are destroyed.
        """
        if self._lives == 0 or self._asteroids == []:
            return True
        return False