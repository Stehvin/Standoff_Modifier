import math
import re

import boothSetupInfo


def execute(booth, points, sdChange, oldPnts):
    """Execute the point conversion program."""
    # Get parameters from excel document.
    nozUtool = boothSetupInfo.boothInfo(booth)[0]
    eulAng = boothSetupInfo.boothInfo(booth)[2]

    # Convert booth strings into actual booth numbers (e.g. '2a' -> 2).
    regexNum = re.compile('[0-9]+')
    try:
        booth = int(regexNum.search(booth).group(0))
    except:
        pass

    # Iterate through points, modifying each one.
    newPnts = dict(oldPnts)
    for pntNum in points:
        pnt = oldPnts[pntNum]

        # Retrieve current UTool and UFrame setpoints.
        pntUtool = boothSetupInfo.curUtool(booth, pnt['ut'])
        pntUframe = boothSetupInfo.curUframe(booth, pnt['uf'])
        
        # Convert point from Uframe to world frame.
        pnt = frame_to_world(pnt, pntUframe)

        # Convert point from original Utool to nozzle Utool and convert
        # angles to UGO (Universal Gun Orientation) angles.
        pnt = utool_to_world(pnt, pntUtool)
        pnt = world_to_utool(pnt, nozUtool)
        pnt = UGO(pnt, eulAng)
        
        # Change standoff distance.
        newPnts[pntNum] = changeSD(pnt, sdChange)
        
        # Convert new point angles from UGO angles to faceplate angles.
        newPnts[pntNum] = unUGO(newPnts[pntNum], eulAng)

        # Convert new nozzle Utool point back to original Utool.
        newPnts[pntNum] = utool_to_world(newPnts[pntNum], nozUtool)
        newPnts[pntNum] = world_to_utool(newPnts[pntNum], pntUtool)

        # Convert new point from world frame to Uframe.
        newPnts[pntNum] = world_to_frame(newPnts[pntNum], pntUframe)
    return dict(newPnts)


def eul2Mat(w, p, r):
    """Converts Euler angles to 3x3 rotation matrix."""
    # Initialize matrix.
    M = [[0, 0, 0], 
         [0, 0, 0], 
         [0, 0, 0]]
    
    # Convert Euler angles from degrees to radians.
    w = math.radians(w)
    p = math.radians(p)
    r = math.radians(r)

    # Calculate matrix elements.
    M[0][0] = math.cos(p) * math.cos(r)
    M[0][1] = (math.sin(w) * math.sin(p) * math.cos(r)) - \
          (math.cos(w) * math.sin(r))
    M[0][2] = (math.sin(w) * math.sin(r)) + \
          (math.cos(w) * math.sin(p) * math.cos(r))
    M[1][0] = math.cos(p) * math.sin(r)
    M[1][1] = (math.cos(w) * math.cos(r)) + \
          (math.sin(w) * math.sin(p) * math.sin(r))
    M[1][2] = (math.cos(w) * math.sin(p) * math.sin(r)) - \
          (math.sin(w) * math.cos(r))
    M[2][0] = -math.sin(p)
    M[2][1] = math.sin(w) * math.cos(p)
    M[2][2] = math.cos(w) * math.cos(p)
    return M


def mat2Eul(M):
    """Converts 3x3 rotation matrix to Euler angles."""
    r = math.degrees(math.atan2(M[1][0], M[0][0]))
    p = math.degrees(-math.asin(M[2][0]))
    w = math.degrees(math.atan2(M[2][1], M[2][2]))
    return w, p, r


def rotMatInv(M):
    """Inverts the 3x3 rotation matrix 'M'.
    The inverse of a rotation matrix is its transpose.
    """
    # initialize output matrix
    MI = [[0, 0, 0],
          [0, 0, 0],
          [0, 0, 0]]

    # calculate matrix elements
    MI[0][0] = M[0][0]
    MI[0][1] = M[1][0]
    MI[0][2] = M[2][0]
    MI[1][0] = M[0][1]
    MI[1][1] = M[1][1]
    MI[1][2] = M[2][1]
    MI[2][0] = M[0][2]
    MI[2][1] = M[1][2]
    MI[2][2] = M[2][2]
    return MI


