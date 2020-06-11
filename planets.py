from vpython import sphere, vector, color, pi, mag, label, rate, scene, local_light, text
import random
import string
import math
import numpy as np
import time
startTime = time.time()
scene.lights = []
class Planet:
    def colorMe(self):
        if self.mass >= 1e22:
            self.planet.color = color.red
            self.planet.trail_color = color.red
        elif self.mass >= 1e18:
            self.planet.color = color.orange
            self.planet.trail_color = color.orange
        elif self.mass >= 1e14:
            self.planet.color = color.yellow
            self.planet.trail_color = color.yellow
        elif self.mass >= 1e10:
            self.planet.color = color.green
            self.planet.trail_color = color.green
        elif self.mass >= 1e6:
            self.planet.color = color.blue
            self.planet.trail_color = color.blue
        else:
            self.planet.color = color.white
            self.planet.trail_color = color.white
    def __init__(self, pos, mass, orbitalParentmass, orbitalParentpos, orbitalParentv):
        self.age = 0
        self.mass = mass
        self.planet = sphere(pos = pos, radius = ((3*self.mass)/(4*pi*3000))**(1/3), make_trail = True, retain=5000)
        self.colorMe()
        self.G = 6.7e-11
        r = orbitalParentpos.x - self.planet.pos.x
        rmag = abs(r)
        inner = self.G * orbitalParentmass / rmag
        self.v = vector(orbitalParentv.x,0,orbitalParentv.z + (random.choice([-1,1]) * math.sqrt(inner)) + random.randint(0,100))
        self.p = self.mass * self.v
        self.Vol = (4 * pi * (self.planet.radius**3))/3
        self.name = (''.join([random.choice(string.ascii_letters) for n in range(4)])).lower()
        self.name = self.name.capitalize()
        self.label = label(pos=self.planet.pos, height=16, yoffset = 5, text=self.name + "\n" + str(int(mag(self.v))) + "m/s", line=False)
        print("New Planet " + self.name)
    
    def update(self,dt,solarObjects):
        self.age = self.age + dt
        Ftotal = vector(0,0,0)
        for solarObject in solarObjects:
            if solarObject.name == self.name:
                continue
            r =  solarObject.planet.pos - self.planet.pos
            rmag = mag(r)
            if rmag < (self.planet.radius + solarObject.planet.radius):
                if self.mass > solarObject.mass:
                    solarObject.planet.visible = 0
                    solarObject.planet.clear_trail()
                    solarObject.label.visible = False
                    self.Vol = self.Vol + solarObject.Vol
                    self.planet.radius = ((self.Vol * 3)/(4*pi))**(1/3)
                    self.mass = self.mass + solarObject.mass
                    self.v = (self.p + solarObject.p)/ self.mass
                    solarObjects.remove(solarObject)
                    print(solarObject.name + " collided with " + self.name)
                else:
                    self.planet.visible = 0
                    self.planet.clear_trail()
                    self.label.visible = False
                    solarObject.Vol = self.Vol + solarObject.Vol
                    solarObject.planet.radius = ((solarObject.Vol * 3)/(4*pi))**(1/3)
                    solarObject.mass = self.mass + solarObject.mass
                    solarObject.v = (self.p + solarObject.p)/ solarObject.mass
                    solarObjects.remove(self)
                    print(self.name + " collided with " + solarObject.name)
                self.colorMe() 
            Fmag = self.G * self.mass * solarObject.mass / (rmag**2)
            rhat = r/rmag
            Fnet = Fmag * rhat
            Ftotal = Ftotal + Fnet
        self.v = self.v + ((Ftotal/self.mass) * dt)
        self.p = self.v * self.mass
        self.planet.pos = self.planet.pos + (self.v*dt)
        self.label.pos = self.planet.pos
        self.label.text = self.name + "\n" + str(int(mag(self.v))) + "m/s"
        return solarObjects    
dt = 1
orbitalParent = Planet(pos=vector(0,0,0), mass = 1e18, orbitalParentmass = 0, orbitalParentpos = vector(1,1,1), orbitalParentv = vector(0,0,0))
orbitalParent.planet.emissive = True
bigLight = local_light(pos = orbitalParent.planet.pos, color = orbitalParent.planet.color)
solarObjects = [orbitalParent]
radiusScale = 4
orbitalParent.v = vector(0,0,0)
ct = 0
ctr = 0
while True:
    rate(200)
    ct += dt
    scene.title = "Time since last collision: " + str(ct) + "s\n" + "Record: " + str(ctr) + "s"
    if ct > ctr:
        ctr = ct
    scene.camera.follow(orbitalParent.planet)
    bigLight.pos = orbitalParent.planet.pos
    #orbitalParent.v = vector(0,0,0)
    for solarObject in solarObjects:
        if solarObject.mass > orbitalParent.mass:
            orbitalParent = solarObject
            orbitalParent.planet.emissive = True
            orbitalParent.v *= 0
        if mag(orbitalParent.planet.pos - solarObject.planet.pos) > 2e9:
            print("Removing " + solarObject.name + " due to being too far.")
            solarObject.planet.visible = 0
            solarObject.planet.clear_trail()
            solarObject.label.visible = False
            solarObjects.remove(solarObject)
        sopre = len(solarObjects)
        solarObjects = solarObject.update(dt, solarObjects)
        if len(solarObjects) < sopre:
            ct = 0
    if (random.randint(0,2000) >= 1999) & (len(solarObjects) <= 15):
        solarObjects.append(Planet(pos = vector(orbitalParent.planet.pos.x + random.randint(-radiusScale*int(orbitalParent.planet.radius),radiusScale*int(orbitalParent.planet.radius)),0,orbitalParent.planet.pos.z), mass = random.randint(1,9) * (10 ** random.randint(10,22)), orbitalParentmass = orbitalParent.mass, orbitalParentpos = orbitalParent.planet.pos, orbitalParentv = orbitalParent.v))