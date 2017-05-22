def getparms(contents, chara):
    parameter=[chara]
    while contents[chara] != ',' :
        if contents[chara] == '>':
            return parameter
        chara +=1
    chara+=1
    parameter.append('')
    while 1:
        if contents[chara] == ',':
            parameter.append('')
            chara+=1
        elif contents[chara] == '>':
            parameter[0]=chara+1
            return parameter
        else:
            parameter[-1]+=contents[chara]
            chara+=1

def lockedahead(loc, doors, direction):
    lockedahead=1
    for i in doors:
        if int(i[0])==loc[0]:
            if int(i[1])==loc[1]:
                if int(i[2])==direction:
                    if int(i[3])==0:
                        lockedahead=0
    return lockedahead

def getunlockindex(loc, doors, direction):
    for i in doors:
        if int(i[0])==loc[0]:
            if int(i[1])==loc[1]:
                if int(i[2])==direction:
                    if int(i[3])==1:
                        return i

def lookfloor(loc, items):
    itemsfound=[]
    for i in items:
        if int(i[0])==loc[0]:
            if int(i[1])==loc[1]:
                itemsfound.append(i[2])
    return itemsfound                  

def pickuponeitem(loc, items, oneitem):
    for i in items:
        if int(i[0])==loc[0]:
            if int(i[1])==loc[1]:
                if i[2]==oneitem:
                    return i                  

def getroomdata(loc, roomdata, direction):
    for i in roomdata:
        if int(i[0])==loc[0]:
            if int(i[1])==loc[1]:
                if int(i[2])==direction:
                    rdata=[i[3],i[4],i[5],i[6]]
                    return rdata                  

def compass(direction):
    if direction==0:
        return 'north'
    if direction==1:
        return 'east'
    if direction==2:
        return 'south'
    if direction==3:
        return 'west'
    

def readroomfile(self, filename='sampledungeon.txt'):
    print 'opening ', filename
    f = open(filename, 'r+')
    contents = f.read() #+ '                                '
    self.filecontents=contents
    f.close()
    print 'file starts: ', contents[0:40]
    chara=0
    while 1:
        while (contents[chara] != '<') :
            chara +=1
        chara+=1
        if contents[chara] == 'l':   #current location
            thing=getparms(contents, chara)
            chara=thing[0]
            self.loc=[int(thing[1]), int(thing[2])]
        if contents[chara] == 'i':   #inventory
            thing=getparms(contents, chara)
            chara=thing[0]
            self.inventory = thing[1:]
        if contents[chara] == 'u':  #current objects
            thing=getparms(contents, chara)
            chara=thing[0]
            self.items=[]
            i=0
            while i*3+3 < len(thing):
                self.items.append(thing[i*3+1:i*3+4])
                i+=1
        if contents[chara] == 'v':  #reset objects
            thing=getparms(contents, chara)
            chara=thing[0]
        if contents[chara] == 'd':   #current doors
            thing=getparms(contents, chara)
            chara=thing[0]
            self.doors=[]
            i=0
            while i*4+4 < len(thing):
                self.doors.append(thing[i*4+1:i*4+5])
                i+=1
        if contents[chara] == 'e':    #restart doors
            thing=getparms(contents, chara)
            chara=thing[0]
        if contents[chara] == 's':    #restart room
            thing=getparms(contents, chara)
            chara=thing[0]
        if contents[chara] == 'r':    #room details
            thing=getparms(contents, chara)
            chara=thing[0]
            self.roomdata.append(thing[1:])
        if contents[chara] == 'e':    #end file
            self.printtobuf( 'On the floor is'+ str(lookfloor(self.loc, self.items))+'\n\n')
            self.filecontents = contents[:chara-2]
            break

def starthere(self,kbin):
    if 1==1:      #only to maintain indents
        rdat=getroomdata(self.loc, self.roomdata, self.direction)
        if kbin[0] == 'f':
            if lockedahead(self.loc, self.doors, self.direction)==0:
                self.printtobuf ('you move forward')
                if self.direction==0:
                     self.loc[1]+=1
                if self.direction==1:
                    self.loc[0]+=1
                if self.direction==2:
                    if self.loc[1]>0:
                        self.loc[1]-=1
                if self.direction==3:
                    if self.loc[0]>0:
                        self.loc[0]-=1
            else:
                if rdat:
                    self.printtobuf (rdat[2])
                else:
                    self.printtobuf ('You cannot move forward, the way ahead is blocked')
              

        if kbin[0] =='l':
            self.direction-=1
            if self.direction<0:
                self.direction=3
        if kbin[0] =='r':
            self.direction+=1
            if self.direction>3:
                self.direction=0
        if kbin[0] =='p':
            pickedsomething=0
            for i in lookfloor(self.loc, self.items):
                if kbin[2:]==i:
                    self.printtobuf ('picked up '+ i)
                    self.items.remove(pickuponeitem(self.loc, self.items, kbin[2:]))
                    self.inventory.append(kbin[2:])
                    pickedsomething=1
                    self.printtobuf ('Your backpack contains '+ str(self.inventory))
            if pickedsomething==0:
                self.printtobuf ('there is no '+ kbin[2:]+ ' here')
        if kbin[0] =='b':
            self.printtobuf ('Your backpack contains '+ str(self.inventory))
     
        if kbin[0] =='d':
            if (kbin[2:]) in self.inventory:
                self.inventory.remove(kbin[2:])
                self.printtobuf ('Your backpack contains '+ str(self.inventory))
                self.items.append([self.loc[0], self.loc[1], kbin[2:]])
            else:
                self.printtobuf ('You do not have '+ kbin[2:]+ 'in your backpack')

        if kbin[0] =='u':
            if (kbin[2:]) in self.inventory:
                if rdat:
                    if rdat[0] != kbin[2:]:
                        self.printtobuf ('You cannot use '+ kbin[2:]+ ' here')
                    else:
                        unlockindex=getunlockindex(self.loc, self.doors, self.direction)
                        if unlockindex:
                            self.doors.remove(unlockindex)
                            self.doors.append([self.loc[0],self.loc[1],self.direction,0])
                else:
                    self.printtobuf ('You cannot use '+ kbin[2:]+ 'here')
            else:
                self.printtobuf ('You do not have '+ kbin[2:]+ ' in your backpack')

        if kbin[0] =='h':
            self.printtobuf ('h - help')
            self.printtobuf ('f - forward')
            self.printtobuf ('r - right')
            self.printtobuf ('l - left')
            self.printtobuf ('b - list backpack contents')
            self.printtobuf ('p item - pick up item')
            self.printtobuf ('d item - drop item')
            self.printtobuf ('u item - use item\n')
        
      
            
        if kbin!='':
            rdat=getroomdata(self.loc, self.roomdata, self.direction)
            self.printtobuf ('You are in a dimly lit cavern facing '+ compass(self.direction))
            self.printtobuf ('On the floor is'+ str(lookfloor(self.loc, self.items)))
            if lockedahead(self.loc, self.doors, self.direction)==0:
                if rdat:
                    self.printtobuf (rdat[1])
                else:self.printtobuf ('the way ahead is open')
            else:
                if rdat:
                    self.printtobuf (rdat[2])
                else:
                    self.printtobuf ('You cannot move forward, the way ahead is blocked')
              


  

