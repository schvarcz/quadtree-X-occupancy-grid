# -*- coding:utf8 -*-
import time
import pygame
from pygame.locals import *
from math import ceil, floor, atan2, degrees, radians, sqrt, cos, sin

#States
UNKNOWN = 0
MISTO = 1
CHEIO = 2
VAZIO = 3

#Mode
EDGES = 0
NO_EDGES = 1


#Tables of Quadtree
ADJ = {
    "NO": {
            "N": True,
            "S": False,
            "E": False,
            "O": True,
            "NO": True,
            "SO": False,
            "NE": False,
            "SE": False,
        },
    "NE": {
            "N": True,
            "S": False,
            "E": True,
            "O": False,
            "NO": False,
            "SO": False,
            "NE": True,
            "SE": False,
        },
    "SO": {
            "N": False,
            "S": True,
            "E": False,
            "O": True,
            "NO": False,
            "SO": True,
            "NE": False,
            "SE": False,
        },
    "SE": {
            "N": False,
            "S": True,
            "E": True,
            "O": False,
            "NO": False,
            "SO": False,
            "NE": False,
            "SE": True,
        },
    }


REFLECT = {
    "NO": {
            "N": "SO",
            "S": "SO",
            "E": "NE",
            "O": "NE",
            "NO": "SE",
            "SO": "SE",
            "NE": "SE",
            "SE": "SE",
        },
    "NE": {
            "N": "SE",
            "S": "SE",
            "E": "NO",
            "O": "NO",
            "NO": "SO",
            "SO": "SO",
            "NE": "SO",
            "SE": "SO",
        },
    "SO": {
            "N": "NO",
            "S": "NO",
            "E": "SE",
            "O": "SE",
            "NO": "NE",
            "SO": "NE",
            "NE": "NE",
            "SE": "NE",
        },
    "SE": {
            "N": "NE",
            "S": "NE",
            "E": "SO",
            "O": "SO",
            "NO": "NO",
            "SO": "NO",
            "NE": "NO",
            "SE": "NO",
        },
    }


COMMON_EDGE = {
    "NO": {
            "NO": None,
            "SO": "O",
            "NE": "N",
            "SE": None,
        },
    "NE": {
            "NO": "N",
            "SO": None,
            "NE": None,
            "SE": "E",
        },
    "SO": {
            "NO": "O",
            "SO": None,
            "NE": None,
            "SE": "S",
        },
    "SE": {
            "NO": None,
            "SO": "S",
            "NE": "E",
            "SE": None,
        },
    }


SONS = {
    "N": ["NO", "NE"],
    "S": ["SO", "SE"],
    "E": ["NE", "SE"],
    "O": ["NO","SO"],
    "NO": ["NO"],
    "SO": ["SO"],
    "NE": ["NE"],
    "SE": ["SE"],
    }

DIR_REFLECT = {
    "N": "S",
    "S": "N",
    "E": "O",
    "O": "E",
    "NO": "SE",
    "SO": "NE",
    "NE": "SO",
    "SE": "NO",

    }

class Node(object):
    NE = NO = SE = SO = None

    def __init__(self, top=-100000, left=-100000, w=200000, h=200000, tipo = UNKNOWN, parent = None):
        self.top = top
        self.left = left
        self.width = w
        self.height = h
        self.__tipo__ = tipo
        self.himm = 0
        self.parent = parent


    @property
    def center(self):
        return self.left+self.width/2., self.top + self.height/2.


    @property
    def hash(self):
        return self.left+self.width/2., self.top + self.height/2.

    
    @property
    def tipo(self):
        return self.__tipo__


    @tipo.setter
    def tipo(self,value):
        if not value in [UNKNOWN,VAZIO, CHEIO,MISTO]:
            raise Exception("NODE: Type not valid")
        
        if self.__tipo__ == CHEIO:
            self.addHIMM()
        elif self.__tipo__ == VAZIO:
            self.subHIMM()
        else:
            self.__tipo__ = value


    def addHIMM(self):
        self.himm += 3
        if self.himm > 15:
            self.himm = 15
        
        if self.himm >= 6:
            self.__tipo__ = CHEIO


    def subHIMM(self):
        self.himm -= 1
        if self.himm < 0:
            self.himm = 0

        if self.himm < 6:
            self.__tipo__ = VAZIO


    def __neighborsDirection__(self,node,direction):
        nodeDir = self.dirByNode(node)
