#!/usr/bin/python

import sys,math,os,re
from genBasic import *

class Tool:
    def __init__(self,f="",width=700,height=900,subAreaSize=0.5):
        self.area=[]
        self.maxR=0.0
        self.size=subAreaSize
        self.width=int(width/subAreaSize)+1
        self.height=int(height/subAreaSize)+1
        for i in range(self.width+1):
            self.area.append([])
            for j in range(self.height+1):
                self.area[i].append([])
        if f!="":
            self.load(f)
    
    def load(self,f):
        ofile=open(f,"r")
        for line in ofile:
            s = re.split('[\s]+', line.strip("\n"))
            if s[1] == "#P":
                v={"name":s[0],
                    "x":float(s[2]),
                    "y":float(s[3]),
                    "r":float(s[4][1:])/2000
                  }
                self.area[int(v["x"]/self.size)][int(v["y"]/self.size)].append(v)
                if v["r"]>self.maxR:
                    self.maxR=v["r"]
        ofile.close()
        print "data loaded."

    def checkPitch(self,pitch):
        ngVias=[]
        maxPitch=pitch+self.maxR*2
        for i in range(self.width):
            for j in range(self.height):
                self.area[i][j].sort(key=lambda v:v["x"])
        for i in range(self.width):
            for j in range(self.height):
                currentArea=self.area[i][j]
                viasCount=len(currentArea)
                for m,v1 in enumerate(currentArea):
                    n=m+1
                    D=v1["r"]+pitch
                    while n<viasCount:
                        v2=currentArea[n]
                        if abs(v2["y"]-v1["y"])<maxPitch and (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias.append(v1["name"])
                            ngVias.append(v2["name"])
                        if v2["x"]-v1["x"]>maxPitch:
                            break
                        n+=1
                    for v2 in self.area[i][j+1]:
                        if abs(v2["y"]-v1["y"])<maxPitch and (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias.append(v1["name"])
                            ngVias.append(v2["name"])
                    for v2 in self.area[i+1][j]:
                        if abs(v2["x"]-v1["x"])>maxPitch:
                            break
                        else:
                            if (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                                ngVias.append(v1["name"])
                                ngVias.append(v2["name"])
                    for v2 in self.area[i+1][j+1]:
                        if abs(v2["x"]-v1["x"])>maxPitch:
                            break
                        else:
                            if (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                                ngVias.append(v1["name"])
                                ngVias.append(v2["name"])
                    if j>0:
                        for v2 in self.area[i+1][j-1]:
                            if abs(v2["x"]-v1["x"])>maxPitch:
                                break
                            else:
                                if (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                                    ngVias.append(v1["name"])
                                    ngVias.append(v2["name"])
        return set(ngVias)

def gensOutput(vias,wkLayer="",prex="_xx"):
    if len(vias)>0:
        for v in vias:
            COM('sel_layer_feat,operation=select,layer='+wkLayer+',index='+str(v[1:]))
        if int(COM('get_select_count')[-1]) != 0:
            COM('sel_copy_other,dest=layer_name,target_layer='+wkLayer+prex+',invert=no,dx=0,dy=0,size=0,x_anchor=0,y_anchor=0,rotation=0,mirror=none')
        COM('zoom_back')
        PAUSE(str(len(vias))+' ng holes in '+wkLayer)
    else:
        COM('zoom_back')
        PAUSE('Checked ok.')

if 'JOB' and 'STEP' not in os.environ.keys(): 
    PAUSE('Need to run this from within a job and step...')
    sys.exit()

xs = COM('open_entity,job='+os.environ['JOB']+',type=step,name='+os.environ['STEP']+',iconic=no')
AUX('set_group,group='+xs[-1])
wkLayer = COM('get_work_layer')[-1]
if wkLayer == "":
    PAUSE('Need to run this on a work layer...')
    sys.exit()

VOF()
COM('delete_layer,layer='+wkLayer+'_ng')
COM('create_layer,layer='+wkLayer+'_ng,context=misc,type=drill,polarity=positive,ins_layer=')
VON()

COM('sel_clear_feat')
COM('clear_layers')
COM('affected_layer,name=,mode=all,affected=no')
COM('units,type=inch')
COM('pan_center,x=99,y=99')

COM('display_layer,name='+wkLayer+',display=yes,number=1')
COM('work_layer,name='+wkLayer)

inputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.input'
outputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.output'
COM('info, out_file='+inputFile+',units=mm,args= -t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d FEATURES -o break_sr+feat_index')

try:
    pitch=float(sys.argv[1])
except:
    pitch=0.0508

try:
    viaHoles=Tool(inputFile,width=700,height=900,subAreaSize=0.5)
except:
    print "Openging source data file error!"
    sys.exit()

try:
    ngViaNames=viaHoles.checkPitch(pitch)
except:
    print "Unexpected errors, please contact the programmer."
    sys.exit()

try:
    gensOutput(ngViaNames,wkLayer,"_ng")
except:
    print "Can't output data!"

sys.exit()
