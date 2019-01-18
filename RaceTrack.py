import sys
import time
from Tkinter import *
import tkMessageBox
import math


class RaceTrackDialog(Frame):

    def __init__(self):
        self.parent = Tk()

        Frame.__init__(self, self.parent)
        self.create_widgets()
        self.parent.mainloop()

    def create_widgets(self):

        DEFAULTtrackwidth ="3"
        self.returnval=[-1, 0]

        self.parent.bind("<Return>", self.enterpressed)
        self.parent.title("Racetrack Parameters")
        self.grid()

        l1 = Label(self, text="Please enter the width (in passes) of the racetrack: ")
        l1.grid(columnspan=10)
        
        self.trackwidth = StringVar(self)
        self.trackwidth.set(DEFAULTtrackwidth)
        self.sb = Spinbox(self, from_=1, to=10, width = 3, textvariable=self.trackwidth)
        self.sb.grid( row=0, column= 10, padx=5, pady=5 )

        l2 = Label(self, text="Expand pattern by 1/2 track width on each side: ")
        l2.grid(columnspan=10, sticky=W, row=1)

        self.broaden = StringVar(self)
        self.broaden.set("broaden")
        self.c = Checkbutton(self, text="", variable=self.broaden, onvalue="broaden", offvalue="leave"        )
        self.c.grid( row=1, column= 10, padx=5, pady=5 )
        
               
        self.okbutton = Button(self, text="OK", command=self.ok, state="active", height = 1, width = 8)
        self.okbutton.grid(padx=5, pady=5, sticky=E, column=9, columnspan=2)
        self.okbutton.focus_set()
        
    def enterpressed (self,event):
        self.ok()

    def ok(self):
        if self.broaden.get() == "broaden":
            self.returnval[1] = 1
        t = self.trackwidth.get()
        if t.isdigit():
            self.returnval[0] = int ( t )
            if self.returnval[0] > 0:   # if correct value successfully found
                self.parent.destroy()   # quit this dialog box
                return()                
        tkMessageBox.showerror("Error", "That is not a valid number")

# creates an error dialog with a custom message
def infoDialog(message):
    root = Tk()
    root.withdraw()
    tkMessageBox.showinfo("Info", message)
    root.destroy()

# creates an error dialog with a custom message
def errorDialog(message):
    root = Tk()
    root.withdraw()
    tkMessageBox.showerror("Error", message)
    root.destroy()

# functions for vector calculations
def vectAdd(v1,v2):
    res = list(v1)
    for i in range( len(v1) ):
        res[i] = v1[i] + v2[i]
    return res

def vectDiff(v1,v2):
    res = list(v1)
    for i in range( len(v1) ):
        res[i] = v1[i] - v2[i]
    return res

def vectDot(v1,v2):
    res = 0
    for i in range( len(v1) ):
        res += v1[i] + v2[i]
    return res

def vectNorm(v):
    res = 0
    for i in range( len(v) ):
        res += v[i] * v[i]
    return math.sqrt(res)

def vectScalar(v, s):
    res = list(v)
    for i in range( len(v) ):
        res[i] = v[i] * s
    return res

# extends a zigzag search pattern by num waypoints
def extendPattern(wplist, num):
    # this method performs no consistency checking
    for i in range (num):
        # duplicate the last waypoint
        wplist.append( list(wplist[-1]) ) # we need to use the list constructor otherwise we just copy by reference
        # move the coordinates of the new waypoint 1 pass further
        wplist[-1][8] = '{:-.6f}'.format( float(wplist[-2][8]) - float(wplist[-5][8]) + float(wplist[-2][8]) )        
        wplist[-1][9] = '{:-.6f}'.format( float(wplist[-2][9]) - float(wplist[-5][9]) + float(wplist[-2][9]) ) 
        wplist[-1][0] = 'new'  # designate WP as new

        # duplicate the second to last waypoint
        wplist.append( list(wplist[-3]) )  # we need to use the list constructor otherwise we just copy by reference
        # move the coordinates of the new waypoint 1 pass further
        wplist[-1][8] = '{:-.6f}'.format( float(wplist[-4][8]) - float(wplist[-5][8]) + float(wplist[-4][8]) )        
        wplist[-1][9] = '{:-.6f}'.format( float(wplist[-4][9]) - float(wplist[-5][9]) + float(wplist[-4][9]) ) 
        wplist[-1][0] = 'new'  # designate WP as new