#        print nodeDir, direction
        if ADJ[nodeDir][direction]:
            if direction in ["NO", "NE", "SE", "SO"]:
                n, t = self.parent.__neighborsDirectionVertex__(self,direction)
            else:
                n, t = self.parent.__neighborsDirection__(self,direction)
            if n.tipo in [UNKNOWN, CHEIO, VAZIO]:
                return n, t+1
            return n.nodeByDir(REFLECT[nodeDir][direction]), t+1
        else:
            return self.nodeByDir(REFLECT[nodeDir][direction]), 1


    def __neighborsDirectionVertex__(self,node,direction):
        nodeDir = self.dirByNode(node)
#        print nodeDir, direction
        if ADJ[nodeDir][direction]:
            if direction in ["NO", "NE", "SE", "SO"]:
                n, t = self.parent.__neighborsDirectionVertex__(self,direction)
            else:
                n, t = self.parent.__neighborsDirection__(self,direction)
            if n.tipo in [UNKNOWN, CHEIO, VAZIO]:
                return n, t+1
            return n.nodeByDir(REFLECT[nodeDir][direction]), t+1
        elif COMMON_EDGE[nodeDir][direction] != None:
            n, t = self.parent.__neighborsDirection__(self, COMMON_EDGE[nodeDir][direction])
            return n, t+1
        else:
            return self.nodeByDir(REFLECT[nodeDir][direction]), 1


    def neighborsDirection(self,direction):
        if direction in ["NO", "NE", "SE", "SO"]:
            n, t = self.parent.__neighborsDirectionVertex__(self,direction)
        else:
            n, t = self.parent.__neighborsDirection__(self,direction)
        if n.tipo == MISTO and not direction in ["NO", "NE", "SE", "SO"]:
#            print "direction ",self.parent.dirByNode(self), direction, DIR_REFLECT[direction]
            direction = DIR_REFLECT[direction]
            sons_dir = SONS[direction]
#            print "sons ", sons_dir
            openset = [n]
            ret = []
            while openset != []:
#                print "openset ", openset
                current = openset[0]
                openset.remove(current)
                t += 1
                if current.tipo == MISTO:
                    for nodeDir in sons_dir:
