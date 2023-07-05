#imports

#creating dictionary which will have info from pgn file
data = {}

#importing important data from the pgn into dictionary
file = 'crystalizer17-white.pgn'

with open(file, 'r') as f:
    for line in f.readlines():
        if line[:2] == "1.":
            firstMoves = line.split("5.")[0]
            if firstMoves not in data:
                data[firstMoves] = [0,0,0]
            if "1-0" in line[-10:]:
                data[firstMoves][0] += 1
            elif "1/2-1/2" in line[-10:]:
                data[firstMoves][1] += 1
            elif "0-1" in line[-10:]:
                data[firstMoves][2] += 1
            firstMoves = ""
print(data)

for key, value in data.items():
    if value[0] + value[1] + value[2] >= 10:
        print(key + str(value))

        