def rotTransMat(rotM, translation):
    """Turns a rotation matrix and a translation vector into a 4x4
    rotation and translation matrix.
    """
    # Create output matrix.
    M = [[rotM[0][0], rotM[0][1], rotM[0][2], translation['x']],
         [rotM[1][0], rotM[1][1], rotM[1][2], translation['y']],
         [rotM[2][0], rotM[2][1], rotM[2][2], translation['z']],
         [0, 0, 0, 1]]
    return M


def rot_matrix_4x4(rotM):
    """Changes a 3x3 rotation matrix into a 4x4 matrix."""
    # create output matrix
    M = [[rotM[0][0], rotM[0][1], rotM[0][2], 0],
         [rotM[1][0], rotM[1][1], rotM[1][2], 0],
         [rotM[2][0], rotM[2][1], rotM[2][2], 0],
         [0, 0, 0, 1]]
    return M


def multMatVec(M, vector):
    """Multiplies a 4x4 matrix and a 4x1 vector."""
    # Initialize output vector.
    vector1 = {'x': 0, 'y': 0, 'z': 0}
    
    # Calculate vector elements.
    vector1['x'] = ((M[0][0]*vector['x']) + (M[0][1]*vector['y'])
                    + (M[0][2]*vector['z']) + M[0][3])
    vector1['y'] = ((M[1][0]*vector['x']) + (M[1][1]*vector['y'])
                    + (M[1][2]*vector['z']) + M[1][3])
    vector1['z'] = ((M[2][0]*vector['x']) + (M[2][1]*vector['y'])
                    + (M[2][2]*vector['z']) + M[2][3])
    return vector1


def matMult(A, B):
    """Multiplies matricies A and B (A*B = C).
    Full disclosure, I did not write this function. Taken from:
    https://stackoverflow.com/questions/10508021/matrix-multiplication-
    in-python
    """
    zip_b = zip(*B)
    zip_b = list(zip_b)
    return [[sum(ele_a*ele_b for ele_a, ele_b in zip(
        row_a, col_b)) for col_b in zip_b] for row_a in A]


def frame_to_world(uframePnt, uframe):
    """Converts uframe point to a world frame point."""
    worldPnt = dict(uframePnt)
    
    # Convert xyz values to world frame.
    rotA = eul2Mat(uframe['w'], uframe['p'], uframe['r'])
    four = rotTransMat(rotA, uframe)
    vec = multMatVec(four, uframePnt)
    worldPnt['x'], worldPnt['y'], worldPnt['z'] = vec['x'], vec['y'], vec['z']

    # Convert wpr angles to world frame angles.
    rotB = eul2Mat(uframePnt['w'], uframePnt['p'], uframePnt['r'])
    worldPnt['w'], worldPnt['p'], worldPnt['r'] = mat2Eul(matMult(rotA, rotB))
    return worldPnt


def world_to_frame(worldPnt, uframe):
    """Converts a world point to a user frame point."""
    ufPnt = dict(worldPnt)
    
    # Set up translation matrix (Uframe setpoints).
    transM = [[1, 0, 0, -uframe['x']], 
              [0, 1, 0, -uframe['y']], 
              [0, 0, 1, -uframe['z']],
              [0, 0, 0, 1]]
        
    # Convert xyz values to Uframe.
    rotA3 = rotMatInv(eul2Mat(uframe['w'], uframe['p'], uframe['r']))
    rotA4 = rot_matrix_4x4(rotA3)
    M = matMult(rotA4, transM)
    vec = multMatVec(M, worldPnt)
    ufPnt['x'], ufPnt['y'], ufPnt['z'] = vec['x'], vec['y'], vec['z']

    # Convert wpr angles to Uframe.
    rotB = eul2Mat(worldPnt['w'], worldPnt['p'], worldPnt['r'])
    ufPnt['w'], ufPnt['p'], ufPnt['r'] = mat2Eul(matMult(rotA3, rotB))
    return ufPnt        


