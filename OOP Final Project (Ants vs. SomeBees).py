#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import keyboard
import pygame
#Make sure that you have the above modules installed before trying to run this program

"""
Some important know-how about a game loop:
1) Getting input from players is known as 'events' in pygame
2) Updating the game based off the player's actions
3) Finally, drawing the game's images on the screen
"""

class AntColony():
    #The colony represents game state information
    #The colony consists of several Places chained together to form a tunnel
    def __init__(self, player_name="", food=6, score=0):
        self.player_name = player_name
        self._score = score
        self._food = food
        
    def remaining_food(self):
        return "\nRemaining food for the colony: " + str(self._food)
    
    def getScore(self):
        return self.getPlayer() + ", your final score for this game is: " + str(self._score)
    
    def setPlayer(self):
        self.player_name = input("Please enter player name: ")
        
    def getPlayer(self):
        return self.player_name
        
    def saveScore(self):
        outfile = open("high_scores.txt", "a")
        print(self.getScore(), file = outfile)
        outfile.close()
        
    def loadScore(self):
        infile = open("high_scores.txt", "r")
        data = infile.readlines()
        record = []
        for i in data:
            temp = int(i.split(" ")[-1][:-1])
            record.append(temp)
            name = i.split(" ")[0]
            for j in reversed(data):
                if temp == max(record):
                    name1 = i.split(" ")[0][:-1]
        if record:
            print("\nThe all-time best for this game was made by " + name1 + " & is: " + str(max(record)))
            print("The previous score for this game made by " + name + " was: " + str(record[-1]))
        infile.close()

class Place():
    #Represents a single place that holds insects and has an exit to another Place
    def __init__(self, name, exit=None):
        self._name = name
        self._entrance = None
        #Tracking entrances will be useful when an Ant needs to see what Bees are in front of it in the tunnel
        self._exit = exit #The Place reached by exiting this Place
        self._ant = None #Currenly set to None because Place is empty, that is to say no ant occupies this Place
        self._bees = [] #List because more than one bee can occupy a single Place
        self.ant_test = False
        
        #If this Place is connected to another one, it means exiting this Place leads to the other
        if self._exit is not None:
            self._exit._entrance = self
            #self._exit._entrance refers to the entrance attribute of exit, exit being another Place
            #If an exit Place is provided, then the new Place (aka, self) is assigned to the entrance attribute of the exit
        
        
    def add_insect(self, insect): #Adds an Insect to this Place
        if isinstance(insect, Ant):
            if self._ant == None: #To check if the Place is empty before moving an ant there
                self._ant = insect
            else:
                self.ant_test = True
                print("\nThere's already an ant deployed at this place!")
        elif isinstance(insect, Bee):
            self._bees.append(insect)
                
        insect._place = self #for when we are adding an object of Insect to this Place via this very method
                
    def remove_insect(self, insect): #Removes an insect from this Place
        if isinstance(insect, Ant):
            if self._ant != None: #Checking if ant is presently occupying this Place
                self._ant = None #Removing ant by setting value of this attribute to None
        elif isinstance(insect, Bee):
            self._bees.remove(insect)
            
        insect._place = None #for when we are removing an object of Insect from this Place via this very method
            
    def getName(self):
        return self._name #Returns name of this Place
    
    def getAnt(self):
        return self._ant
    
    def getBee(self):
        return self._bees
            
    
class Insect():
    #A superclass for Ant and Bee
    def __init__(self, armor, name=None, place=None):
        #Create an insect with an ARMOR amount and a starting PLACE
        self._name = name
        self._armor = armor
        self._place = place #set this attribute using add_insect or remove_insect method of 'Place' class
        #eg. place9.add_insect(insect1)
        
    def reduce_armor(self, damage):
        #reduce armor by the damage taken and remove insect from Place if it has no armor remaining
        self._armor -= damage
        if self._armor <= 0:
            self._place.remove_insect(self)
            
                
    def remaining_armor(self):
        return "The remaining armor for this bee is: " + str(self._armor)
    
    def action(self):
        #This method is meant to be overridden by the action methods of Ant and Bee class
        pass

