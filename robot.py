from math import sin, cos, pi
from mapa import *
from quadtree import *
from matplotlib import pyplot as plt

#Mode
QUAD = 0
GRID = 1

quadLen = []
mapLen = []
shot = 1
class RodaSimulacao(object):
    def __init__(self):
        self.baseDados = open("datasets/mapeamento_esparso.txt",'r')
        self.map = Mapa()
        self.quadRoot = Quadtree()
        self.k = None
        self.center = [9300,-6600]
        self.scale = 4.
        self.followRobot = False
        self.pos = [0,0]

        self.map.scale = self.scale
        self.map.center = self.center
        self.quadRoot.scale = self.scale
        self.quadRoot.center = self.center
        self.goal = self.start = None

        self.mode = GRID
        self.interative = True
        self.sweepArea = True


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
                if self.k == pygame.K_UP:
                    self.center[1]+=300
                if self.k == pygame.K_DOWN:
                    self.center[1]-=300
                if self.k == pygame.K_RIGHT:
                    self.center[0]+=300
                if self.k == pygame.K_LEFT:
                    self.center[0]-=300
                if self.k == pygame.K_EQUALS:
                    self.scale+=0.25
                if self.k == pygame.K_MINUS:
                    self.scale-=0.25
                if self.k == pygame.K_l:
                    self.followRobot = not self.followRobot
                if self.k == pygame.K_s:
                    self.mode += 1
                    self.mode %= 2
                    if self.start != None:
                        if self.mode == QUAD:
                            self.quadRoot.pathPlannig(pygame.display.get_surface(),self.start,self.goal)
                        if self.mode == GRID:
                            self.map.pathPlannig(pygame.display.get_surface(),self.start,self.goal)
                if self.k == pygame.K_q:
                    self.quadRoot.mode += 1
                    self.quadRoot.mode %= 2
                if self.k == pygame.K_i:
                    self.interative = not self.interative
                if self.k == pygame.K_a:
                    global shot
                    pygame.image.save(pygame.display.get_surface(),"screenshot_{0}.png".format(shot))
                    shot += 1
                print "scale: ", self.scale
                print "center: ", self.center

                self.map.scale = self.scale
                self.map.center = self.center
                self.quadRoot.scale = self.scale
                self.quadRoot.center = self.center

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.start == None:
                        self.start = list(pygame.mouse.get_pos())
                    elif self.goal == None:
                        self.goal = list(pygame.mouse.get_pos())
                    else:
                        self.goal = self.start = None

                    if self.mode == QUAD:
                        self.quadRoot.pathPlannig(pygame.display.get_surface(),self.start,self.goal)
                    if self.mode == GRID:
                        self.map.pathPlannig(pygame.display.get_surface(),self.start,self.goal)
                if event.button == 3:
                    self.goal = self.start = None



    def run(self):

        pygame.init()

        pygame.display.set_mode((700,700),pygame.RESIZABLE)
        pygame.display.update()
        plt.ion()
        f = plt.figure()
        for l in self.baseDados:
            l = l.split(',')
            x,y,th = [float(i) for i in l[:3]]
            leituras = [int(i) for i in l[3:]]
            self.pos = [x,y]
            if self.followRobot:
                self.center = self.pos
                self.map.center = self.pos
                self.quadRoot.center = self.pos

            if self.sweepArea:
                if leituras != []:
                    self.map.putObstaculoSweep((x,y,th),leituras)
                    self.quadRoot.putObstaculoSweep((x,y,th),leituras)
            else:
                anguloLeitura = 180
                for leitura in leituras:
                    if(leitura <= 5000):
                        angle = anguloLeitura+th-90
                        rad = angle*pi/180.
                        lx, ly = x+cos(rad)*leitura, y+sin(rad)*leitura
                        self.quadRoot.putObstaculo((lx,ly))
                        self.map.putObstaculo(lx,ly)
                    anguloLeitura -= 1

            quadLen.append(len(self.quadRoot))
            mapLen.append(len(self.map))

            ##################
            #  Show Results  #
            ##################
            if self.interative:
                self.listenControls()
                screen = pygame.display.get_surface()
                screen.fill((204,204,204))
                if self.mode == QUAD:
                    self.quadRoot.draw(screen)
                    self.quadRoot.drawRobot(screen,x,y,th,leituras)
                if self.mode == GRID:
                    self.map.draw(screen)
                    self.map.drawRobot(screen,x,y,th,leituras)
                f.clear()
                plt.plot(quadLen)
                f.axes[0].set_xlim([0,388])
                f.canvas.get_tk_widget().update()
                f.canvas.draw()
                pygame.display.update()
                pygame.time.wait(33)
                global shot
                pygame.image.save(pygame.display.get_surface(),"imgs/screenshot_{0}.png".format(shot))
                shot += 1

        print "Quadtree max: ", max(quadLen)
        print "Quadtree size: ", quadLen[-1]
        print "Map size: ", mapLen[-1]
        f.clear()
        plt.plot(quadLen)
#        plt.plot(mapLen)
        # f.axes[0].set_xlim([0,388])
        f.canvas.draw()

        while(True):
            self.listenControls()
            screen = pygame.display.get_surface()
            screen.fill((204,204,204))
            if self.mode == GRID:
                self.map.draw(screen)
                self.map.drawPathPlanning(screen)
            if self.mode == QUAD:
                self.quadRoot.draw(screen)
                self.quadRoot.drawPathPlanning(screen)

            f.canvas.get_tk_widget().update()
            pygame.display.update()

if __name__ == "__main__":
    r = RodaSimulacao()
    r.mode = QUAD
    r.mode = GRID
    r.run()