def world_to_utool(worldPnt, utool):
    """Converts a world frame point to a Utool point."""
    utoolPnt = dict(worldPnt)
    
    # Set up world-coord matrix and translate by Utool xyz setpoints.
    rotM = eul2Mat(worldPnt['w'], worldPnt['p'], worldPnt['r'])
    M4x4 = rotTransMat(rotM, worldPnt)
    vec = multMatVec(M4x4, utool)
    utoolPnt['x'], utoolPnt['y'], utoolPnt['z'] = vec['x'], vec['y'], vec['z']

    # Change world-coord angles to Utool angles.
    rotA = eul2Mat(worldPnt['w'], worldPnt['p'], worldPnt['r'])
    rotB = eul2Mat(utool['w'], utool['p'], utool['r'])
    utoolPnt['w'], utoolPnt['p'], utoolPnt['r'] = mat2Eul(matMult(rotA, rotB))
    return utoolPnt


def utool_to_world(utoolPnt, utool):
    """Converts a Utool point to a world coordinate point."""
    utoolCopy = dict(utool)
    worldPnt = dict(utoolPnt)

    # Change Utool angles to world angles.
    rotA = eul2Mat(utoolPnt['w'], utoolPnt['p'], utoolPnt['r'])
    rotB = rotMatInv(eul2Mat(utoolCopy['w'], utoolCopy['p'], utoolCopy['r']))
    utoolPnt['w'], utoolPnt['p'], utoolPnt['r'] = mat2Eul(matMult(rotA, rotB))

    # Reverse Utool setpoint value signs.
    for key in utoolCopy:
        utoolCopy[key] *= -1
    
    # Set up Utool matrix.
    rotM = eul2Mat(utoolPnt['w'], utoolPnt['p'], utoolPnt['r'])
    M4x4 = rotTransMat(rotM, utoolPnt)
    vec = multMatVec(M4x4, utoolCopy)
    worldPnt['x'], worldPnt['y'], worldPnt['z'] = vec['x'], vec['y'], vec['z']
    worldPnt['w'], worldPnt['p'], worldPnt['r'] = (
        utoolPnt['w'], utoolPnt['p'], utoolPnt['r'])
    return worldPnt


def UGO(pnt, Euler):
    """Convert a point's angles to Universal Gun Orientation (UGO)
    angles.
    """
    pnt1 = dict(pnt)
    rotM = matMult(eul2Mat(pnt1['w'], pnt1['p'], pnt1['r']),
                   eul2Mat(Euler['w'], Euler['p'], Euler['r']))
    pnt1['w'], pnt1['p'], pnt1['r'] = mat2Eul(rotM)
    return pnt1


def unUGO(pnt, Euler):
    """Convert a point's angles from Universal Gun Orientation (UGO)
       angles to faceplate angles.
    """
    pnt1 = dict(pnt)
    rotM = matMult(eul2Mat(pnt1['w'], pnt1['p'], pnt1['r']),
                   rotMatInv(eul2Mat(Euler['w'], Euler['p'], Euler['r'])))
    pnt1['w'], pnt1['p'], pnt1['r'] = mat2Eul(rotM)
    return pnt1


def changeSD(oldPnt, sdChange):
    """Change a point's standoff distance. The point has already been
    converted to UGO angles.
    """
    # Copy old point dictionary to a new point dictionary.
    newPnt = dict(oldPnt)

    # Convert UGO angles to a rotation matrix.
    M = eul2Mat(newPnt['w'], newPnt['p'], newPnt['r'])
    
    # Multiply unit vector [0, 0, 1] and rotation matrix to get X-Y-Z
    # projection points.
    x = M[0][2]
    y = M[1][2]
    z = M[2][2]

    # Find the change in each axis value (math not shown) and subtract
    # it from the original value.
    newPnt['x'] -= (sdChange * 25.4) * x
    newPnt['y'] -= (sdChange * 25.4) * y
    newPnt['z'] -= (sdChange * 25.4) * z
    return newPnt