class Ant(Insect):
    
    food_cost = 0
    blocks_path = True
    
    def __init__(self, armor=1):
        Insect.__init__(self, armor) #Creating an Ant and equipping it with some armor
        
class Bee(Insect):
    #A bee moves from Place to Place, following exits and stinging ants
    
    name = "Bee"
    damage = 1
    
    def sting(self, ant):
        #Attack an ant, reducing its armor by 1
        ant.reduce_armor(self.damage)
        
    def move_to(self, place):
        #Move from the Bee's current Place to a new Place
        self._place.remove_insect(self)
        place.add_insect(self)
        
    def blocked(self):
        #Return True if this bee cannot advance to the next Place
        return (self._place._ant != None) and (self._place._ant.blocks_path)
    
    def action(self):
        #A bee's action stings the ant that blocks its exit
        #Otherwise, it moves to the exit of this current Place
        if self.blocked(): #Ant always blocks path since class variable blocks_path is set to True
            self.sting(self._place._ant)
            print("\n" + self.getName() + " just latched onto your ant deployed at: Place " + self.getExplicitPlace() + "!")
        elif self._armor > 0 and self._place._exit is not None:
            self.move_to(self._place._exit)
            
    def getPlace(self):
        return "\n" + self.getName() + " is currently hovering around Place: " + self._place._name
    
    def getName(self):
        return self._name
    
    def getExplicitPlace(self):
        try:
            return self._place._name
        except:
            return None
        
    
class HarvesterAnt(Ant):
    #A harvester ant will produce 1 additional food per turn for the colony
    
    name = "Harvester"
    food_cost = 2
    implemented = True
    
    #Defining these as class variables, and not inside the constructor, because they will always remain the same
    
    def __init__(self, armor):
        Ant.__init__(self, armor)


    def action(self, colony): #'colony' is an object of class AntColony
        colony._food += 1
        print("\nThis ant just produced +1 food for the colony!")
        
    def subtract_food(self, colony):
        if self.implemented:
            if colony._food>= self.food_cost:
                colony._food -= self.food_cost
        
        
class ThrowerAnt(Ant):
    #A thrower ant throws a leaf each turn at the target Bee
    
    name = "Thrower"
    damage = 1
    food_cost = 3
    implemented = True
    
    
    def __init__(self, armor):
        Ant.__init__(self, armor)

    def action(self, target):
        #Throws a leaf at the target Bee, reducing its armor
        try:
            if target is not None:
                target.reduce_armor(self.damage)
                print("\nYou have catapulted a leaf towards " + target.getName() + "!")
                if target._armor <= 0:
                    print("\nYou have successfully vanquished this pesky bee!")
                    colony._score += 5
        except:
            print("\nTarget bee doesn't exist")
            
    def subtract_food(self, colony):
        if self.implemented:
            if colony._food>= self.food_cost:
                colony._food -= self.food_cost
            
               
