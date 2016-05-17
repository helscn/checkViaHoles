#!/usr/bin/python

import sys,math,os,re

class Tool:
    def __init__(self,f=""):
        self.vias=[]
        self.maxR=0
        if f!="":
            self.load(f)
    
    def load(self,f):
        ofile=open(f,"r")
        self.vias=[]
        for line in ofile:
            s = re.split('[\s]+', line.strip("\n"))
            if s[1] == "#P":
                v=[s[0],float(s[2]),float(s[3]),s[4],float(s[4][1:])/2000]
                self.vias.append(v)
                if v[4]>self.maxR:
                    self.maxR=v[4]
        ofile.close()
            
    def checkPitch(self,pitch):
        self.vias.sort(key=lambda v:v[2])
        viasCount=len(self.vias)
        ngVias=[]
        maxPitch=pitch+self.maxR*2
        for i,v in enumerate(self.vias):
            j=i+1
            while j<viasCount:
                v2=self.vias[j]
                if abs(v2[1]-v[1])<maxPitch and (v[4]+v2[4]+pitch)>math.sqrt((v[1]-v2[1])**2+(v[2]-v2[2])**2):
                    ngVias.append(v[0])
                    ngVias.append(v2[0])
                if v2[2]-v[2]>maxPitch:
                    break
                j+=1
        return set(ngVias)

def gensOutput(vias,wkLayer="",prex="_XX"):
    if len(vias)>0:
        for v in vias:
            COM('sel_layer_feat,operation=select,layer='+wkLayer+',index='+str(v[1:]))
        if int(COM('get_select_count')[-1]) != 0:
            COM('sel_copy_other,dest=layer_name,target_layer='+wkLayer+prex+',invert=no,dx=0,dy=0,size=0,x_anchor=0,y_anchor=0,rotation=0,mirror=none')
        PAUSE(str(len(vias))+' ng holes in '+wkLayer)
    else
        PAUSE('Checked ok.')

if 'JOB' and 'STEP' not in os.environ.keys(): 
    PAUSE('Need to run this from within a job and step...')
    sys.exit()

COM('open_job,job='+os.environ['JOB'])
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
COM('pan_center,x=99,y=99')
COM('units,type=inch')

COM('display_layer,name='+wkLayer+',display=yes,number=1')
COM('work_layer,name='+wkLayer)

#xinfo = DO_INFO('-t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d SYMS_HIST')
#threshold = float(xinfo['gSYMS_HISTsymbol'][0][1:]) * 25.4 / 1000.0
#print(threshold)

inputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.input'
outputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.output'
COM('info, out_file='+inputFile+',units=mm,args= -t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d FEATURES -o feat_index')


pitch=0.102

try:
    viaHoles=Tool(inputFile)
except:
    print "Openging source data file error!"
    sys.exit()

try:
    ngViasName=viaHoles.checkPitch(pitch)
except:
    print "Unexpected errors, please contact the programmer."
    sys.exit()

try:
    gensOutput(ngViasName,wkLayer,"_ng")
    print "Job finished!"
except:
    print "Can't output data!"
    
sys.exit()
