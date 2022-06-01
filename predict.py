# -*- coding: utf-8 -*-
import os
import sys

class node(object):
    def __init__(self):
        self.name=None
        self.node=[]
        self.pra=None
    def prev(self):
        return self.pra
    def add(self):
        addnode=node()
        self.node.append(addnode)  
        addnode.pra=self
        return addnode
    def goto(self,data):
        "Gets the node by name"
        for child in range(0,len(self.node)):
            if(self.node[child].name==data):
                return self.node[child]
    def travel(self):
        print(self.name,end='-')
        for child in self.node:
            child.travel()
    def travelterminal(self):
        if len(self.node)==0:
            print(self.name,end='-')
        else:
            for child in self.node:
                child.travelterminal()   

    def tensepredict(self,fromVB,SenPOS,POStype,senbuffer,Sennum,tense,fout):  
        blockslib=0        
        for child in self.node:
            if child.name=='VP':
                blockslib=1
        if self.name=='S':
            tense.append('[')#print('[' if self.name=='S' else '',end='')
        
        for child in self.node:
            if child.name=='VP' and fromVB==False and blockslib>0:
                #print('(',end='')
                deter=True
                blockslib-=10
                for grand in child.node:
                    if grand.name=='VP':
                        #grand.tensepredict(fromVB)
                        deter=False
                if deter==True:
                    #tense.append('(')#print('(',end='')
                    rootstring=child.findsubleft(tense)
                    fout.write("{:50}".format(rootstring))
                    tense.append(Tense(SenPOS,POStype,rootstring,senbuffer,Sennum,fout))
                    #tense.append(')')#print(')',end='')
                    #if child.findbysubname('NP')
                    child.tensepredict(True,SenPOS,POStype,senbuffer,Sennum,tense,fout)
                else:
                    child.tensepredict(fromVB,SenPOS,POStype,senbuffer,Sennum,tense,fout)
                #print(')',end='')
            elif child.name=='SBAR' and len(child.node)!=1 and child.node[-1].name=='S' and (child.node[0].name!='WHADVP' or child.node[0].node[0].node[0].name.lower()=='when') and child.node[0].name!='WHNP' and child.node[0].name!='WP$' and 'that' not in child.node[0].node[0].name:
                #print('[',end='')
                tense.append(child.findbysubPOS('IN').findsubleft(tense))
                child.tensepredict(False,SenPOS,POStype,senbuffer,Sennum,tense,fout)
                #print(']',end='')
            elif self.name=='S' and child.name=='CC':
                tense.append(child.findbysubPOS('CC').findsubleft(tense))
                child.tensepredict(False,SenPOS,POStype,senbuffer,Sennum,tense,fout)
            elif blockslib==0: #child.name==None or child.name=='S' or child.name=='ROOT' or child.name=='NP' or child.name=='PP':
                child.tensepredict(fromVB,SenPOS,POStype,senbuffer,Sennum,tense,fout)
        if self.name=='S':
            tense.append(']')#print(']' if self.name=='S' else '',end='')
          
    def findsubleft(self,tense):
        if len(self.node)!=0:
            return self.node[0].findsubleft(tense)
            
        else:
            #tense.append(self.name)#print(self.name,end='')#in=in order to
            return self.name
                

    def findbysubPOS(self,name):
        for child in self.node:
            if name==child.name:
                return child
        return self
        
def BuildTree(buffer,SenPOS,POStype,senbuffer,Sennum,fout):
    oper=[]
    string=''
    for i in buffer:
        if i=='(' or i==')':
            oper.append(string)        
            oper.append(i)
            string=''
        else:
            string+=i
    oper=[s.strip(' ') for s in oper if len(s)>0 and s!=' ']
    oper1=[]
    for i in oper:
        if ' ' in i:
            oper1.append(i.split(' ')[0])
            oper1.append('(')
            oper1.append(i.split(' ')[1])
            oper1.append(')')
        else:
            oper1.append(i)
    #print(oper1)    
    index=0
    num=0
    tree=node()
    while index!=len(oper1):
        if oper1[index]=='(':
            tree=tree.add()
        elif oper1[index]==')':
            tree=tree.prev()
        else:
            if oper1[index-1]=='(' and oper1[index+1]==')':
                num+=1
                tree.name=oper1[index]+'-'+str(num)
                #print(tree.name)
            else:
                tree.name=oper1[index]
            
        index+=1
    #tree.travel()    
    #print('\n')
    tense=[]
    tree.tensepredict(False,SenPOS,POStype,senbuffer,Sennum,tense,fout)
    

    tense=Cleannoise(tense,1)    
    tense=Cleannoise(tense,2)
    

    for i in tense:
        fnest.write(i+' ')#print(i,end=' ')
    fnest.write('\n')
    #print(tense)
    #print('\n')
    #tree.findsubleft()
    #tree.travelterminal()
    #print("\n")
