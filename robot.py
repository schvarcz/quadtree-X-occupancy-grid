from math import sin, cos, pi
from mapa import *
from quadtree import *

class RodaSimulacao(object):
    def __init__(self):
        self.baseDados = open("datasets/mapeamento_esparso.txt",'r')
        self.map = Mapa()
        self.quadRoot = Node()
        self.k = None
        self.center = [9300,-6600]
        self.scale = 4.
        self.followRobot = False
        self.pos = [0,0]

        self.map.scale = self.scale
        self.map.center = self.center
        self.quadRoot.scale = self.scale
        self.quadRoot.center = self.center


    def listenControls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return 
            if event.type == pygame.VIDEORESIZE:
                w, h = event.size
                pygame.display.set_mode((w,h),pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                self.k=event.key
            if event.type == pygame.KEYUP:
                self.k = None
            if self.k != None:
                if(self.k == pygame.K_w):
                    self.center[1]+=300
                if(self.k == pygame.K_s):
                    self.center[1]-=300
                if(self.k == pygame.K_d):
                    self.center[0]+=300
                if(self.k == pygame.K_a):
                    self.center[0]-=300
                if(self.k == pygame.K_EQUALS):
                    self.scale+=0.25
                if(self.k == pygame.K_MINUS):
                    self.scale-=0.25
                if(self.k == pygame.K_l):
                    self.followRobot = not self.followRobot
                print "scale: ", self.scale
                print "center: ", self.center

                self.map.scale = self.scale
                self.map.center = self.center
                self.quadRoot.scale = self.scale
                self.quadRoot.center = self.center

       
    def run(self):

        pygame.init()

        pygame.display.set_mode((1024,600),pygame.RESIZABLE)
        pygame.display.update()
        for l in self.baseDados:
            l = l.split(',')
            x,y,th = [float(i) for i in l[:3]]
            leituras = [int(i) for i in l[3:]]
            self.pos = [x,y]
            if self.followRobot:
                self.center = self.pos
                self.map.center = self.pos

#            anguloLeitura = 180
#            for leitura in leituras:
#                if(leitura <= 5000):
#                    angle = anguloLeitura+th-90
#                    rad = angle*pi/180.
#                    lx, ly = x+cos(rad)*leitura, y+sin(rad)*leitura
#                    self.quadRoot.putObstaculo((lx,ly))
#                    self.map.putObstaculo(lx,ly)
#                anguloLeitura -= 1

#            if leituras != []:
#                self.map.putObstaculo2((x,y,th),leituras)
            if leituras != []:
                self.quadRoot.putObstaculo2((x,y,th),leituras)
            self.listenControls()
            screen = pygame.display.get_surface()
            screen.fill((204,204,204))
            self.quadRoot.draw(screen)
            self.quadRoot.drawRobot(screen,x,y,th,leituras)
            #self.map.draw(screen)
            #self.map.drawRobot(screen,x,y)
            pygame.display.update()
            pygame.time.wait(33)
        
        while(True):
            self.listenControls()
            screen = pygame.display.get_surface()
            screen.fill((204,204,204))
            #self.map.draw(screen)
            self.quadRoot.draw(screen)
            pygame.display.update()

if __name__ == "__main__":
    r = RodaSimulacao()
    r.run()
