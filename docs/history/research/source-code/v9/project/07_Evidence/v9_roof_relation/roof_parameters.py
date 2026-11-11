"""V9 relation geometry in LOCAL metre coordinates; no IO or baseline mutation."""
import math

GATE_BOUNDS = [4.05, -13.02, 9.05, -10.22]
KITCHEN_BOUNDS = [6.98, -12.05, 13.60, -2.15]
GATE_RIDGE_Y = -11.62
KITCHEN_RIDGE_X = 11.515
SHELL_THICKNESS = .075
KITCHEN_FOOTPRINT = [
    [6.98, -11.28], [8.45, -11.28], [9.05, -12.05],
    [13.60, -12.05], [13.60, -2.15], [6.98, -2.15],
]

def kitchen_ymin(x):
    if x <= 8.45: return -11.28
    if x >= 9.05: return -12.05
    return -11.28 - .77 * (x - 8.45) / .60

def zkitchen(x, y):
    west = -.29889484 + .39953197*x - .00177447*y
    east = 9.41247826 - .440834917*x + .00312578606*y
    return min(west, east) - .050 + .080*max(0, (7.2-x)/.22)**2

def zgate(x, y):
    t=abs((x-6.55)/2.55)
    v=abs((y+11.62)/1.40)
    return 4.35 - .58*v**1.6 + .30*t**6 + .40*t**5*v**3

def in_kitchen(x, y, margin=0):
    return (6.98+margin <= x <= 13.60-margin
            and kitchen_ymin(x)+margin <= y <= -2.15-margin)

# Wood roof underlap: it ends in front of the gate support wall, while
# remaining hidden below the gate front overhang. The gate roof high edge
# and kitchen visible drip direction are separate; this is not a valley.
UNDERLAP_POLYGON = [[6.98,-11.28],[8.45,-11.28],[9.05,-12.05],
                    [9.05,-10.22],[6.98,-10.22]]
JOINT_TERMINATION_LINE = [[6.98,-11.28],[8.45,-11.28],[9.05,-12.05]]