class Game():
    def __init__(self):
        pygame.init() #Used to initialize all pygame modules
        #In other words, provides access to all the features of pygame
        pygame.display.set_caption('Ants vs. Bees') #Changing the window title
        self.icon = pygame.image.load("ant_thrower.gif")
        pygame.display.set_icon(self.icon)
        self.colony = pygame.image.load("background.jpg")
        self.colony = pygame.transform.scale(self.colony, (1100,600))
        self.hold = pygame.image.load("doodle.jpg")
        self.hold = pygame.transform.smoothscale(self.hold, (100,100))
        self.charm = pygame.image.load("splash.png")
        self.charm = pygame.transform.smoothscale(self.charm, (1100,600))
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 1100, 600 #Display width and display height variables to determine canvas size
        #In other words, these are canvas dimensions
        self.i = 0 #Setting up a counter
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H)) #Creating our canvas/blank sheet of paper
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H)) #Creating our window
        self.font_name = '8-BIT WONDER.TTF'
        #self.font_name = pygame.font.get_default_font()
        self.BLACK, self.WHITE = (0,0,0), (255,255,255) #RGB (Red, Green, Blue) values for these colors
        self.GREEN, self.FIREBRICK = (0,100,0), (178,34,34)
        self.curr_menu = MainMenu(self) #Game will pass itself as a parameter for the MainMenu class
    
    def game_loop(self):
        while self.playing:
            self.check_events() #To see what the player does while playing the game
            if self.START_KEY:
                self.playing = False
            self.display.fill(self.BLACK) #Resetting our frame
            #self.draw_text("Welcome to Ants vs Bees", 20, self.DISPLAY_W/2, self.DISPLAY_H/2)
            self.display.blit(self.colony, (self.i,0))
            #Adding the second image to the end of the first image
            self.display.blit(self.colony, (self.DISPLAY_W + self.i,0))
            
            if self.i == -self.DISPLAY_W:
                self.display.blit(self.colony, (self.DISPLAY_W + self.i, 0))
                self.i = 0
            self.i -= 0.25 
            #The backgroud image is going to move every 2.5 pixel to the left for every while loop iteration
            
            self.display.blit(self.hold, (100,250))
            self.display.blit(self.hold, (200,250))
            self.display.blit(self.hold, (300,250))
            self.display.blit(self.hold, (400,250))
            self.display.blit(self.hold, (500,250))
            self.display.blit(self.hold, (600,250))
            self.display.blit(self.hold, (700,250))
            self.display.blit(self.hold, (800,250))
            self.display.blit(self.hold, (900,250))

            self.window.blit(self.display, (0,0)) #Aligning our display with our window
            #surfaces need to be blit to the screen in order to be able to display them
            #blitting essentially means copying pixels from one surface to another
            #blit() requires the image itself and then the coordinates for it inside a tuple as its parameters
            pygame.display.update() #Updating our display window to include the changes we've made
            self.reset_keys()
        pygame.quit()
            
    def check_events(self):
        for event in pygame.event.get():
            #Goes through a list of everything a player can do on the computer
            if event.type == pygame.QUIT: #To check if the player hits the exit button at the top of window
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            elif event.type == pygame.KEYDOWN: #The KEYDOWN event shows you which keys were pressed in a particular frame
                if event.key == pygame.K_RETURN: #To check if enter key was pressed
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE: #To check if backspace key was pressed
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN: #To check if down key was pressed
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP: #To check if up key was pressed
                    self.UP_KEY = True
                    
    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        
        
    def draw_text(self, text, size, x, y):
        """
        In pygame, text cannot be written directly to the screen. The steps for working with text are:
        1) Create a font object with the given font size
        2) Render the text into an image with the given color
        3) Blit the image to the screen
        """
        font = pygame.font.Font(self.font_name, size) #Loading up our font
        text_surface = font.render(text, True, self.BLACK)
        """
        The render method will return a Surface object with the text drawn on it.
        The second parameter is a Boolean for whether or not to anti-alias the font.
        Anti-aliasing blurs your text slightly to make it look smoother.
        When we created the Font object, a Rect object was already made for it, so all we need to do now is retrieve it.
        """
        text_rect = text_surface.get_rect() #To retrieve the rectangular area/dimensions of the surface
        text_rect.center = (x,y)
        self.display.blit(text_surface, text_rect) #Putting the text onto our canvas
        
class Menu():
    def __init__(self, game):
        self.obj_game = game
        self.mid_w, self.mid_h = self.obj_game.DISPLAY_W/2, self.obj_game.DISPLAY_H/2
        self.run_display = True #This is what tells our menu to keep running
        self.cursor_rect = pygame.Rect(0,0,20,20) #20x20 square as our cursor
        #In this square, we can place whatever image we want
        self.offset = -100 #Set offset accordingly to keep our cursor towards the left of our text
        
    def draw_cursor(self):
        self.obj_game.draw_text("*", 15, self.cursor_rect.x, self.cursor_rect.y)
        
    def blit_screen(self):
        #Method to blit our menu to the screen
        self.obj_game.window.blit(self.obj_game.display, (0,0))
        pygame.display.update()
        self.obj_game.reset_keys()
        
