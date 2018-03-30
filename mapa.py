# -*- coding:utf8 -*-
import time
import pygame
from pygame.locals import *
from math import ceil, floor, atan2, degrees, radians, sqrt, cos, sin

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
    start = goal = None
    path = []


    def __init__(self,w=2000,h=2000,celXSize=100,celYSize=100):
        self.cellXSize = celXSize
        self.cellYSize = celYSize
        self.width = w
        self.height = h
        self.boundingBox = ((w/2,h/2),(w/2,h/2))
        self.map = [[Celula() for colunas in xrange(self.width)] for linhas in xrange(self.height)]


    def putObstaculo(self,x,y):
        x,y = self.worldToMap((x,y))
        self.map[y][x].isObstacle = True
        self.boundingBox = ((min(self.boundingBox[0][0],x), min(self.boundingBox[0][1],y)),
                            (max(self.boundingBox[1][0],x), max(self.boundingBox[1][1],y)))


    def putObstaculoSweep(self,roboPos,leituras):
        x,y = self.worldToMap((roboPos[0],roboPos[1]))
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


    def worldToMap(self,pt):
        x, y = pt
        x /= self.cellXSize
        x += self.width/2.

        y /= self.cellYSize
        y = self.height/2. - y
        return int(round(x)),int(round(y))


    def mapToWorld(self,pt):
        x, y = pt
        x -= self.width/2.
        x *= self.cellXSize

        y = self.height/2. - y
        y *= self.cellYSize
        return x,y


    def mapToScreen(self,screen,pt):

        s = screen.get_size()

        x, y = pt
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        center = self.worldToMap(self.center)

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (max(center[0]-halfWidthMap,0),
                                max(center[1]-halfHeightMap,0),
                                min(center[0]+halfWidthMap,self.width),
                                min(center[1]+halfHeightMap,self.height))

        return (int(sx*(x-minx)),int(sy*(y-miny)))


    def screenToMap(self,screen,pt):
        s = screen.get_size()

        x, y = pt
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        center = self.worldToMap(self.center)

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (max(center[0]-halfWidthMap,0),
                                max(center[1]-halfHeightMap,0),
                                min(center[0]+halfWidthMap,self.width),
                                min(center[1]+halfHeightMap,self.height))

        return (int(x/sx + minx),int(y/sy + miny))


    def worldToScreen(self,screen,pt):
        pt = self.worldToMap(pt)
        return self.mapToScreen(screen,pt)

    def screenToWorld(self,screen,pt):
        pt = self.screenToMap(screen,pt)
        return self.mapToWorld(pt)


    def draw(self,screen,scale=None,center=None):
        if (scale != None):
            self.scale = scale
        if (center != None):
            self.center = center

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        center = self.worldToMap(self.center)

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


    def drawRobot(self,screen,x,y,th,leituras):
        robot = (x,y)

        self.drawPoint(screen,self.worldToMap(robot),(255,0,0))

        if leituras != []:
            dLaser = [self.worldToMap(robot)]
            angle = 90+th
            for r in leituras:
                if r > 5000:
                    r = 5000
                dLaser.append(self.worldToMap((
                                x + r*cos(radians(angle)) ,
                                y + r*sin(radians(angle)))))
                angle -= 1

            # pygame.draw.polygon(screen,(0,0,255),dLaser,0)
            self.drawPolygon(screen, dLaser, (0,0,255))


    def drawPathPlanning(self,screen):
        if (self.start != None):
            self.drawPoint(screen,self.start,(0,0,255))
        if (self.goal != None):
            self.drawPoint(screen,self.goal,(255,0,0))

        if self.path != []:
#            print self.path
#            for pt in self.path:
#                self.drawPoint(screen,pt,(0,0,255))
            pts = [self.mapToScreen(screen,pt) for pt in self.path]
            pygame.draw.lines(screen,(0, 0, 255), False,pts,int(1.*self.scale))


    def drawPoint(self,screen,pt,color = (0,255,0), size = 1):
        pt = self.mapToScreen(screen,pt)
        pygame.draw.circle(screen,color,pt,int(size*self.scale),0)

    def drawPolygon(self,screen,polygon,color = (0,255,0), size = 1):
        nPolygon = [self.mapToScreen(screen,pt) for pt in polygon ]
        pygame.draw.polygon(screen,color,nPolygon,0)


    def pathPlannig(self,screen, start, goal):
        if None in [start,goal]:
            self.path = []
        if start != None:
            start = self.screenToMap(screen,start)
        if goal != None:
            goal = self.screenToMap(screen,goal)

        self.start = start
        self.goal = goal

        if not None in [start,goal]:
            print "Procurando!"
            tstart = time.time()
            def distance(pt1,pt2):
                return sqrt( pow(pt2[1]-pt1[1],2) + pow(pt2[0]-pt1[0],2))

            def heuristic(pt):
                return distance(pt,goal)

            def hashing(pt):
                return ", ".join([str(i) for i in pt])

#            neighbors = [[-1,-1], [0,-1], [1,-1], [-1,0], [1,0], [-1,1], [0,1], [1,1]]
            neighbors = [[0,-1], [-1,0], [1,0], [0,1]]
            closeset = []
            openset = [start]
            h = hashing(start)
            g_score = {h: 0}
            f_score = {h: g_score[h] + heuristic(start)}
            came_from = {}
            last = start
            visitados = 1
            while openset != []:
                current = min(openset,key=lambda pt: f_score[hashing(pt)])

                if current == goal:
                    print "Achou!!"
                    path = []
                    path.append(current)
                    path.append(last)
                    while(came_from.has_key(hashing(last))):

                        last = came_from[hashing(last)]
                        path.append(last)
                    self.path = path[::-1]
                    print "Tempo de busca: {0}".format(time.time() - tstart)
                    print "Nós visitados: {0}".format(visitados)
                    return
                openset.remove(current)
                closeset.append(current)
                hc = hashing(current)
                for neighbor in neighbors:
                    neighbor = (current[0]+neighbor[0], current[1]+neighbor[1])
                    visitados += 1
                    if self.map[neighbor[1]][neighbor[0]].isObstacle:
                        continue

                    h = hashing(neighbor)
                    t_g_score = g_score[hc] + distance(neighbor,current)
                    t_f_score = t_g_score + heuristic(neighbor)

                    if neighbor in closeset:
                        continue

                    if not neighbor in openset or t_f_score < f_score[h]:
                        came_from[h] = current
                        g_score[h] = t_g_score
                        f_score[h] = t_f_score
                        if not neighbor in openset:
                            openset.append(neighbor)
                last = current

    def __len__(self):
        return self.width*self.height
