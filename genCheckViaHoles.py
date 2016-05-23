#!/usr/bin/python

import sys,math,os,re,genClasses
from genBasic import *

maxWidth=700
maxHeight=900

class Tool:
    def __init__(self,f="",width=700,height=900,subAreaSize=0.5):
        self.area=[]
        self.tooling=[]
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
                if "lsr_reg" in s[8]:
                    self.tooling.append(v)
                else:
                    self.area[int(v["x"]/self.size)][int(v["y"]/self.size)].append(v)
                if v["r"]>self.maxR:
                    self.maxR=v["r"]
        ofile.close()
        for i in range(self.width):
            for j in range(self.height):
                self.area[i][j].sort(key=lambda v:v["x"])
        self.tooling.sort(key=lambda v:v["x"])

    def checkPitch(self,pitch):
        ngVias={}
        maxPitch=pitch+self.maxR*2
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

    def checkTooling(self,pitch):
        ngVias={}
        for i,v1 in enumerate(self.tooling):
            j=i+1
            while j<len(self.tooling):
                v2=self.tooling[j]
                if v2["x"]-v1["x"]>pitch:
                    break
                elif pitch>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
                    ngVias[v1["id"]]=v1
                    ngVias[v2["id"]]=v2
                j+=1
        return ngVias
    
    def checkPitchWithTooling(self,pitch):
        ngVias={}
        maxPitch=pitch+self.maxR*2
        for v1 in self.tooling:
            i=int(v1["x"]/self.size)-1
            j=int(v1["y"]/self.size)-1
            D=v1["r"]+pitch
            for m in range(3):
                for n in range(3):
                    if i+m>0 and j+n>0:
                        for v2 in self.area[i+m][j+n]:
                            if v2["x"]-v1["x"]>maxPitch:
                                break
                            elif (v2["r"]+D)>math.sqrt((v1["x"]-v2["x"])**2+(v1["y"]-v2["y"])**2):
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
        
    def msgBox(self,text="message",button="CLOSE AND CONTINUE",color="000000",font="cbr14"):
        s='WIN 400 300'+'\nCLABEL '+button+'\nFG '+color+'\nFONT '+font
        for label in text.split('\n'):
            s+='\nLABEL '+label
        s+='\nFG 000000\nFONT cbr14\nEND\n'
        self.createWIN(s)
        
def gensOutput(vias,wkLayer="",prex="_ng"):
    if len(vias)>0:
        for id in vias.keys():
            COM('sel_layer_feat,operation=select,layer='+wkLayer+',index='+id[1:])
        if int(COM('get_select_count')[-1]) != 0:
            COM('sel_copy_other,dest=layer_name,target_layer='+wkLayer+prex+',invert=no,dx=0,dy=0,size=0,x_anchor=0,y_anchor=0,rotation=0,mirror=none')

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
            "LABEL Input the threshold value:",
            "FG 000000",
            "FONT cbr14",
            "RADIO radio1 'Checking  normal  via  holes:  ' H 1 990000",
            "Yes",
            "No",
            "END",
            "FONT cmr14",
            "FORM radio1 1",
            "TEXT threshold1 5 Edge-to-edge  spacing  Min  :",
            "DTEXT threshold1 4",
            "LABEL mil",
            "ENDFORM",
            "FONT cbr14",
            "RADIO radio2 'Checking  tooling  via holes: ' H 1 990000",
            "Yes",
            "No",
            "END",
            "FONT cmr14",
            "FORM radio2 1",
            "TEXT threshold2 5 Center-to-center spacing Min:",
            "DTEXT threshold2 0.5",
            "LABEL mil",
            "ENDFORM",
            "FONT cbr14",
            "RADIO radio3 'Checking normal with tooling:' H 1 990000",
            "Yes",
            "No",
            "END",
            "FONT cmr14",
            "FORM radio3 1",
            "TEXT threshold3 5 Edge-to-edge  spacing  Min  :",
            "DTEXT threshold3 5",
            "LABEL mil",
            "FONT cbr14",
            "ENDFORM"
        ]
options=myGUI.createWIN(optionWin)
if len(options)==0:
    sys.exit()
try:
    threshold1=float(options.get("threshold1"))*0.0254
    threshold2=float(options.get("threshold2"))*0.0254
    threshold3=float(options.get("threshold3"))*0.0254
except:
    myGUI.msgBox(text="Invalid number in the value.",button="CLOSE",font="cbr18",color="700000")
    sys.exit()

COM('sel_clear_feat')
COM('clear_layers')
COM('affected_layer,name=,mode=all,affected=no')
COM('units,type=inch')
COM('pan_center,x=99,y=99')

COM('display_layer,name='+wkLayer+',display=yes,number=1')
COM('work_layer,name='+wkLayer)

inputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.input'
COM('info, out_file='+inputFile+',units=mm,args= -t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d FEATURES -o index+break_sr')

try:
    viaHoles=Tool(inputFile,width=maxWidth,height=maxHeight,subAreaSize=0.5)
except:
    GenGUI().msgBox(text="Openging source data file error!",button="CLOSE")
    sys.exit()

try:
    ngVias,ngVias1,ngVias2,ngVias3={},{},{},{}
    if options.get("radio1")==1:
        ngVias1=viaHoles.checkPitch(threshold1)
        print str(len(ngVias1))+" ng holes found in normal via holes."
    if options.get("radio2")==1:
        ngVias2=viaHoles.checkTooling(threshold2)
        print str(len(ngVias2))+" ng holes found in tooling via holes."
    if options.get("radio3")==1:
        ngVias3=viaHoles.checkPitchWithTooling(threshold3)
        print str(len(ngVias3))+" ng holes found between tooling and normal holes."
    ngVias.update(ngVias1)
    ngVias.update(ngVias2)
    ngVias.update(ngVias3)
except:
    GenGUI().msgBox(text="Unexpected errors, please contact the programmer.",button="CLOSE")
    sys.exit()

try:
    if len(ngVias)>0:
        VOF()
        COM('delete_layer,layer='+wkLayer+'_ng')
        COM('create_layer,layer='+wkLayer+'_ng,context=misc,type=drill,polarity=positive,ins_layer=')
        VON()
        gensOutput(ngVias,wkLayer,"_ng")
        GenGUI().msgBox(text=str(len(ngVias))+' ng holes found in <'+wkLayer+'>!\nPlease refer to layer <'+wkLayer+'_ng>.',button='CLOSE',color='700000',font="cbr20")
        
        #for v in ngVias.values():
        #    print v["id"],v["x"],v["y"]
    else:
        GenGUI().msgBox(text="Checked ok!",button="CLOSE",color="003000",font="cbr24")
    COM('zoom_back')

except:
    GenGUI().msgBox(text="Can't output data!",button="CLOSE")

sys.exit()
