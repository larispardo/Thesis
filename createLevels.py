import numpy as np

def GetDifficultyParameters(difficulty):
    import math
    maxTreasures = 4
    width = math.floor((gridSize[0] - 18) * difficulty + 4 * np.random.random()) + 5
    height = math.floor((gridSize[1] - 18) * difficulty + 4 * np.random.random()) + 5
    enemyAmount = difficulty + math.floor(np.random.random()*difficulty/2)
    # TODO: replace Magic numbers with resource amount
    resourceAmount = 5 + (5-round(difficulty*np.random.random()))
    treasuresAmount = np.random.randint(maxTreasures)
    return width, height, enemyAmount, resourceAmount, treasuresAmount
'''
def CreateLevel(grid, width, height, enemies, resources, treasures):
    global onlyOne, levelMap
    import math
    levelm = levelMap.copy()
    del levelm['wall']
    if enemies == 0:
        for keys in levelMap.keys():
            if 'enemy' in keys:
                del levelm[keys]
    if resources == 0:
        del levelm['resource']
    if treasures == 0:
        del levelm['treasure']

    level = []
    vertMid = math.floor(grid[0]/2)-1
    horMid = math.floor(grid[1]/2)-1
    realVMid = math.floor(height/2)
    realHMid = math.floor(width/2)
    totenemies = 0
    totresources = 0
    tottreasures = 0
    vertPlayArea = (vertMid - realVMid, vertMid + (height - realVMid))
    horPlayArea = (horMid - realHMid, horMid + (width - realHMid))
    # TODO: Change this to make the random variable be dependent on position instead of the list of keys
    #  Use range 10
    for row in range(grid[0]):
        if row <= vertPlayArea[0] or row > vertPlayArea[1]:
            level += [levelMap['wall']]*grid[1]+['\n']
            continue
        for col in range(grid[1]):
            if col <= horPlayArea[0] or col > horPlayArea[1]:
                level += [levelMap['wall']]
            else:
                key = np.random.choice(list(levelm.keys()), size=1)[0]
                level += [levelm[key]]
                if key in onlyOne:
                    del levelm[key]
                elif 'enemy' in key:
                    totenemies += 1
                    if totenemies == enemies:
                        for keys in levelMap.keys():
                            if 'enemy' in keys:
                                del levelm[keys]
                elif 'resource' in key:
                    totresources += 1
                    if totresources == resources:
                        del levelm[key]
                elif 'treasure' in key:
                    tottreasures += 1
                    if tottreasures == treasures:
                        del levelm[key]
        level += ['\n']
    return level
'''

def CreateLevel(grid, width, height, enemies, resources, treasures):
    global onlyOne, levelMap
    import math
    levelm = levelMap.copy()
    del levelm['wall']
    del levelm['floor']
    goPositions = []
    level = []
    vertMid = math.floor(grid[0]/2)
    horMid = math.floor(grid[1]/2)
    realVMid = math.floor(height/2)
    realHMid = math.floor(width/2)
    vertPlayArea = (vertMid - realVMid, vertMid + (height - realVMid))
    horPlayArea = (horMid - realHMid, horMid + (width - realHMid))
    # TODO: Change this to make the random variable be dependent on position instead of the list of keys
    #  Use range 10
    for row in range(grid[0]):
        if row < vertPlayArea[0] or row >= vertPlayArea[1]:
            level += [levelMap['wall']]*grid[1]+['\n']
            continue
        for col in range(grid[1]):
            if col < horPlayArea[0] or col >= horPlayArea[1]:
                level += [levelMap['wall']]
            else:
                level += [levelMap['floor']]
        level += ['\n']
    vertical = list(range(vertPlayArea[0], vertPlayArea[1]))
    horizontal = list(range(horPlayArea[0], horPlayArea[1]))
    avPos = GetPositions(1, vertical, horizontal, goPositions, level, ['avatar'])
    goPositions += avPos
    goalPos = GetPositions(1, vertical, horizontal, goPositions, level, ['goal'])
    goPositions += goalPos
    enPos = GetPositions(enemies, vertical, horizontal, goPositions, level, ['enemy'])
    goPositions += enPos
    trPos = GetPositions(treasures, vertical, horizontal, goPositions, level, ['treasure'])
    goPositions += trPos
    rePos = GetPositions(resources, vertical, horizontal, goPositions, level, ['resource'])
    goPositions += rePos
    return level

def GetPositions(amount, vpos, hpos, goPos, level, keyVals):
    global gridSize, levelMap
    # TODO: now is not impossible to get all values in same line blocking avatar if all are enemies.
    vertPos = np.random.choice(vpos, size=amount)
    horPos = np.random.choice(hpos, size=amount)
    positions = [(x, y) for x, y in zip(vertPos, horPos)]
    while True:
        counter = 0
        for i in range(len(positions)):
            pos = positions[i]
            tmpPositions = positions.copy()
            tmpPositions.remove(pos)
            if pos in goPos or pos in tmpPositions:
                vtmp = np.random.choice(vpos, size=1)[0]
                htmp = np.random.choice(hpos, size=1)[0]
                positions[i] = (vtmp, htmp)
            else:
                counter += 1
        if counter == len(positions):
            break
    for pos in positions:
        i = pos[0] * (gridSize[0]+1) + pos[1]
        val = np.random.choice(keyVals, size=1)[0]
        level[i] = levelMap[val]
    return positions


def WriteLevel(level, game="thesis0", lvl = 0):
    file = game + "_lvl" + str(lvl) + ".txt"
    f = open(file, "w+")
    f.write(''.join(level))
    f.close()


levelMap = {'goal': 'g',
            'enemy': '1',
            'enemy1': '1',
            'enemy2': '2',
            'enemy3': '3',
            'resource': '4',
            'treasure': '5',
            'avatar': 'A',
            'wall': 'w',
            'floor': '.'}

gridSize = (20, 20)
onlyOne = ['avatar', 'goal']
width, height, enemyAmount, resourceAmount, treasuresAmount = GetDifficultyParameters(5)
level = CreateLevel(gridSize, width, height, enemyAmount, resourceAmount, treasuresAmount)
WriteLevel(level, lvl=4)

