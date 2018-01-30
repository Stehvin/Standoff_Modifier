# Standoff_Modifier
This program modifies the standoff distance for points in a Fanuc 6-axis robot program.

The term "standoff distance" refers to the distance between the end-of-arm tooling and the workpiece. For example, in thermal spray, the standoff distance is the distance between the nozzle of the gun and the part which is being coated. This distance is usually set by a guess-and-check method where the robot is moved a small increment and then the distance is physically measured. Unfortunately, this means that once a standoff distance is chosen for a particular robot program, due to the amount of work required to touch-up every individual point, that standoff distance is essentially set in stone.

This standoff distance modification program enables the user to change the standoff distance of any number of points in a robot program. It works by determining the orientation vector of a given point and calculating a closer or further point along the line of the orientation vector.

## Files
"standoff_modifier.py": This is the main file, which calls the other files and runs the whole program. All necessary user input is entered into this file.

"boothSetupInfo.py": This module retrieves all necessary robot information from the Excel document where it is stored.

"get_points.py": This module retrieves information about the robot points from the input program text file.

"point_converter.py": This module calculates the location and orientation of the new robot points, based on the information given in the above modules.

"write_points.py": This module writes the new robot points into an output text file.

## Notes
This program is designed for Fanuc robots. A similar approach could be used for other types of robots, but some differences must be accounted for that are not included in this code. Specifically, how the program's text file is formatted and the robot's Euler angle convention. 

Additionally, this program was developed for a specific application (thermal spray) and I am using this repository mostly as a backup, so I do not intend modify the code for more general applications. This is also the reason why some variable names may seem unusual to other Fanuc robot users; for example, "booth" and "gun" are application-specific terms.

Finally, for this program to work, some information must be known about each robot's configuration. I use an Excel document that contains this information, which includes: robot utools, uframes, and end-of-arm tooling orientation.