class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 30
        #Setting coordinates which we will use later to draw our text
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 50
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 70
        #Adding 20 to each of their y-values to move the text boxes down
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty) #Assign a starting position for our cursor
    
    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.obj_game.check_events()
            self.check_input()
            self.obj_game.display.fill(self.obj_game.BLACK)
            self.obj_game.display.blit(self.obj_game.charm, (0,0))
            self.obj_game.draw_text("Main Menu", 20, self.obj_game.DISPLAY_W/2, self.obj_game.DISPLAY_H/2 - 20)
            self.obj_game.draw_text("Start Game", 20, self.startx, self.starty)
            self.obj_game.draw_text("Options", 20, self.optionsx, self.optionsy)
            self.obj_game.draw_text("Credits", 20, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()
            
    def move_cursor(self):
        #Logic to move the cursor
        if self.obj_game.DOWN_KEY:
            if self.state == 'Start': #Check the state
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy) #Adjust the cursor
                self.state = 'Options' #Readjust the state
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.obj_game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
                
    def check_input(self):
        self.move_cursor()
        if self.obj_game.START_KEY:
            if self.state == "Start":
                self.obj_game.playing = True
            elif self.state == "Options":
                pass #Passed for now because we haven't decided what to do once inside this state
            elif self.state == "Credits":
                pass #Passed for now because we haven't decided what to do once inside this state
            self.run_display = False
            

#Driver Code
engine = Game()

while engine.running:
    engine.curr_menu.display_menu()
    engine.game_loop()

#Uncomment the above lines of code to enable graphics

colony = AntColony()
place1 = Place("A")
place2 = Place("B", exit=place1)
place3 = Place("C", exit=place2)
place4 = Place("D", exit=place3)
place5 = Place("E", exit=place4)
place6 = Place("F", exit=place5)
place7 = Place("G", exit=place6)
place8 = Place("H", exit=place7)
place9 = Place("I", exit=place8)
insect = Insect(3)
place9.add_insect(insect)
place = list()
place.extend([place1, place2, place3, place4, place5, place6, place7, place8, place9])
end_places = list()
end_places.extend([place6, place7, place8, place9])
obj_list = list()

def text_menu():
    print("\nWelcome to Ants vs. Bees. This is a tower defense game meant",
         "for those with an eye for strategy. \nPull your defenses together and get ready",
         "to fight the enemy: Bees")
    
    print("\033[4m" + "\033[1m" + "\nINSTRUCTIONS:" + "\033[0m")
    
    print("\u001b[32m" + "\nA game of Ants Vs. SomeBees consists of a series of turns.",
         "In each turn, new bees may enter the ant colony.",
         "\nThen, new ants are placed to defend their colony.",
         "Finally, all insects (ants, then bees) take individual actions.",
         "\nBees either try to move toward the end of the tunnel or sting ants in their way.",
         "\nAnts perform a different action depending on their type, such as collecting more food,",
         "or throwing leaves at the bees.\n",
          "\nOnce you have selected an ant type, you will be asked to deploy it."
          "\nIf you try to deploy your ant at a Place that is already occupied by another ant,"
          "\nyou will lose the turn and your ant will not be deployed."
          "\nRemember, a single Place can only hold one ant but multiple bees can simultaneously exist inside it."
         "\nThe game ends either when a bee reaches the last place in the tunnel: Place A (you lose),",
         "\nor the entire bee fleet has been vanquished (you win)." + "\u001b[0m")
    
    print("\u001b[32m" + "\nThe default health of HarvesterAnts is: 1" + "\u001b[0m")
    print("\u001b[32m" + "The default health of ThrowerAnts is: 2" + "\u001b[0m")
    print("\u001b[32m" + "The default health of Bees is: 3" + "\u001b[0m")
    
    print("\u001b[32m" + "\nThe food cost required to deploy a HarvesterAnt is: 2" + "\u001b[0m")
    print("\u001b[32m" + "The food cost required to deploy a ThrowerAnt is: 3" + "\u001b[0m")
    
    print("\u001b[32m" + "\nRemember you are given 6 crumbs of food at the start of this game! Use them wisely."
          + "\u001b[0m")
    
    print("\u001b[32m" + "\nYou get 5 points for eliminating an enemy bee." + "\u001b[0m")
    print("\u001b[32m" + "Your final score will be displayed at the end of the game." + "\u001b[0m")
    
    print("\u001b[32m" + "\nThe Places in the tunnel are listed as: [A, B, C, D, E, F, G, H, I]" + "\u001b[0m")
    
    print("\u001b[32m" + "\nMay the QueenAnt be with you. Good luck!\n" + "\u001b[0m")
    
    colony.setPlayer()
    while True:
        if not colony.getPlayer():
            print("\u001b[31m" + "You cannot leave this field empty. Please try again!" + "\u001b[0m")
            colony.setPlayer()
        else:
            break
            
    start = input("Press y to start game or n to exit: ")
    while True:
        if start == "y":
            break
        else:
            raise Exception("\nDo come back another time!")