# extends a list of zigzag search patterns by the appropriate number of waypoints
def extendPatterns(navwpts, trackwidth):
    revint  = 2 * trackwidth +1          # the number of passes after which the pattern reverses
    
    for area in range( len(navwpts) -1 ):# loop through all scan areas but the last one, which is a placeholder
        # check for consistency
        numnavs = len( navwpts[area] )
        if numnavs % 2 == 1:         	# if there is an odd number of waypoints in the area
            errorDialog('Scan area %d has odd number of waypoints ' % a)
            return False                        # exit the method
        if numnavs < 4:                     # if the area contains less than 4 waypoints 
            errorDialog('Scan area %d has too few waypoints ' % a)
            return False                        # exit the method

        # determine by how much the pattern needs to be extended
        numpasses = numnavs / 2
        if numpasses % revint == 0:
            goalpasses = numpasses
        else:
            goalpasses = (numpasses/revint) * revint + revint

        #extend the pattern
        extendPattern(navwpts[area], goalpasses - numpasses)
    return True

# shuffles waypoints to produce a sliding racetrack pattern
def zigzag2racetrack(navwpts, trackwidth):
    revint  = 2 * trackwidth +1          # the number of passes after which the pattern reverses

    for area in range( len(navwpts) -1 ):# loop through all scan areas but the last one, which is a placeholder
        #print navwpts
        templist = []
        for scanpass in range( len(navwpts[area]) /2 ):

            # determine the correct source pass
            sourcepass = (scanpass / revint) * revint + (scanpass % revint) /2
            if (scanpass % revint) %2 == 1:
                sourcepass += trackwidth + 1
            #print scanpass
            #print sourcepass

            # append the two waypoints from the source pass in the correct order
            if (scanpass %2) + (sourcepass %2) == 1:
                #print 'flip'
                templist.append( navwpts[area][sourcepass *2 + 1] )
                templist.append( navwpts[area][sourcepass *2    ] )
            else:
                #print 'nonflip'
                templist.append( navwpts[area][sourcepass *2    ] )
                templist.append( navwpts[area][sourcepass *2 + 1] )
            #print templist
        navwpts[area] = templist

# lengthen the track, so turning occurs outside of the scan area
def lengthenTrack(navwpts, trackwidth):
    for area in range( len(navwpts) -1 ):# loop through all scan areas but the last one, which is a placeholder

        # get the coordinates of 3 significant waypoints
        p0 = [ float(navwpts[area][0][8]), float(navwpts[area][0][9]) ]
        p1 = [ float(navwpts[area][1][8]), float(navwpts[area][1][9]) ]
        p2 = [ float(navwpts[area][2][8]), float(navwpts[area][2][9]) ]
        
        # get a unit vector in the direction of the passes 
        dirP = vectDiff(p1, p0)
        dirP = vectScalar( dirP, 1/vectNorm(dirP) )
        
        # find the drift (perpendicular) direction
        #print p0[0]
        c = math.cos( p0[0] / 180 * math.pi )   # the factor needed to euclidize
        dirPe = [ dirP[0], dirP[1] * c ]        # euclidize the pass direction
        dirDe = [ - dirPe[1], dirPe[0] ]        # find the normal vector
        dirD  = [ dirDe[0], dirDe[1] / c ]      # re-skew the vector to lat and long

        # find the point along the drift direction coming from p2 and crossing the pass line
        sP = dirP[1] / dirP[0]                      # the slope in pass direction
        sD = dirD[1] / dirD[0]                      # the slope in drift direction
        q = [ 0.0, 0.0 ]                            # initialize the crossing point
        q[0] = ( p2[1] - p0[1] + p0[0]*sP - p2[0]*sD ) / (   sP -   sD ) # x-component of the crossing point
        q[1] = ( p2[0] - p0[0] + p0[1]/sP - p2[1]/sD ) / ( 1/sP - 1/sD ) # y-component of the crossing point
        #print q

        # measure the distance and apply it to the pass direction
        lD = vectDiff(p2,q)                          # the distance between passes
        lP = [ - lD[1] * c, lD[0] /c ]               # turn it 90 degrees
        dist = vectNorm( lP )
        
        # offset the beginnings and end
        offset = vectScalar( dirP, dist * trackwidth /2.0 )
        for wpt in range( len(navwpts[area]) ):
            if ( (wpt + 1) /2 ) % 2 == 0:
                navwpts[area][wpt][8] = '{:-.6f}'.format( float(navwpts[area][wpt][8]) - offset[0] )        
                navwpts[area][wpt][9] = '{:-.6f}'.format( float(navwpts[area][wpt][9]) - offset[1] )
            else:
                navwpts[area][wpt][8] = '{:-.6f}'.format( float(navwpts[area][wpt][8]) + offset[0] )        
                navwpts[area][wpt][9] = '{:-.6f}'.format( float(navwpts[area][wpt][9]) + offset[1] )
                
