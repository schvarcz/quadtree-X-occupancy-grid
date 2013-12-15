# -*- coding:utf8 -*-
import pygame
from pygame.locals import *
from math import ceil, floor, atan2, degrees, radians, sqrt

class Celula(object):
    def __init__(self):
        self.isObstacle = False
        self.isVisited = False
        self.himm = -1

    def addHimm(self):
        self.himm += 3
        if self.himm >=15:
            self.himm = 15

        if self.himm >=10:
            self.isObstacle = True

    def subHimm(self):
        self.himm -= 1
        if self.himm <=0:
            self.himm = 0
        if self.himm < 10:
            self.isObstacle = False

class Mapa(object):
    scale = 1.0
    center = (0,0)

    def __init__(self,w=2000,h=2000,celXSize=100,celYSize=100):
        self.cellXSize = celXSize
        self.cellYSize = celYSize
        self.width = w
        self.height = h
        self.boundingBox = ((w/2,h/2),(w/2,h/2))
        self.map = [[Celula() for colunas in xrange(self.width)] for linhas in xrange(self.height)]

    def putObstaculo(self,x,y):
        x,y = self.worldToMap(x,y)
        self.map[y][x].isObstacle = True
        self.boundingBox = ((min(self.boundingBox[0][0],x), min(self.boundingBox[0][1],y)),
                            (max(self.boundingBox[1][0],x), max(self.boundingBox[1][1],y)))


    def putObstaculoSweep(self,roboPos,leituras):
        x,y = self.worldToMap(roboPos[0],roboPos[1])
        pad = 5500./self.cellXSize

        minx, miny, maxx, maxy = max(x - pad,0), max(y - pad,0), min(x + pad,self.width), min(y + pad,self.height)

        variacao = 100
        for nx in xrange(int(minx),int(maxx)):
            for ny in xrange(int(miny),int(maxy)):

                center = (nx-self.width/2.+0.5)*self.cellXSize, (self.height/2.-ny-0.5)*self.cellYSize
                angle = degrees(atan2(center[1]-roboPos[1],center[0]-roboPos[0])) - roboPos[2]

                angle %= 360
                if angle> 180:
                    angle -= 360

                if -90. <= angle <= 90.:

                    r = leituras[int(90-angle)]
                    r = min(r,5000)

                    d = sqrt(pow(center[1]-roboPos[1],2) + pow(center[0]-roboPos[0],2))

                    if r < 5000 and r-variacao < d < r+variacao:
                        self.map[ny][nx].addHimm()
                        self.map[ny][nx].isVisited = True
                    elif d <= r-variacao:
                        self.map[ny][nx].subHimm()
                        self.map[ny][nx].isVisited = True

        self.boundingBox = ((min(self.boundingBox[0][0],minx),min(self.boundingBox[0][1],miny)),
                            (max(self.boundingBox[1][0],maxx),max(self.boundingBox[1][1],maxy)))

    def worldToMap(self,x,y):
        x /= self.cellXSize
        x += self.width/2.

        y /= self.cellYSize
        y = self.height/2. - y 
        return int(round(x)),int(round(y))
    
    def mapToWorld(self,x,y):
        x -= self.width/2.
        x *= self.cellXSize

        y = self.height/2. - y 
        y *= self.cellYSize
        return x,y

    def draw(self,screen,scale=None,center=None):
        if (scale != None):
            self.scale = scale
        if (center != None):
            self.center = center

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        center = self.worldToMap(self.center[0],self.center[1])

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (max(center[0]-halfWidthMap,0),
                                max(center[1]-halfHeightMap,0),
                                min(center[0]+halfWidthMap,self.width),
                                min(center[1]+halfHeightMap,self.height))


        (bminx,bminy),(bmaxx,bmaxy) = self.boundingBox
        bminx,bminy,bmaxx,bmaxy = max(bminx,minx), max(bminy,miny), min(bmaxx,maxx), min(bmaxy,maxy)
        for x in xrange(int(bminx),int(bmaxx)):
            for y in xrange(int(bminy),int(bmaxy)):
                r = pygame.Rect(floor(sx*(x-minx)), floor(sy*(y-miny)), ceil(sx), ceil(sy))

                if self.map[y][x].isObstacle:
                    pygame.draw.rect(screen,(0,0,0),r,0)
                elif self.map[y][x].isVisited:
                    pygame.draw.rect(screen,(255,255,255),r,0)

        pygame.draw.rect(screen,(255,0,0),
                            pygame.Rect((sx*(bminx-minx),sy*(bminy-miny)), (sx*(bmaxx-bminx),sy*(bmaxy-bminy))),
                            int(1.*self.scale))


    def drawRobot(self,screen,x,y):

        x, y = self.worldToMap(x,y)

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        center = self.worldToMap(self.center[0],self.center[1])

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (max(center[0]-halfWidthMap,0),
                                max(center[1]-halfHeightMap,0),
                                min(center[0]+halfWidthMap,self.width),
                                min(center[1]+halfHeightMap,self.height))

        robot = (int(sx*(x-minx)),int(sy*(y-miny)))

        pygame.draw.circle(screen,(255,0,0),robot,int(1.*self.scale),0)

