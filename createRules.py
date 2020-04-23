import numpy as np
import createLevels
import os
import math
import sys

'''
    TODO: Check the amount of enemies when creating them, they can have different attributes depending 
    on their class. 
'''

spriteSet = {'floor': 'floor > Immovable img=newset/floor2 hidden=True',
             'sword': 'sword > OrientedFlicker limit=5 singleton=True img=oryx/slash1',
             # Limit refers how long it stays in game.
             'avatar': 'avatar  > ',
             'enemy': 'enemy > ',
             'resource': 'resource > Resource limit=',
             'treasure': 'treasure > Immovable ',
             'wall': 'wall > Immovable img=oryx/wall3 autotiling=True',
             'goal': 'goal  > Immovable '}
enemies = {'enemy1': 'enemy1 > ',
           'enemy2': 'enemy2 > ',
           'enemy3': 'enemy3 > '}

levelMap = {'goal': 'g > floor goal',
            'enemy': '1 > floor enemy',
            'enemy1': '1 > floor enemy1',
            'enemy2': '2 > floor enemy2',
            'enemy3': '3 > floor enemy3',
            'resource': '4 > floor resource',
            'treasure': '5 > floor treasure',
            'avatar': 'A > floor avatar',
            'wall': 'w > wall',
            'floor': '. > floor'}

interactionSet = {'avwa': 'avatar wall > stepBack',
                  'swen': 'enemy sword > killSprite scoreChange=2',
                  'enen': 'enemy enemy > stepBack',  # Need to check what is the best way to
                  # handle this section for multiple enemies.
                  'aven': 'avatar enemy > killSprite scoreChange=-1',
                  'trav': 'treasure avatar > killSprite scoreChange=1',
                  'enwa': 'enemy wall > stepBack',
                  'enwaA': 'enemy wall > reverseDirection',
                  'avre': 'resource avatar > collectResource  scoreChange=2',
                  'avgo': 'goal avatar  > killSprite scoreChange=2',
                  'avgoR': 'goal avatar  > killIfOtherHasMore resource=resource limit='}

terminationSet = {'goal': 'SpriteCounter stype=goal    limit=0 win=True',
                  'enemy': 'SpriteCounter stype=enemy limit=0  win=True',
                  'avatar': 'SpriteCounter stype=avatar win=False'}

sections = ['SpriteSet', 'LevelMapping', 'InteractionSet', 'TerminationSet']


def SelectGame(games):
    ## uniformly random chooses a game from the options
    return np.random.choice(games, size=1)[0]


def ChooseAmountEnemies(maximum=2, diff=0):
    import math
    print(diff)
    return min(maximum, math.floor(np.random.random() * diff)) + 1


def AddCheckpoint():
    global gameSprites, gameInteractions
    if np.random.random() < probExtra:
        del spriteSet['checkpoint']
    else:
        gameSprites += ['checkpoint']
        gameInteractions += ['chav']


def AddAvatarType(avType):
    global spriteSet, avatarTypes
    ty = np.random.choice(avType, size=1)[0]
    spriteSet['avatar'] = spriteSet['avatar'] + avatarTypes[ty] + ' '


'''def CheckParameters(ty):
    if ty == 'Missile':
        parameter = 'orientation=' + np.random.choice(orientations, size=1)[0] + \
                    ' speed=' + str(np.random.choice(speeds, size=1)[0])
    elif ty == 'RandomNPC':
        parameter = 'cooldown=' + str(np.random.choice(coolDown, size=1)[0])
    else:
        parameter = ''
    return parameter'''

'''def AddEnemies(amount, enTypes, proba = None):
    global spriteSet, enemies, spriteTypes, possibleSlimeSprites, gameInteractions
    # TODO: check this section and add behavior for when the enemies need cool down and amount > 2
    space = '  '
    identations = 3
    if amount == 1:
        if len(enTypes) == 1:
            ty = spriteTypes[enTypes[0]]
        else:
            ty = np.random.choice(enTypes, size=1, p=proba)[0]
            ty = spriteTypes[ty]
        parameter = CheckParameters(ty)
        spriteSet['enemy'] = spriteSet['enemy'] + ty + ' ' + parameter + ' '
    else:
        gameInteractions += ['enen']
        possibleSlimeSprites.remove('enemy')
        for i in range(1,amount+1):
            spriteSet['enemy'] += '\n' + space * identations
            enemy = 'enemy'+str(i)
            if len(enTypes) == 1:
                ty = spriteTypes[enTypes[0]]
            else:
                ty = np.random.choice(enTypes, size=1, p=proba)[0]
                ty = spriteTypes[ty]
            parameter = CheckParameters(ty)
            spriteSet['enemy'] += enemies[enemy] + ty + ' ' + parameter + ' ' + 'img=' + sprites.pop()'''


def SelectEnemyTypes(types, amount):
    global isGoal, isMissile, difficulty, gameInteractions  # using it as global variable.
    slowCool = 8  # From easier to most difficult
    fastCool = 2
    minSpeed = 0.1
    maxSpeed = 0.2
    orientations = ['LEFT', 'RIGHT']
    gametypes = []
    typeVariables = []
    if difficulty == 0 and isGoal:
        return [types[0]], [[None]]
    for i in range(amount):
        ty = np.random.choice(types, size=1)[0]  # Currently uniform distributed
        gametypes.append(ty)
        if ty == 'Immovable':
            types.remove(ty)
            typeVariables += [[None]]
        elif ty == 'RandomNPC':
            cooldown = round(slowCool - min(slowCool - fastCool, np.random.random() * difficulty * 2), 3)
            typeVariables += [[('cooldown', cooldown)]]
            key = 'enwa' + str(i + 1)
            interactionSet[key] = 'enemy' + str(i + 1) + ' wall > stepBack'
            gameInteractions += [key]

        elif ty == 'Missile':  # Now redundant, but could help to keep track of all variable types.
            speedScale = 30
            speed = round(minSpeed + min(maxSpeed - minSpeed, np.random.random() / speedScale * difficulty), 3)
            orientation = np.random.choice(orientations, size=1)[0]
            typeVariables += [[('orientation', orientation), ('speed', speed)]]
            isMissile = True
            key = 'enwa' + str(i + 1)
            interactionSet[key] = 'enemy' + str(i + 1) + ' wall > reverseDirection'
            gameInteractions += [key]
    return gametypes, typeVariables


def SetResource():
    global difficulty, maxDifficulty
    import math
    minResources = 3
    goalResources = minResources + math.floor(np.random.random() * difficulty)
    limitResources = goalResources + math.floor(np.random.random() * (maxDifficulty - difficulty) +
                                                minResources * (maxDifficulty - difficulty))
    return limitResources, goalResources


def createRules():
    global differentEnemies, avatarType, enemyTy, enemyVar, gameSprites, \
        gameTerminations, gameInteractions, possibleSlimeSprites
    space = '  '
    rules = ''
    for section in sections:
        rules += space + section + '\n'
        if section == 'SpriteSet':
            for value in gameSprites:
                isEnemy = False
                if value == 'avatar':
                    if avatarType != 'ShootAvatar':
                        spriteSet[value] += 'ShootAvatar' + ' stype=sword '
                    else:
                        if 'swen' not in gameInteractions:
                            spriteSet[value] += avatarType + ' stype=sword '
                            gameInteractions += ['swen']
                elif value == 'enemy':
                    isEnemy = True
                    rules += space * 2 + spriteSet[value] + '\n'
                print(value, possibleSlimeSprites, value in possibleSlimeSprites)
                if (value in possibleSlimeSprites) and not isEnemy:
                    rules += space * 2 + spriteSet[value] + 'img=' + sprites.pop() + '\n'
                elif isEnemy:
                    for i in range(1, differentEnemies + 1):
                        if enemyVar[i - 1][0] is not None:
                            print("HERE: " + enemyTy[i - 1])
                            variables = [x[0] + '=' + str(x[1]) for x in enemyVar[i - 1]]
                            variables = ' '.join(variables)
                            rules += space * 3 + enemies[value + str(i)] + enemyTy[i - 1] + ' ' + variables \
                                     + ' ' + 'img=' + sprites.pop() + '\n'
                        else:
                            rules += space * 3 + enemies[value + str(i)] + enemyTy[i - 1] + ' ' \
                                     + 'img=' + sprites.pop() + '\n'
                else:
                    rules += space * 2 + spriteSet[value] + '\n'
        elif section == 'LevelMapping':
            for value in gameSprites:
                if value == 'sword':
                    continue
                if value == 'enemy':
                    for i in range(1, differentEnemies + 1):
                        rules += space * 2 + levelMap[value + str(i)] + '\n'
                else:
                    rules += space * 2 + levelMap[value] + '\n'
        if section == 'InteractionSet':
            for value in gameInteractions:
                rules += space * 2 + interactionSet[value] + '\n'
        if section == 'TerminationSet':
            for value in gameTerminations:
                rules += space * 2 + terminationSet[value] + '\n'
    return rules


def WriteRules(file, rules, path=""):
    print(differentEnemies)

    f = open(path + file + '.txt', "w+")
    f.write('BasicGame\n')
    f.write(rules)
    f.close()


maxDifficulty = 5
difficulty = 5
gameNumber = 7
probabilityTreasures = 0.1
probabilityGoal = 0.8
probResourceGGoal = 0.2

# Could we make this general? I say yes, just make sure the general structure is saved.
sprites = ['oryx/slime1', 'oryx/slime2', 'oryx/slime3', 'oryx/slime4', 'oryx/slime5', 'oryx/slime6']
indices = np.arange(len(sprites))
np.random.shuffle(indices)
sprites = [sprites[i] for i in indices]
avatarTypes = ['ShootAvatar', 'MovingAvatar']
gameSprites = ['floor', 'wall', 'enemy', 'avatar']
gameInteractions = ['avwa', 'aven']
enemyTypes = ['Immovable', 'RandomNPC', 'Missile']
# counter = [2, 4, 8]  # Counter in randomnpc class.
possibleSlimeSprites = ['avatar', 'enemy', 'goal', 'treasure', 'resource']
specialTypeSprites = ['avatar', 'enemy']
gameTerminations = ['avatar']
gameSprites += ['sword']

isGoal = False
isResource = False
isMissile = False
isTreasure = False
if np.random.random() < probabilityGoal:
    isGoal = True
    gameSprites += ['goal']
    gameTerminations += ['goal']
    if np.random.random() < probResourceGGoal:  # total probability of 0.16
        isResource = True
        gameSprites += ['resource']
        limitR, goalR = SetResource()
        spriteSet['resource'] += str(limitR) + ' '
        interactionSet['avgoR'] += str(goalR)
        gameInteractions += ['avre', 'avgoR']
    else:
        gameInteractions += ['avgo']
else:
    gameTerminations += ['enemy']  # TODO: Make this also have a probability of exist in certain difficulties.
    #tmpAvatarTy = avatarTypes.copy()
    avatarTypes.remove('MovingAvatar')

if np.random.random() < probabilityTreasures:
    isTreasure = True
    gameSprites += ['treasure']
    gameInteractions += ['trav']

differentEnemies = ChooseAmountEnemies(diff=difficulty)
if differentEnemies > 1:
    gameInteractions += ['enen']
# spriteWithTypes = ['avatar']
# spriteWithTypes += ['enemy'+str(i+1) for i in range(differentEnemies)]

# TODO: think what is better to be the avatar type when increasing difficulty

avatarType = np.random.choice(avatarTypes, size=1)[0]

enemyTy, enemyVar = SelectEnemyTypes(enemyTypes, differentEnemies)
# goTypes += enemyTy
rules = createRules()

gameName = 'thesis0' + str(gameNumber)
version = 0
if sys.platform.startswith('win'):
    gamesPath = 'C:\\Users\\Lenovo\\Envs\\thesis1\\Lib\\site-packages\\gym_gvgai\\envs\\games\\'
else:
    gamesPath = "/Users/larispardo/Downloads/GVGAI_GYM/gym_gvgai/envs/games/"
path01 = gamesPath + gameName + "_v" + str(version) + "/"
path02 = gamesPath + gameName + "_v" + str(version + 1) + "/"

# Create target directory & all intermediate directories if don't exists
try:
    os.makedirs(path01)
    print("Directory ", path01, " Created ")
except FileExistsError:
    print("Directory ", path01, " already exists")
try:
    os.makedirs(path02)
    print("Directory ", path02, " Created ")
except FileExistsError:
    print("Directory ", path02, " already exists")
WriteRules(gameName, rules, path=path01)
WriteRules(gameName, rules, path=path02)

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

enemyTy = ['enemy' + str(i + 1) for i in range(differentEnemies)]
gridSize = (20, 20)
version = 0
for i in range(10):
    width, height, enemyAmount, resourceAmount, treasuresAmount = createLevels.GetDifficultyParameters(math.ceil(i / 2),
                                                                                                       gridSize=gridSize,
                                                                                                       isGoal=isGoal)
    level = createLevels.CreateLevel(gridSize, width, height, enemyAmount, resourceAmount,
                                     treasuresAmount, levelMap=levelMap, gridSize=gridSize,
                                     enemyTypes=enemyTy, isGoal=isGoal, isResource=isResource, isTreasure=isTreasure)
    if i % 5 == 0:
        version += 1
    if version == 1:
        createLevels.WriteLevel(level, game=gameName, lvl=i % 5, path=path01)
    else:
        createLevels.WriteLevel(level, game=gameName, lvl=i % 5, path=path02)