# recombines the waypoint lists into a new mission string
def recombineMission(inbetween, navwpts, anomalies):
    line = inbetween[0].pop(0)[0]         # get the header string
    counter = 0
    for a in range( len(navwpts) ):

        for l in range( len(inbetween[a]) ):
            line = line + '%d' % counter                # this overwrites the old waypoint number
            counter += 1
            #line = line + inbetween[a][l][0]
            for v in range( 1, len(inbetween[a][l] )):
                line = line + '\t' + inbetween[a][l][v]

        for l in range( 1, len(navwpts[a]) ):
            line = line + '%d' % counter                # this overwrites the old waypoint number
            counter += 1
            #line = line + navwpts[a][l][0]
            for v in range( 1, len(navwpts[a][l] )):
                line = line + '\t' + navwpts[a][l][v]

        for l in range( len(anomalies[a]) ):
            line = line + '%d' % counter                # this overwrites the old waypoint number
            counter += 1
            #line = line + anomalies[a][l][0]
            for v in range( 1, len(anomalies[a][l] )):
                line = line + '\t' + anomalies[a][l][v]
    return line
		
def clearLists(l1,l2,l3):
    l1 = []
    l2 = []
    l3 = []

def addArea (inbetween, navwpts, anomalies, areaNum ):
    inbetween.append([])                    # add a new empty area to parse lists
    anomalies.append([])
    navwpts.append  ([])
    navwpts[areaNum].append ([])            # create a placeholder for the first racetrack wpt


def parseMission( mission, inbetween, navwpts, anomalies ):
    if mission[0][0].rstrip() != 'QGC WPL 110': 
        errorDialog("The file does not have the right format!")
        return False
    area = 0
    recording = False
    clearLists (inbetween, navwpts, anomalies)  # clear the parse lists
    addArea (inbetween, navwpts, anomalies, 0)  # add a new empty area to parse lists
    inbetween[0].append(mission[0])             # put the header as the first element of the first inbetween section  

    for i in range( 1, len(mission) ):      # go through each line of the mission (except the header)
        if mission[i][3] == '206':              # check if this line turns the camera on or off
            if float( mission[i][4] )== 0:          # if camera gets shut off
                recording = False                       # set recording flag to False
                area += 1                               # advance area counter
                inbetween.append([])                    # add a new empty area to parse lists
                anomalies.append([])
                navwpts.append  ([])
                navwpts[area].append ([])               # create a placeholder for the first racetrack wpt
                inbetween[area].append (mission[i])     # add the 'camera off' command to the new 'inbetween' area
            else:                                   # if camera gets turned on
                recording = True                        # set recording flag to True
                inbetween[area].append (mission[i])     # add the 'camera on' command to the 'inbetween' area

        elif recording:                         # while recording
            if mission[i][3] == '16':               # if this command is a nav waypoint
                navwpts[area].append(mission[i])        # add it to the current scan area
            else:                                   # if it is not a nav waypoint
                if len(navwpts[area]) == 1:             # but we have not yet reached the 2nd wpt in the scan area
                    inbetween[area].append (mission[i])     # add the command to the 'inbetween' area
                else:                                   # if it is a non-nav command within the the scan area
                    anomalies[area].append(mission[i])      # add the command to the 'anomalies' area
                    infoDialog('Unexpected command in wpt ' + mission[i][0] + '.\nIt will be added to the end of the scan area.' )
        
        else:                                   # while not recording
            inbetween[area].append (mission[i])     # add the command to the 'inbetween' area
            if mission[i][3] == '16':               # if this command is a nav waypoint 
                navwpts[area][0] = (mission[i])         # also overwrite the first wpt of the current scan area

    if recording:                            # if the camera is not turned off by the end of the mission
        errorDialog("The camera does not shut off after the mission!")
        return False
    return True
    
                

# ==================== Main Program ========================

if len(sys.argv) == 1: # no parameter given
    errorDialog("You need to drag and drop a Mission Planner \nwaypoint file onto this program!")
    sys.exit()

# open the main dialog
params = RaceTrackDialog()
if params.returnval[0] == -1:   # the dialog box was cancelled
    sys.exit()

sourcefilename = str(sys.argv[1])
trackwidth     = params.returnval [0]
extend         = params.returnval [1]
inbetween = []
navwpts   = []
anomalies = []
s = []

# read the file into an array
f = open(sourcefilename, 'r')
for line in f:
    s.append(line.split('\t'))
f.close()

# parse Strings into lists
if parseMission( s, inbetween, navwpts, anomalies ) == False:
    sys.exit()
#print 'all parsed!'

# extend the scan areas as needed
if extend == 1:
    if extendPatterns( navwpts, trackwidth ) == False:
        sys.exit()
#print 'scan areas extended'

# move waypoints outward to make sure the plane flies straight over the scan area
lengthenTrack( navwpts, trackwidth )

# shuffle waypionts to produce sliding racetrack pattern
zigzag2racetrack( navwpts, trackwidth )

# recombine all into a new mission string
line = recombineMission(inbetween, navwpts, anomalies)

# write the result to a file
filenameblocks = sourcefilename.rsplit('.',1)

filename = filenameblocks[0] + "_Racetrack.txt"
f = open(filename, "w")
f.write(line)
f.close()