def Cleannoise(tense,window):
    back=1        
    while back>0:        
        back=0
        dellist=[]
        for i in range(len(tense)-window):
            if tense[i]=='[' and tense[i+window]==']':
                dellist.append(i)
                dellist.append(i+window)
                back+=1
        removeset=set(dellist)
        tense=[v for i,v in enumerate(tense) if i not in removeset]
    return tense
        
def RootTypeCheck(senPOS,rootstring):#[1545, 34, 6, 24, 0, 0,...]
    index=int(rootstring.split("-")[-1])-1
    if SenPOS[index] in verbPOS:
        roottype[0]+=1
    for i in POStype:
        if i==SenPOS[index]:
            roottype[POStype.index(i)]+=1
            
def RootCorrect(originroot,relation,relationtable,Sennum):
    for i in relationtable:       
        #print(i,i[:len(relation)])
        
        if originroot==i[len(relation):len(relation)+len(originroot)] and relation == i[:len(relation)]:
            #print("YEEYEEYEEYEEYEEYEEYEEYEE","*",i.split(',',maxsplit=1)[1].strip(' ').split(')')[0])
            return i.split(',',maxsplit=1)[1].strip(' ').split(')')[0]
    return originroot
    
def LookDepPOS(SenPOS,root,relation,relationtable,Sennum):
    POSsets={}
    for i in relationtable:       
        if root==i[len(relation):len(relation)+len(root)] and relation == i[:len(relation)]:    
            depindex=int(i.split(',',maxsplit=1)[1].strip(' ').split(')')[0].rsplit('-',maxsplit=1)[1])-1
            POSsets.update({SenPOS[depindex]:i.split(',',maxsplit=1)[1].strip(' ').split(')')[0].split('-')[0]})
    return POSsets#{POS:word}
    
