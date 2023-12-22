"""
Primary module for Alien Invaders

This module contains the main controller class for the Planetoids application. There
is no need for any any need for additional classes in this module. If you need more
classes, 99% of the time they belong in either the wave module or the models module. If
you are ensure about where a new class should go, post a question on Ed Discussions.

Lucas Casas lcc79, Borjan Jovanov bj262
Dec 8, 2022
"""
from consts import *
from game2d import *
from wave import *
import json

# PRIMARY RULE: Planetoids can only access attributes in wave.py via getters/setters
# Planetoids is NOT allowed to access anything in models.py

class Planetoids(GameApp):
    """
    The primary controller class for the Planetoids application
    
    This class extends GameApp and implements the various methods necessary for processing
    the player inputs and starting/running a game.
        
        Method start begins the application.
        
        Method update either changes the state or updates the Play object
        
        Method draw displays the Play object and any other elements on screen
    
    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class. Any initialization should be done in
    the start method instead. This is only for this class. All other classes
    behave normally.
    
    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.
    
    The primary purpose of this class is managing the game state: when is the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state. For a complete description of how the states work, see the 
    specification for the method update().
    
    As a subclass of GameApp, this class has the following (non-hidden) inherited
    INSTANCE ATTRIBUTES:
    
    Attribute view: the game view, used in drawing (see examples from class)
    Invariant: view is an instance of GView
    
    Attribute input: the user input, used to control the ship and change state
    Invariant: input is an instance of GInput
    
    This attributes are inherited. You do not need to add them. Any other attributes
    that you add should be hidden.
    """
    # Attribute _state: the current state of the game as a value from consts.py
    # Invariant: _state is one of STATE_INACTIVE, STATE_LOADING, STATE_PAUSED, 
    #            STATE_ACTIVE, STATE_CONTINUE
    #
    # Attribute _wave: the subcontroller for a single wave, which manages the game
    # Invariant: _wave is a Wave object, or None if there is no wave currently active.
    #            _wave is only None if _state is STATE_INACTIVE.
    #
    # Attribute _title: the game title
    # Invariant: _title is a GLabel, or None if there is no title to display. It is None 
    #            whenever the _state is not STATE_INACTIVE.
    #
    # Attribute _message: the currently active message
    # Invariant: _message is a GLabel, or None if there is no message to display. It is 
    #            only None if _state is STATE_ACTIVE.
    #
    # Attribute _score: Label to be displayed for the score
    # Invariant: _score is a GLabel only not None when STATE_ACTIVE
    #
    # Attribute _lives: Label to be displayed for the lives
    # Invariant: _lives is a GLabel only not None when STATE_ACTIVE 

    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and creates both 
        the title (in attribute _title) and a message (in attribute _message) saying 
        that the user should press a key to play a game.
        """
        self._title = GLabel(text="Planetoids", font_size=TITLE_SIZE,
            font_name=TITLE_FONT, halign='center')
        self._title.bottom = self.height /2 + TITLE_OFFSET
        self._title.x = self.width/2
        
        self._message = GLabel(text="Press 'S' to Start", font_size=MESSAGE_SIZE,
            font_name=MESSAGE_FONT, halign='center')
        self._message.bottom = self.height /2 + MESSAGE_OFFSET
        self._message.x = self.width/2

        self._state = STATE_INACTIVE
        self._wave = None
        self._score = GLabel(text="0", font_size=MESSAGE_SIZE,
            font_name=MESSAGE_FONT)
        self._score.top = self.height
        self._score.right = self.width
        self._lives = GLabel(text=str(SHIP_LIVES), font_size=MESSAGE_SIZE, 
            font_name=MESSAGE_FONT)
        self._lives.top = self.height
        self._lives.left = 0

    def update(self,dt):
        """
        Animates a single frame in the game.
        
        It is the method that does most of the work. It is NOT in charge of playing the
        game. That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.
        
        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_LOADING,
        STATE_ACTIVE, STATE_PAUSED, and STATE_CONTINUE. Each one of these does its own
        thing, and might even needs its own helper. We describe these below.
        
        STATE_INACTIVE: This is the state when the application first opens. It is a
        paused state, waiting for the player to start the game. It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key. In addition, the application returns to this state
        when the game is over (all lives are lost or all planetoids are destroyed).
        
        STATE_LOADING: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.
        
        STATE_ACTIVE: This is a session of normal gameplay. The player can move the
        ship and fire bullets. All of this should be handled inside of class Wave
        (NOT in this class). Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.
        
        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.
        
        STATE_CONTINUE: This state restores the ship after it was destroyed. The
        application switches to this state if the state was STATE_PAUSED in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.
        
        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """

        if self._state == STATE_INACTIVE and self.input.is_key_down('s'):
            self._state = STATE_LOADING
            self._title = None
            self._message = None

        if self._state == STATE_LOADING:
            dic = self.load_json(DEFAULT_WAVE)
            self._wave = Wave(dic)
            self._state = STATE_ACTIVE

        if self._state == STATE_ACTIVE:
            self._wave.draw(self.view)
            self._wave.update(self.input)
            self._score.text = "Score: " + str(self._wave.getScore())
            self._lives.text = "Lives: " + str(self._wave.getLives())
            if self._wave.pauseCheck():
                self._state = STATE_PAUSED
            if self._wave.endCheck():
                self._state = STATE_COMPLETE
                
        if self._state == STATE_PAUSED:
            self._message = GLabel(text="Press 'S' to Continue", 
                font_size=MESSAGE_SIZE, font_name=MESSAGE_FONT, halign='center')
            self._message.bottom = self.height /2 + MESSAGE_OFFSET
            self._message.x = self.width/2
            if self.input.is_key_down('s'):
                self._message = None
                self._wave.resetShip()
                self._state = STATE_ACTIVE    
        
        if self._state == STATE_COMPLETE:
            self._message = None
            self.endMessage()


    def draw(self):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject. To draw a GObject
        g, simply use the method g.draw(self.view). It is that easy!
        
        Many of the GObjects (such as the ships, planetoids, and bullets) are attributes 
        in Wave. In order to draw them, you either need to add getters for these 
        attributes or you need to add a draw method to class Wave. We suggest the latter. 
        See the example subcontroller.py from class.
        """
        if self._state == STATE_INACTIVE:
            self._message.draw(self.view)
            self._title.draw(self.view)
        if self._state == STATE_PAUSED:
            self._message.draw(self.view)
        if self._state == STATE_ACTIVE:
            self._score.draw(self.view)
            self._lives.draw(self.view)
        if self._state == STATE_COMPLETE:
            self._message.draw(self.view)

    def endMessage(self):
        """ 
        Helper function to determine if win/lose message is to be displayed when game over.
        """
        if self._wave._lives == 0:
            self._message = GLabel(text="You lost!", font_size=TITLE_SIZE,
                font_name=TITLE_FONT, halign='center')
            self._message.bottom = self.height /2 + MESSAGE_OFFSET
            self._message.x = self.width/2
        else:
            self._message = GLabel(text="You Won!", font_size=TITLE_SIZE, 
                font_name=TITLE_FONT, halign='center')
            self._message.bottom = self.height /2 + MESSAGE_OFFSET
            self._message.x = self.width/2