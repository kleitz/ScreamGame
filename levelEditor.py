import pygame
from pygame.locals import *
import os, sys
from environment import *
from player import *

class levelEditorMain():
    def __init__(self, width=1152,height=896):
        self.width = width
        self.height = height
        pygame.init()
        # Create the screen
        self.screen = pygame.display.set_mode((self.width,self.height))

        self.levelName = ""
    def MainLoop(self):
        self.loadSprites()

        self.background = pygame.transform.scale(pygame.image.load('images/clouds.jpg'),(self.width,self.height))
        self.background = self.background.convert()

        while 1:
            self.mousePos = pygame.mouse.get_pos()
            self.boxLeft = int(self.mousePos[0]/64)*64
            self.boxRight = self.boxLeft+64
            self.boxUp = int(self.mousePos[1]/64)*64
            self.boxDown = self.boxUp + 64

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_1]:
                        self.elements.add(GroundBlock(self.boxLeft,self.boxUp))
                    if keys[pygame.K_2]:
                        self.elements.add(Block(self.boxLeft,self.boxUp))
                    if keys[pygame.K_0]:
                        for item in self.elements.sprites():
                            if type(item)==Character:
                                item.kill()
                        self.elements.add(Character(vec(self.boxLeft,self.boxUp)))
                    if keys[pygame.K_s]:
                        self.save()
                    if keys[pygame.K_o]:
                        self.openLevel()

            self.draw()

            pygame.display.update()

    def openLevel(self):
        self.levelName = input("What Level Would You Like To Edit?")
        try:
            editingLevel = Level(self.levelName)
            self.elements.add(editingLevel.allSprites)
            hambo = Character(editingLevel.playerSpawn)
            hambo.pos -= vec(hambo.rect.width/2,hambo.rect.height)
            self.elements.add(Character(editingLevel.playerSpawn))
            print("Level Loaded!")
        except IOError:
            print("Uh Oh Spaghettios That Level Does Not Exist")

    def save(self):
        if self.levelName == "":
            self.levelName = input("Input Level Name: ")
        f = open("levels/%s.txt"%self.levelName,"w+")
        character = []
        blocks = []
        ground = []
        for item in self.elements.sprites():
            if type(item)==Character:
                character.append(item.rect.x - item.rect.width/2)
                character.append(item.rect.y + item.rect.height)
            if type(item)==Block:
                blocks.append([item.rect.x,item.rect.y])
            if type(item)==GroundBlock:
                ground.append([item.rect.x,item.rect.y])

        f.write("Player: %s\nGround: %s\nBlock: %s" %(character,ground,blocks))
        f.close()
        print("Level has been save under %s" %self.levelName)
    def draw(self):
        self.screen.blit(self.background,(0,0))

        self.elements.draw(self.screen)
        # draws grid
        for x in range(0,int(self.width/64)):
            pygame.draw.lines(self.screen,(0,0,0),False,[(x*64,0),(x*64,self.height)],1)
        for y in range(0,int(self.height/64)):
            pygame.draw.lines(self.screen,(0,0,0),False,[(0,y*64),(self.width,y*64)],1)

        pygame.draw.lines(self.screen,(50,205,50),True,[(self.boxLeft,self.boxDown),(self.boxRight,self.boxDown),(self.boxRight,self.boxUp),(self.boxLeft,self.boxUp)],2)
    def loadSprites(self):
        self.elements = pygame.sprite.Group()
if __name__ == "__main__":
    MainWindow = levelEditorMain()
    MainWindow.MainLoop()