def Tense(SenPOS,POStype,rootstring,senbuffer,Sennum,fout):

    #for i in range(len(senbuffer)):
    #    if 'advcl'in senbuffer[i] and rootstring in senbuffer[i]:
    #        print(Sennum,end=',')
    #print(rootstring,end='%')
    '''
    for i in POStype:            
        if SenPOS[int(rootstring.split("-")[-1])-1]==i:
            rootstring=RootCorrect(rootstring,'cop(',senbuffer,Sennum)
            rootstring=RootCorrect(rootstring,'acl(',senbuffer,Sennum)
            rootstring=RootCorrect(rootstring,'parataxis(',senbuffer,Sennum)
    '''
    MD_begoingto=False
    if 'going' in rootstring:
        rootstring=RootCorrect(rootstring,'xcomp(',senbuffer,Sennum)
        #print(rootstring,end='')
        if 'going' in rootstring:
            MD_begoingto=False
        else:
            MD_begoingto=True
            #rootstring=RootCorrect(rootstring,'advcl',senbuffer,Sennum)
    #fout.write(str(Sennum))
    
    RootTypeCheck(SenPOS,rootstring)
    fout.write('[')
    rootindex=int(rootstring.split("-")[-1])-1
    if len(LookDepPOS(SenPOS,rootstring,'auxpass(',senbuffer,Sennum) )!=0:
        #print(Sennum,'Passive')
        auxpassPOS=LookDepPOS(SenPOS,rootstring,'auxpass(',senbuffer,Sennum)
        auxPOS=LookDepPOS(SenPOS,rootstring,'aux(',senbuffer,Sennum)  
        if 'MD' in auxPOS :
            if auxPOS['MD'].lower() in ['can','ca','does','may','must','do','would','did','could','might','should','\'d','dare','need']:
                if auxPOS['MD'].lower() in ['can','ca','does','may','must','do','should','dare','need','ought']:                
                    fout.write('Present Passive Simple')
                elif auxPOS['MD'].lower() in ['might','could','would','\'d','did']:
                    fout.write('Past Passive Simple')
                else:
                    fout.write('Fail to label 0')
            elif auxPOS['MD'].lower() in ['will','\'ll','wo','shall','shalt','wilt'] and ('VB' or 'VBG' or 'VBN') in auxpassPOS:
                if 'VB' in auxpassPOS:                       
                    fout.write('Future Passive Simple')   
                elif 'VBG' in auxpassPOS:
                    fout.write('Future Passive Progressive')                  
                elif 'VBN' in auxpassPOS:
                    fout.write('Future Passive Perfect')                        
                else:
                    fout.write('Fail to label 1') 
            else:
                fout.write('Fail to label 7')                 
        elif MD_begoingto:
            if 'VB' in auxpassPOS:                       
                fout.write('Future Passive Simple')   
            elif 'VBG' in auxpassPOS:
                fout.write('Future Passive Progressive')                  
            elif 'VBN' in auxpassPOS:
                fout.write('Future Passive Perfect')  
            else:
                fout.write('Fail to label 6')                 
        else:
            if 'VBP' in auxpassPOS or 'VBZ' in auxpassPOS or 'VB' in auxpassPOS:
                fout.write('Present Passive Simple') 
            elif 'VBD' in auxpassPOS:
                fout.write('Past Passive Simple') 
            elif 'VBG' in auxpassPOS and ('VBZ' in auxPOS or 'VBP' in auxPOS):
                fout.write('Present Passive Progressive') 
            elif 'VBG' in auxpassPOS and 'VBD' in auxPOS:
                fout.write('Past Passive Progressive') 
            elif 'VBN' in auxpassPOS and ('VBZ' in auxPOS or 'VBP' in auxPOS):
                fout.write('Present Passive Perfect') 
            elif 'VBN' in auxpassPOS and 'VBD' in auxPOS:
                fout.write('Past Passive Perfect')           
            else:
                fout.write('Fail to label 2')    
    else:
        auxPOS=LookDepPOS(SenPOS,rootstring,'aux(',senbuffer,Sennum)                
        if 'MD' in auxPOS :
            if auxPOS['MD'].lower() in ['can','ca','does','may','must','do','dare','need','ought']:
                #print(Sennum,auxPOS,end='')
                if SenPOS[rootindex] in ['VB']:
                    fout.write('Present Active Simple')
                elif SenPOS[rootindex] in ['VBG']:
                    fout.write('Present Active Progressive')
                else:
                    fout.write('VB -> NN')
            elif auxPOS['MD'].lower() in ['would','did','could','might','should','\'d']:
                #print(Sennum,auxPOS,end='')
                if SenPOS[rootindex] in ['VB']:
                    fout.write('Past Active Simple')
                elif SenPOS[rootindex] in ['VBG']:
                    fout.write('Past Active Progressive')
                else:
                    fout.write('VB -> NN')                    
            elif auxPOS['MD'].lower() in ['will','\'ll','wo','shall','shalt','wilt']:
                if SenPOS[rootindex] in ['VB']:
                    fout.write('Future Active Simple')
                elif SenPOS[rootindex] in ['VBG']:              
                    fout.write('Future Active Progressive')
                elif SenPOS[rootindex] in ['VBN']:                 
                    fout.write('Future Active Perfect')
                else:
                    fout.write('Fail to label 3') 
            else:
                print(Sennum,auxPOS,end='')
                fout.write('Fail to label 8') 
        elif MD_begoingto:
            if SenPOS[rootindex] in ['VB']:
                fout.write('Future Active Simple')
            elif SenPOS[rootindex] in ['VBG']:              
                fout.write('Future Active Progressive')
            elif SenPOS[rootindex] in ['VBN']:                 
                fout.write('Future Active Perfect')  
            else:
                fout.write('Fail to label 5')                  
        else:
            if SenPOS[rootindex] in ['VBP','VBZ','VB']:
                if 'does' in auxPOS.values() or 'do' in auxPOS.values() or 'did' in auxPOS.values():#does do did每次雌性都被判定錯QQ
                    fout.write('Fail to label 9')
                else:
                    fout.write('Present Active Simple')
            elif SenPOS[rootindex] in ['VBD']:
                fout.write('Past Active Simple')
            elif SenPOS[rootindex] in ['VBG'] and ('VBZ' in auxPOS or 'VBP' in auxPOS):
                fout.write('Present Active Progressive')
            elif SenPOS[rootindex] in ['VBG'] and 'VBD' in auxPOS:
                fout.write('Past Active Progressive')
            elif SenPOS[rootindex] in ['VBN'] and ('VBZ' in auxPOS or 'VBP' in auxPOS):
                fout.write('Present Active Perfect')
            elif SenPOS[rootindex] in ['VBN'] and 'VBD' in auxPOS:                 
                fout.write('Past Active Perfect')
            else:
                fout.write('Fail to label 4') 
            
    fout.write(']    ')
    return rootstring
        #if len(LookDepPOS(SenPOS,rootstring,'advcl(',senbuffer,Sennum))!=0:
        #    rootstring=RootCorrect(rootstring,'advcl(',senbuffer,Sennum)
        #    Tense(SenPOS,POStype,rootstring,senbuffer,Sennum,fout)
        
