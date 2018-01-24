import os
import re

import boothSetupInfo


def formatDict(pntsDict):
    """Format points dictionary for proper output to .ls files."""
    for pntNum, pnt in pntsDict.items():
        for coord in pnt:
            if coord not in ['ut', 'uf']:
                formatPnt(pnt, coord)


def formatPnt(pnt, coord):
    """Formats a point for proper output to .ls files."""
    pnt[coord] = round(pnt[coord], 3)
    if pnt[coord] < 1 and pnt[coord] > 0:
        pnt[coord] = format(pnt[coord], '.3f')[1:]
    elif pnt[coord] < 0 and pnt[coord] > -1:
        pnt[coord] = "-" + format(pnt[coord], '.3f')[2:]
    else:
        pnt[coord] = format(pnt[coord], '.3f')


def pointWrite(outfile, line, pntMatch, pntStatusCount, pntsDict,
           newBooth, configStr):
    """Properly format and write each line after a point has been
    discovered.
    """
    # Get the point number.
    pntNum = int(pntMatch.group(1))

    # First three lines can be printed verbatim.
    if pntStatusCount in [0, 1, 2]:
        outfile.write(line)

    # Reformat fourth and fifth lines to paste new point coordinates.
    elif pntStatusCount == 3:
        outfile.write("\t" + "X = {:>9}".format(pntsDict[pntNum]['x'])
                      + "  mm,\t" + "Y = {:>9}".format(pntsDict[pntNum]['y'])
                      + "  mm,\t" + "Z = {:>9}".format(pntsDict[pntNum]['z'])
                      + "  mm,\n")
    elif pntStatusCount == 4:
        outfile.write("\t" + "W = {:>9}".format(pntsDict[pntNum]['w'])
                      + " deg,\t" + "P = {:>9}".format(pntsDict[pntNum]['p'])
                      + " deg,\t" + "R = {:>9}".format(pntsDict[pntNum]['r'])
                      + " deg")
        if newBooth in (1, 2, 13, 16):
            outfile.write(",\n\t" + "E1= {:>9}".format(pntsDict[pntNum]['e1'])
                          + " deg\n")
        else:
            outfile.write("\n")


def writeFile(inputPath, outputPath, pntsDict, newBooth):
    """Write old program to new program file path, using new points
    dictionary.
    """
    # Get new booth's configuration string.
    configStr = boothSetupInfo.boothInfo(newBooth)[5]
    
    # Convert booth string into actual booth number (e.g. '2a' -> '2').
    regexNum = re.compile('[0-9]+')
    try:
        newBooth = int(regexNum.search(newBooth).group(0))
    except:
        pass
    
    # Format point dictionary decimals.
    formatDict(pntsDict)
    
    # Set up regular expression to match point beginning.
    regex_pnt = re.compile('P\[(\d+)(\s?:\s?".*")?\]\s?\{\n')

    # Initialize beginning of point checker to false.
    pntStatus = False

    # Get output file name (without .ls).
    newProgName = os.path.basename(outputPath)[:-3]
    
    # Copy input file to output file.
    with open(inputPath, 'r') as infile:
        with open(outputPath, 'w') as outfile:
            for line in infile:
                
                # Search line for beginning of point.
                pntMatch = regex_pnt.search(line)
                if pntMatch:
                    pntStatus = True
                    pntStatusCount = 0
                    pntMatchCopy = pntMatch
                
                # Search line for end of point.
                elif line == "};\n":
                    pntStatus = False
                
                # Execute pointWrite function if line is within a point.
                if pntStatus:
                    pointWrite(outfile, line, pntMatchCopy, pntStatusCount,
                               pntsDict, newBooth, configStr)
                    pntStatusCount += 1

                # Change program name.
                elif line[0:5] == r"/PROG":
                    outfile.write("/PROG  " + newProgName + "\n")
                else:
                    outfile.write(line)
