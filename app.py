import math
for deg in range(0, 181, 30):
    print(deg, round(math.sin(math.radians(deg)), 3))