verbPOS=["VBZ","VBP","VB","VBG","VBD","VBN"]
roottype=[0]*40 
POStype=['yee','NN','JJ','NNS','NNP','``','JJS','RB','CC','DT','NNPS','JJR','IN','WRB','CD','MD']
rootnearlation=[]



filename="EBi-MicroblogplusPURE"
#filelist=["EBi-EducationplusPURE","EBi-LawsplusPURE","EBi-MicroblogplusPURE","EBi-NewsplusPURE","EBi-ScienceplusPURE","EBi-SpokenplusPURE"\
#,"EBi-SubtitlesplusPURE","EBi-ThesisplusPURE"]

if __name__ == "__main__":  
    if len(sys.argv) != 2:
        print("""Usage: python3 predict.py sample.in
sample.in:    the input file in the format of the output of Stanford CoreNLP dependency parser
        """)
        quit()
    filein=open(sys.argv[1], "r", encoding="UTF-8")    
    fout = sys.stdout
    fnest = open(os.devnull, 'w')
    part=True  
    buffer=''
    Sennum=0
    while True :
        line=filein.readline()
        if "Sentence #" in line :
            tokennum=int(line.split("(")[1].split(" ")[0])#tatal token number
            Sennum=int(line.strip('Sentence #').split(' ')[0])
            filein.readline()
            SenPOS=[]#all token POS ['PRP', 'VBP', 'NN', 'IN'...]
            senbuffer=[]# all dependcy['nsubj(provide-2, We-1)',...]
            rootnearlation_sen=[]
        elif part==True and line!="\n":#POS,Tree
            if line[:6]=="[Text=":#POS
                SenPOS.append(line.split("PartOfSpeech=")[1].split(' ')[0])
            else:#Tree
                buffer+=line.strip('\n').strip(' ').strip('\t')
        elif part!=True and line!="\n" and line:#Relation
            if line[:11]=='root(ROOT-0':#Root
                pass#rootstring=line.split(',',maxsplit=1)[1].strip(' ').split(')')[0]
                #print(rootstring,end="----->\n")
            else:#all denpendcy
                senbuffer.append(line[:-1])
        elif line=="\n" or not line:
            if part==True:
                #if Sennum==789:
                pass
            else:
                #print(SenPOS)  
                fout.write("{:<7}".format(str(Sennum)))
                #print(Sennum)   
                BuildTree(buffer,SenPOS,POStype,senbuffer,Sennum,fout)
                
                fout.write('\n')
                buffer=''            
                #20160201#Tense(SenPOS,POStype,rootstring,senbuffer,Sennum,fout)
            part=~part
        if not line:
            break            
    filein.close()
    fout.close()
    fnest.close()                