#                        print nodeDir
                        openset.append(current.nodeByDir(nodeDir))
                elif current.tipo == VAZIO:
                    ret.append(current)
            return ret, t
        if n.tipo == VAZIO:
            return [n], t
        return [], t


    def nodeByDir(self,direction):
        if direction == "NO":
            return self.NO
        if direction == "NE":
            return self.NE
        if direction == "SO":
            return self.SO
        if direction == "SE":
            return self.SE


    def dirByNode(self,node):
        if self.NO == node:
            return "NO"
        if self.NE == node:
            return "NE"
        if self.SO == node:
            return "SO"
        if self.SE == node:
            return "SE"


    def putObstaculo(self, p, value = CHEIO, minSize = 100):
        if self.tipo == value:
            return
        w,h = self.width/2., self.height/2.
        if self.tipo in [UNKNOWN, VAZIO, CHEIO]:
            self.NO, self.NE, self.SO, self.SE = (Node(self.top,self.left, w,h,self.tipo,self),
                                                    Node(self.top,self.left+w, w,h,self.tipo,self),
                                                    Node(self.top+h,self.left, w,h,self.tipo,self),
                                                    Node(self.top+h,self.left+w, w,h,self.tipo,self))
            self.tipo = MISTO

        if self.tipo == MISTO:
            if w + self.left > p[0]:
                if h + self.top > p[1]:
                    if w > minSize and h > minSize:
                        self.NO.putObstaculo(p,value)
                    else:
                        self.NO.tipo = value
                else:
                    if w > minSize and h > minSize:
                        self.SO.putObstaculo(p,value)
                    else:
                        self.SO.tipo = value
            else:
                if h + self.top > p[1]:
                    if w > minSize and h > minSize:
                        self.NE.putObstaculo(p,value)
                    else:
                        self.NE.tipo = value
                else:
                    if w > minSize and h > minSize:
                        self.SE.putObstaculo(p,value)
                    else: 
                        self.SE.tipo = value

        if (self.tipo == MISTO) and (self.NO.tipo == self.NE.tipo == self.SE.tipo == self.SO.tipo != MISTO):
            maxi = max(self.NE.himm,self.NO.himm,self.SO.himm,self.SE.himm)
            mini = min(self.NE.himm,self.NO.himm,self.SO.himm,self.SE.himm)
            
            if (maxi-mini) < 10:
                self.tipo = self.NE.tipo
                self.himm = maxi
                self.NE = self.NO = self.SE = self.SO = None


    def whoContains(self, pt):

        if self.tipo in [UNKNOWN, VAZIO, CHEIO]:
            return self

        w,h = self.width/2., self.height/2.

        if w + self.left > pt[0]:
            if h + self.top > pt[1]:
                return self.NO.whoContains(pt)
            else:
                return self.SO.whoContains(pt)
        else:
            if h + self.top > pt[1]:
                return self.NE.whoContains(pt)
            else:
                return self.SE.whoContains(pt)



    def isInside(self,p):
        if (self.top <= p[1] < self.height+self.top) and (self.left <= p[0] < self.width+self.left):
            return True
        return False


    def drawNode(self,screen,minRect, celSize, mode = EDGES):

        s = screen.get_size()

        (minx,miny),(maxx,maxy) = minRect
        sx, sy = celSize
        #Arrumar para desenhar somente o que for visivel
        #if self.isInside((minx,miny)) or self.isInside((minx,maxy)) or self.isInside((maxx,maxy)) or self.isInside((maxx,miny)):

        p = floor(self.left - minx)*sx, s[1] - floor(self.top - miny)*sy
        size = ceil(self.width*sx),-ceil(self.height*sy)
        if self.tipo == CHEIO:
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),0)
            if mode == EDGES:
                pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == VAZIO:
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(p, size),0)
            if mode == EDGES:
                pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == UNKNOWN and mode == EDGES:
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == MISTO:
            self.NO.drawNode(screen,minRect,celSize,mode)
            self.SO.drawNode(screen,minRect,celSize,mode)
            self.NE.drawNode(screen,minRect,celSize,mode)
            self.SE.drawNode(screen,minRect,celSize,mode)


    def drawNodePath(self,screen,minRect, celSize,color=(255,255,0)):

        s = screen.get_size()

        (minx,miny),(maxx,maxy) = minRect
        sx, sy = celSize

        p = floor(self.left - minx)*sx, s[1] - floor(self.top - miny)*sy
        size = ceil(self.width*sx),-ceil(self.height*sy)
        pygame.draw.rect(screen,color,pygame.Rect(p, size),1)


    def __len__(self):
        if self.tipo in [UNKNOWN,VAZIO,CHEIO]:
            return 1
        if self.tipo == MISTO:
            return 1 + len(self.NO) + len(self.NE) + len(self.SO) + len(self.SE)


    def __eq__(self,n):
        return self.top == n.top and self.left == n.left and self.width == n.width and self.height == n.height

    def __repr__(self):
        return self.parent.dirByNode(self)


class Quadtree(Node):

    minSize = 100
    scale = 1.
    center = (0.,0.)
    start = goal = None


    def __init__(self, top=-100000, left=-100000, w=200000, h=200000, tipo = UNKNOWN):
        super(Quadtree,self).__init__(top, left, w, h, tipo)
        self.mode = EDGES
        self.path = self.openset = self.closeset = []


    def putObstaculoSweep(self,roboPos,leituras):
        x,y = roboPos[0], roboPos[1]
        pad = 5500.

        minx, miny, maxx, maxy = x - pad, y - pad, x + pad, y + pad

        variacao = 100
        for nx in xrange(int(minx),int(maxx),self.minSize):
            for ny in xrange(int(miny),int(maxy),self.minSize):

                center = nx, ny
                angle = degrees(atan2(center[1]-roboPos[1],center[0]-roboPos[0])) - roboPos[2]

                angle %= 360
                if angle> 180:
                    angle -= 360

                if -90. <= angle <= 90.:

                    r = leituras[int(90-angle)]
                    r = min(r,5000)
            
                    d = sqrt(pow(center[1]-roboPos[1],2) + pow(center[0]-roboPos[0],2))

                    if r < 5000 and r-variacao < d < r+variacao:
                        self.putObstaculo(center,CHEIO,self.minSize)
                    elif d <= r-variacao:
                        self.putObstaculo(center,VAZIO,self.minSize)


    def worldToScreen(self,screen, pt):
        x, y = pt
        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)

        return int(sx*(x-minx)), s[1] - int(sy*(y-miny))


    def screenToWorld(self,screen, pt):
        x, y = pt
        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)


        return x/sx + minx, (s[1] - y)/sy + miny


    def draw(self,screen):

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height


        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)
        celSize = sx, sy
        minRect = (minx,miny),(maxx,maxy)

        self.drawNode(screen,minRect,celSize,self.mode)


        if (self.start != None):
            self.whoContains(self.start).drawNodePath(screen,minRect,celSize,self.mode)
        if (self.goal != None):
            self.whoContains(self.goal).drawNodePath(screen,minRect,celSize,self.mode)



    def drawRobot(self,screen,x,y,th,leituras):

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)

        robot = int(sx*(x-minx)), s[1] - int(sy*(y-miny))
        pygame.draw.circle(screen,(255,0,0),robot,int(1.*self.scale),0)
        if leituras != []:
            dLaser = [robot]
            angle = 90+th
            for r in leituras:
                if r > 5000:
                    r = 5000
                dLaser.append((
                                sx*(x + r*cos(radians(angle)) - minx) ,
                                s[1] - sy*(y + r*sin(radians(angle)) - miny)))
                angle -= 1
            
            pygame.draw.polygon(screen,(0,0,255),dLaser,0)


    def drawPathPlanning(self,screen):

        if (self.start != None):
            self.drawPoint(screen,self.start,(0,0,255))
        if (self.goal != None):
            self.drawPoint(screen,self.goal,(255,0,0))

        if self.path != []:
#            for pt in self.openset:
#                self.drawPoint(screen,pt.center,(0,255,255))
#            for pt in self.closeset:
#                self.drawPoint(screen,pt.center,(255,0,255))
#            for pt in self.path:
#                self.drawPoint(screen,pt.center,(0,0,255))
            pts = [self.worldToScreen(screen,pt) for pt in self.path]
            pygame.draw.lines(screen,(0, 0, 255), False,pts,int(1.*self.scale))


    def drawPoint(self,screen,pt,color = (0,255,0), size = 1):
        pt = self.worldToScreen(screen,pt)

        pygame.draw.circle(screen,color,pt,int(size*self.scale),0)


    def pathPlannig(self,screen, start, goal):
        if None in [start,goal]:
            self.path = []
        if start != None:
            start = self.screenToWorld(screen,start)
        if goal != None:
            goal = self.screenToWorld(screen,goal)

        self.start = start
        self.goal = goal

        if not None in [start,goal]:
            startpt = start
            goalpt = goal
            print "Procurando!"
            tstart = time.time()
            start = self.whoContains(start)
            goal = self.whoContains(goal)
            def distance(pt1,pt2):
                return sqrt( pow(pt2.center[1]-pt1.center[1],2) + pow(pt2.center[0]-pt1.center[0],2))

            def heuristic(pt):
#                return sqrt( pow(goalpt[1]-pt.center[1],2) + pow(goalpt[0]-pt.center[0],2))
                return distance(pt,goal)

            closeset = []
            openset = [start]
            h = hash(start)
            g_score = {h: 0}
            f_score = {h: g_score[h] + heuristic(start)}
            came_from = {}
            last = start
            visitados = 1
            while openset != []:
                current = min(openset,key=lambda pt: f_score[hash(pt)])

                if current == goal:
                    print "Achou!!"
                    path = []
                    path.append(goalpt)
#                    path.append(current)
                    path.append(last.center)
                    while(came_from.has_key(hash(last))):

                        current = came_from[hash(last)]
                        if current.left == last.left or current.width+current.left == last.left+last.width:
                            if current.width < last.width:
                                x = current.left + current.width/2.

                            else:
                                x = last.left + last.width/2.

                            if current.top < last.top:
                                y = current.top + current.height
                            else:
                                y = current.top
                        if current.top == last.top or current.height+current.top == last.top+last.height:
                            if current.height < last.height:
                                y = current.top + current.height/2.
                            else:
                                y = last.top + last.height/2.

                            if current.left < last.left:
                                x = current.left+current.width
                            else:
                                x = current.left

                        path.append((x,y))
                        last = current
                        path.append(last.center)
                    path.pop()
                    path.append(startpt)
                    self.path = path[::-1]
                    self.openset = openset
                    self.closeset = closeset

                    print "Tempo de busca: {0}".format(time.time() - tstart)
                    print "Nós visitados: {0}".format(visitados)
                    return self.path
                openset.remove(current)
                closeset.append(current)
                hc = hash(current)

                neighbors = []
#                for direction in ["N","S","O","E","NO","SO","NE","SE"]:
                for direction in ["N","S","O","E"]:
                    nei, t = current.neighborsDirection(direction)
                    neighbors += nei
                    visitados += t

                for neighbor in neighbors:
                    h = hash(neighbor)
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

