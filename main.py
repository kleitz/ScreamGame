import pygame
from pygame.locals import *
import os, sys
from environment import *
from player import *
from voiceAmplitude import *
import threading
import queue

i = 0
clock = pygame.time.Clock()
dt = None
displayDebug = False  # variable that controls whether debug info is being displayed


class ScreamGameMain(threading.Thread):
    def __init__(self, width=1856, height=768):
        threading.Thread.__init__(self)
        self.width = width
        self.height = height
        pygame.init()
        # Create the screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.recording = recordingThread()
        self.recording.start()

        self.gameState = 0 # 0 is playing game, 1 is death screen, 2 is win screen
        self.currentLevel = 11 # the level number

    def run(self):
        self.MainLoop()

    def MainLoop(self):
        """ main loop of game """
        self.loadSprites(self.currentLevel)
        global displayDebug
        global dt
        # calibration()
        # allow player to hold down keys for continous input
        pygame.key.set_repeat(50, 100)

        self.background = pygame.image.load('images/clouds.jpg')
        self.background = self.background.convert()

        self.deathScreen = pygame.image.load('images/deathScreen.png')
        self.winScreen = pygame.image.load('images/winScreen.png')

        while 1:
            global i
            dtime_ms = clock.tick(60)  # gets the tick time in milliseconds
            dt = dtime_ms/1000  # converting the tick time to seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.recording.stop()
                    pygame.display.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_F3]:
                        if displayDebug:
                            displayDebug = False
                        else:
                            displayDebug = True
                    if keys[pygame.K_RETURN]:
                        if self.gameState == 1:
                            self.gameState = 0
                            for sprite in self.gameSprites.sprites():
                                sprite.kill()
                            self.loadSprites(self.currentLevel)

            # Checks if character has reached the end of the level
            if pygame.sprite.spritecollideany(self.character, self.levelMark):
                for sprite in self.gameSprites.sprites():
                    sprite.kill()
                if self.currentLevel == 11:
                    self.gameState = 2
                else:
                    self.currentLevel = self.currentLevel+1
                    self.loadSprites(self.currentLevel)

            if self.gameState == 0:
                self.drawGame()
                self.update()
            elif self.gameState == 1:
                self.drawDeathScreen()
            elif self.gameState == 2:
                self.drawWinScreen()

    def update(self):
        global dt

        # Trigger for falling objects
        global i
        deathObject = [death for death in self.triggerElements]
        deathObject.sort(key=lambda death: death.rect.x)

        if not recordingQueue.empty():
            recordingQueue.get()
            if i <= len(deathObject) - 1:
                    deathObject[i].trigger()
                    i += 1

        for sprite in self.gameSprites.sprites():
            pass
            if sprite.rect.top > self.height:
                sprite.kill()

        if not self.character.alive():
            self.gameState = 1

        self.gameSprites.update(dt,self.safeEnviron,self.deathElements)

    def drawGame(self):
        global amp
        self.screen.blit(self.background, (0, 0))
        self.gameSprites.draw(self.screen)

        if amplitudeQueue.empty():
            amp = 0.00
        else:
            amp = amplitudeQueue.get()

        height = -amp*1000
        if height < -80:
            height = -80
        pygame.draw.rect(self.screen, (255, 255, 255), (25, 35, 100, 110))
        pygame.draw.rect(self.screen, (0, 0, 255), (35, 120, 80, height))

        if pygame.font:
            font = pygame.font.Font(None, 24)
            text = font.render("Amplitude", 1, (0, 0, 0))
            textpos = text.get_rect(top=125, centerx=75)
            self.screen.blit(text, textpos)

        if displayDebug:
            if pygame.font:
                font = pygame.font.Font(None, 36)
                text = font.render("Gravity: %s Velocity: %s,%s" %
                                   (self.character.applyGravity,int(self.character.vel.x),int(self.character.vel.y)),1,(0,0,0))
                textpos = text.get_rect(top=100, centerx = self.screen.get_width()/2)
                self.screen.blit(text, textpos)

        pygame.display.flip()

    def drawDeathScreen(self):
        self.screen.blit(self.deathScreen,(0,0))
        pygame.display.flip()

    def drawWinScreen(self):
        self.screen.blit(self.winScreen,(0,0))
        pygame.display.flip()

    def loadSprites(self,level):
        self.lvl = Level("level%d" %(level))
        self.character = Character(self.lvl.playerSpawn)

        self.gameSprites = pygame.sprite.Group(self.character, self.lvl.groundList,
                                               self.lvl.blockList,self.lvl.fallingObjectList,self.lvl.windList,self.lvl.spikesList,self.lvl.levelMark)
        # Sprite Group for environment sprites that won't kill the character
        self.safeEnviron = pygame.sprite.Group(self.lvl.blockList, self.lvl.groundList)
        # Sprite Group for environment sprites that will kill the character
        self.deathElements = pygame.sprite.Group(self.lvl.fallingObjectList,self.lvl.windList,self.lvl.spikesList)

        self.fallingObjects = pygame.sprite.Group(self.lvl.fallingObjectList)

        self.triggerElements = pygame.sprite.Group(self.lvl.fallingObjectList,self.lvl.windList)

        self.levelMark = pygame.sprite.Group(self.lvl.levelMark)

if __name__ == "__main__":
    MainWindow = ScreamGameMain()
    MainWindow.start()
