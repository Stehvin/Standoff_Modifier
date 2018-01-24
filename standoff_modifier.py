import get_points
import point_converter
import write_points


'''
INPUT INFORMATION
'''

inputPath = r"C:\Users\Example\inTestProg.ls"
outputPath = r"C:\Users\Example\outTestProg.ls"
booth = 6

'''
    Enter the point numbers to be modified as a Python list. Examples:
    points = [1]
    points = [1, 2, 3, 36]
'''

points = [1, 2, 3]

'''
    Enter standoff distance change (in inches). Positive moves the gun
    further away from the part and negative moves the gun closer to the part.
'''

sdChange = 1.00

'''
END OF INPUT INFORMATION
'''


# Get points from input file.
pntsDict = get_points.makePntsDict(inputPath)

# Change points' standoff distance.
pntsDict = point_converter.execute(booth, points, sdChange, pntsDict)

# Write output file with new points.
write_points.writeFile(inputPath, outputPath, pntsDict, booth)
