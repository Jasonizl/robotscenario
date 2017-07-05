# robotscenario
## main-scenario
The robot searches for QR-Codes within a closed area (e.g. a room) and can scan these QR-Codes. Scanning a QR-Code will give you a color. The robot has then to find the color in the area and go/walk there. The color will be laid down as a sheet of paper, so the robot has a area big enough to find and stand on.

## What are the steps?
1. Scan area for possible QR-Codes
    1. If not found scan more
2. Walk closer to QR-Code (maybe not needed)
    1. Walk closer to it aslong as you can't scan it correctly
3. Scan QR-Code and get color
4. Search area for wanted color
    1. look through lower camera 
    2. create color palette for every picture and look if it's wanted color
5. walk to area
6. do a pose when standing on area (sitting, idle..)

## Group
QRoboter Group (Frederic, Paul, Henryk, Arno, Milan, Jason)