text_menu()

for i in range(1,5):
    obj_list.append(Bee(3, "Bee" + str(i))) #Creating multiple Bee objects here

for i in obj_list:
    select = random.choice(end_places)
    select.add_insect(i)
    


def placement():
    select = input("\nPress 1 to select HarvesterAnt or Press 2 to select ThrowerAnt or Press 3 to skip: ")
    while True:
        if select not in ["1", "2", "3"]:
            print("\u001b[31m" + "You have entered an invalid input. Please try again!" + "\u001b[0m")
            select = input("\nPress 1 to select HarvesterAnt or Press 2 to select ThrowerAnt or Press 3 to skip: ")
        else:
            break
    
    if select == "1":
        global workerant
        workerant = HarvesterAnt(1)
        if colony._food < workerant.food_cost:
            print("\u001b[32m" + "\nYou do not have the resources to call this hardworking ant to action!" + "\u001b[0m")
            #print(colony.remaining_food())
        else:
            name1 = input("\u001b[34m" + "Enter the name of the place where you wish to deploy this HarvesterAnt: "
                         + "\u001b[0m")
            name1 = name1.upper()
            while True:
                if name1 not in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
                    print("\u001b[31m" + "You have entered an invalid input. Please try again!" + "\u001b[0m")
                    name1 = input("\u001b[34m" + "\nEnter the name of the place where you wish to deploy this HarvesterAnt: "
                         + "\u001b[0m")
                    name1 = name1.upper()
                else:
                    break
                    
            if name1 == 'A':
                place1.add_insect(workerant)
                if place1.ant_test == True:
                    #Passing because we don't want food to be deducted if another ant is already deployed at this place
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'B':
                place2.add_insect(workerant)
                if place2.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'C':
                place3.add_insect(workerant)
                if place3.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'D':
                place4.add_insect(workerant)
                if place4.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'E':
                place5.add_insect(workerant)
                if place5.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'F':
                place6.add_insect(workerant)
                if place6.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'G':
                place7.add_insect(workerant)
                if place7.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'H':
                place8.add_insect(workerant)
                if place8.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
            elif name1 == 'I':
                place9.add_insect(workerant)
                if place9.ant_test == True:
                    pass
                else:
                    workerant.subtract_food(colony)
                    
            print(colony.remaining_food())
    elif select == "2":
        global throwerant
        throwerant = ThrowerAnt(2)
        if colony._food < throwerant.food_cost:
            print("\u001b[32m" + "\nYou do not have the resources to call this fearless ant to action!" + "\u001b[0m")
            #print(colony.remaining_food())
        else:
            name2 = input("\u001b[34m" + "Enter the name of the place where you wish to deploy this ThrowerAnt: "
                        + "\u001b[0m")
            name2 = name2.upper()
            while True:
                if name2 not in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
                    print("\u001b[31m" + "You have entered an invalid input. Please try again!" + "\u001b[0m")
                    name2 = input("\u001b[34m" + "Enter the name of the place where you wish to deploy this ThrowerAnt: "
                        + "\u001b[0m")
                    name2 = name2.upper()
                else:
                    break
                    
            if name2 == 'A':
                place1.add_insect(throwerant)
                if place1.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'B':
                place2.add_insect(throwerant)
                if place2.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'C':
                place3.add_insect(throwerant)
                if place3.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'D':
                place4.add_insect(throwerant)
                if place4.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'E':
                place5.add_insect(throwerant)
                if place5.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'F':
                place6.add_insect(throwerant)
                if place6.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'G':
                place7.add_insect(throwerant)
                if place7.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'H':
                place8.add_insect(throwerant)
                if place8.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
            elif name2 == 'I':
                place9.add_insect(throwerant)
                if place9.ant_test == True:
                    pass
                else:
                    throwerant.subtract_food(colony)
                    
            print(colony.remaining_food())
    elif select == "3":
        pass


