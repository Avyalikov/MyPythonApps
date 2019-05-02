import xml.etree.cElementTree as ET
import os
width = 1280
height = 1085
blinkingObjectCoef = 2
allow = 10

class Coord:
    def __init__(self, xp, yp, xs, ys):
        self.xp = xp
        self.yp = yp
        self.xs = xs
        self.ys = ys

def checkOutborder(frame, coord):
    #horizontal
    if coord.xp + coord.xs > width + allow or coord.xp + coord.xs < -allow or coord.xp < -allow:
        print('Error oX, frame: ', frame.attrib['frame'])
    #vertical
    if coord.yp + coord.ys > height + allow or coord.yp + coord.ys < -allow or coord.yp < -allow:
        print('Error oY, frame: ', frame.attrib['frame'])
      
def start():
    
    filename = os.path.abspath(os.curdir).split('\\')[len(os.path.abspath(os.curdir).split('\\')) - 1] + '.xml'
    tree = ET.ElementTree(file=filename)
    root =  tree.getroot()

    keyFrames = 0
    interpolationFrames = 0
    
    sourcesLight = {}
    isEvenFrameNum = -1

    sourcesOfLight = root.find('Source_of_Light')
    #for every source of light
    for sLight in sourcesOfLight:
        #object id
        #print(sLight.text)

        #for every timestamp
        for tStamp in sLight:
            if tStamp.tag != 'timestamps':
                continue
            #deleted object
            if len(tStamp) == 0:
                break
            prevFrame = tStamp[0]
            firstObjectFrame = 1
            for frame in tStamp:
                #print(frame.attrib.keys())
                coordFrame = Coord(float(frame[0][0][2][0].text),
                                   float(frame[0][0][2][1].text),
                                   float(frame[0][0][2][3].text),
                                   float(frame[0][0][2][4].text))
                coordPrevFrame = Coord(float(prevFrame[0][0][2][0].text),
                                   float(prevFrame[0][0][2][1].text),
                                   float(prevFrame[0][0][2][3].text),
                                   float(prevFrame[0][0][2][4].text))
                
                checkOutborder(frame, coordFrame)

                frameCost = 1.0
                
                if isEvenFrameNum == -1:
                    isEvenFrameNum = int(frame.attrib['frame']) %2
                    
                #delta size/position this & previous frame
                if firstObjectFrame != 1:
                    delta = abs(coordPrevFrame.xp - coordFrame.xp) + abs(coordPrevFrame.yp - coordFrame.yp) + abs(coordPrevFrame.xs - coordFrame.xs) + abs(coordPrevFrame.ys - coordFrame.ys) 
                    if delta < 3:
                        frameCost *= delta * 0.3 + 0.1
                    
                    #only light frames
                    if int(frame.attrib['frame']) %2 == isEvenFrameNum:
                        if int(frame.attrib['frame']) - int(prevFrame.attrib['frame']) > 2:
                            frameCost += blinkingObjectCoef
                        prevFrame = frame

                if firstObjectFrame == 1:
                    frameCost += blinkingObjectCoef
                    firstObjectFrame = 0
                
                #lightType_lightId
                objectNum = sLight.tag + '_' + sLight.text.split()[0]
                if sourcesLight.get(objectNum, -1) == -1:
                    #sourcesLight[objectNum] = (count, cost)
                    sourcesLight[objectNum] = (0, 0)
                sourcesLight[objectNum] = (sourcesLight[objectNum][0] + 1, sourcesLight[objectNum][1] + frameCost)

                if frame.attrib.get('interpolationState', -1) == -1:
                    keyFrames += 1
                    continue
                if frame.attrib['interpolationState'] == 'interpolated':
                    interpolationFrames += 1
                    continue
                #interpolation start/end
                keyFrames += 1
               
            
                 
    result = 0
    oldResult = 0
    for obj in sourcesLight.keys():
        print("%s:\t\t%s\t%s"%(obj, sourcesLight[obj][0], sourcesLight[obj][1]))
        result += sourcesLight[obj][1]
        oldResult += sourcesLight[obj][0]
    
    print('Old result:\t', oldResult)
    print('New result:\t', result)
    hours = int(input('Enter hours: '))
    print('Old W/h:', oldResult/hours)
    print('New W/h:', result/hours)
    

if __name__ == '__main__':
    start()
