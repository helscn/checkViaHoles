#!/usr/bin/python

import sys,math,os,re,genClasses
from genBasic import *

maxWidth=700
maxHeight=900

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
                v={ "id":s[0],
                    "x":float(s[2]),
                    "y":float(s[3]),
                    "r":float(s[4][1:])/2000
                  }
                self.area[int(v["x"]/self.size)][int(v["y"]/self.size)].append(v)
                if v["r"]>self.maxR:
                    self.maxR=v["r"]
        ofile.close()

    def checkPitch(self,pitch):
        ngVias={}
        maxPitch=pitch+self.maxR*2
        for i in range(self.width):
            for j in range(self.height):
                self.area[i][j].sort(key=lambda v:v["x"])
        for i in range(self.width):
            for j in range(self.height):
                currentArea=self.area[i][j]
                for m,v1 in enumerate(currentArea):
                    n=m+1
                    D=v1["r"]+pitch
                    while n<len(currentArea):
                        v2=currentArea[n]
                        if v2["x"]-v1["x"]>maxPitch:
                            break
                        elif (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                        n+=1
                    for v2 in self.area[i][j+1]:
                        if (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    for v2 in self.area[i+1][j]:
                        if v2["x"]-v1["x"]>maxPitch:
                            break
                        elif (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    for v2 in self.area[i+1][j+1]:
                        if v2["x"]-v1["x"]>maxPitch:
                            break
                        elif (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    if j>0:
                        for v2 in self.area[i+1][j-1]:
                            if v2["x"]-v1["x"]>maxPitch:
                                break
                            elif (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                                ngVias[v1["id"]]=v1
                                ngVias[v2["id"]]=v2
        return ngVias

    def checkDistance(self,distance):
        ngVias={}
        for i in range(self.width):
            for j in range(self.height):
                self.area[i][j].sort(key=lambda v:v["x"])
        for i in range(self.width):
            for j in range(self.height):
                currentArea=self.area[i][j]
                for m,v1 in enumerate(currentArea):
                    n=m+1
                    while n<len(currentArea):
                        v2=currentArea[n]
                        if v2["x"]-v1["x"]>distance:
                            break
                        elif distance>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                        n+=1
                    for v2 in self.area[i][j+1]:
                        if distance>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    for v2 in self.area[i+1][j]:
                        if v2["x"]-v1["x"]>distance:
                            break
                        elif distance>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    for v2 in self.area[i+1][j+1]:
                        if v2["x"]-v1["x"]>distance:
                            break
                        elif distance>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                            ngVias[v1["id"]]=v1
                            ngVias[v2["id"]]=v2
                    if j>0:
                        for v2 in self.area[i+1][j-1]:
                            if v2["x"]-v1["x"]>distance:
                                break
                            elif distance>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                                ngVias[v1["id"]]=v1
                                ngVias[v2["id"]]=v2
        return ngVias

class GenGUI:
    def createWIN(self,guiText):
        gen=genClasses.Genesis()
        gui = os.path.join(gen.edir, 'all', 'gui')
        if isinstance(guiText,list):
            myText="\n".join(guiText)
        else:
            myText=str(guiText)
        fo=open(gen.tmpfile,"w")
        fo.write(myText)
        fo.close()
        fd=os.popen(gui+" "+gen.tmpfile)
        result={}
        for line in fd.readlines():
            s=line[4:].split("=",1)
            result[s[0].strip()]=eval(s[1].strip())
        return result

    def inputBox(self,text="Input a value:",value="",button="CLOSE AND CONTINUE"):
        s='WIN 400 300\nCLABEL '+button+'\nTEXT text '+text+'\nDTEXT text '+value+'\nEND\n'
        return self.createWIN(s)["text"]
        
    def msgBox(self,text="",button="CLOSE AND CONTINUE"):
        self.createWIN('WIN 400 300\nCLABEL '+button+'\nLABEL '+text+'\nEND\n')
        
def gensOutput(vias,wkLayer="",prex="_ng"):
    if len(vias)>0:
        for id in vias.keys():
            COM('sel_layer_feat,operation=select,layer='+wkLayer+',index='+id[1:])
        if int(COM('get_select_count')[-1]) != 0:
            COM('sel_copy_other,dest=layer_name,target_layer='+wkLayer+prex+',invert=no,dx=0,dy=0,size=0,x_anchor=0,y_anchor=0,rotation=0,mirror=none')
        COM('zoom_back')
        GenGUI().msgBox(str(len(vias))+' ng holes in '+wkLayer,"CLOSE")

    else:
        COM('zoom_back')
        GenGUI().msgBox("Checked ok.","CLOSE")

if 'JOB' and 'STEP' not in os.environ.keys(): 
    PAUSE('Need to run this from within a job and step...')
    sys.exit()

xs = COM('open_entity,job='+os.environ['JOB']+',type=step,name='+os.environ['STEP']+',iconic=no')
AUX('set_group,group='+xs[-1])
wkLayer = COM('get_work_layer')[-1]
if wkLayer == "":
    PAUSE('Need to run this on a work layer...')
    sys.exit()

myGUI=GenGUI()
optionWin=[
            "WIN 400 300",
            "CLABEL Start to check "+wkLayer+"...",
            "FONT cbi18",
            "FG 000099",
            "LABEL Please choose the type of checking:",
            "FONT cmr14",
            "FG 000000",
            "RADIO type ' ' V 1 990000", 
            "Checking the pitch (edge to edge)",
            "Checking the distance (center to center)",
            "END",
            "FONT cbr14",
            "FORM",
            "TEXT threshold Input the min value:",
            "DTEXT threshold 4",
            "OPTION unit ''",
            "mil",
            "mm",
            "END",
            "ENDFORM"
        ]
options=myGUI.createWIN(optionWin)
if len(options)==0:
    sys.exit()
threshold=options.get("threshold")

try:
    threshold=float(threshold)
    if options.get("unit")==1:
        threshold*=0.0254
except:
    myGUI.msgBox("Invalid number in the value.","CLOSE")
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
#outputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.output'
COM('info, out_file='+inputFile+',units=mm,args= -t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d FEATURES -o index+break_sr')

try:
    viaHoles=Tool(inputFile,width=maxWidth,height=maxHeight,subAreaSize=0.5)
except:
    print "Openging source data file error!"
    sys.exit()

try:
    if options.get("type")==1:
        print "Checking the pitch:",threshold,"mm"
        ngVias=viaHoles.checkPitch(threshold)
    else:
        print "Checking the distance:",threshold,"mm"
        ngVias=viaHoles.checkDistance(threshold)
except:
    print "Unexpected errors, please contact the programmer."
    sys.exit()

try:
    gensOutput(ngVias,wkLayer,"_ng")
    #for v in ngVias.values():
    #    print v["id"],v["x"],v["y"]
except:
    print "Can't output data!"

sys.exit()