flag = True
print_flag = True
target1 = obj_list[0]
target2 = obj_list[1]
target3 = obj_list[2]
target4 = obj_list[3]

while flag:
    if print_flag:
        #Using ANSI escape sequences to make text bold and add colors
        try:
            colony.loadScore()
        except:
            pass
        print("\033[1m" + "\nPress the space key to continue!" + "\033[0m")
        print_flag = False
    if keyboard.is_pressed(" "): #Check to see if space key has been pressed
        #Build logic for user interface here
        placement()
        for i in place:
            if isinstance(i._ant, HarvesterAnt):
                workerant.action(colony)
                print(colony.remaining_food())
                
            elif isinstance(i._ant, ThrowerAnt):
                print()
                print("The bees coming to attack you are:")
                for i in obj_list:
                    print(i.getName())
                
                target = input("\u001b[34m" + "\nReady? Aim? Throw leaf at (enter name of bee): " + "\u001b[0m")
                target = target.lower()
                while True:
                    if target not in ["bee1", "bee2", "bee3", "bee4"]:
                        print("\u001b[31m" + "Target bee doesn't exist. Please try again!" + "\u001b[0m")
                        target = input("\u001b[34m" + "\nReady? Aim? Throw leaf at (enter name of bee): " + "\u001b[0m")
                        target = target.lower()
                    else:
                        break
                        
                if target == "bee1":
                    target = target1
                elif target == "bee2":
                    target = target2
                elif target == "bee3":
                    target = target3
                elif target == "bee4":
                    target = target4
                    
                throwerant.action(target)
                print(target.remaining_armor())
                
        if target1._armor > 0:
            target1.action()
            print(target1.getPlace())
        elif target1 not in obj_list:
            pass
        else:
            obj_list.remove(target1)
        if target2._armor > 0:
            target2.action()
            print(target2.getPlace())
        elif target2 not in obj_list:
            pass
        else:
            obj_list.remove(target2)
        if target3._armor > 0:
            target3.action()
            print(target3.getPlace())
        elif target3 not in obj_list:
            pass
        else:
            obj_list.remove(target3)
        if target4._armor > 0:
            target4.action()
            print(target4.getPlace())
        elif target4 not in obj_list:
            pass
        else:
            obj_list.remove(target4)
            
        print("\033[1m" + "\nPress the space key for next turn!" + "\033[0m")
        
        if target1.getExplicitPlace() == "A" or target2.getExplicitPlace() == "A" or target3.getExplicitPlace() == "A" or target4.getExplicitPlace() == "A":
            #Lose condition
            print(colony.getScore())
            colony.saveScore()
            raise Exception("The ant fortress has been penetrated! You have lost the game.")
                
        elif target1._armor <= 0 and target2._armor <=0 and target3._armor <= 0 and target4._armor <= 0:
            #Win condition
            print(colony.getScore())
            colony.saveScore()
            raise Exception("You have successfully thwarted off the enemy attack! You win.")

            
#-------------------------------------------------------------------------------------------------------------------------


# In[ ]:




