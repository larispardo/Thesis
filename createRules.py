import numpy as np
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
            'treasure': '5 > floor check',
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

terminationSet = {'goal':'SpriteCounter stype=goal    limit=0 win=True',
                  'enemy':'SpriteCounter stype=enemy limit=0  win=True',
                  'avatar':'SpriteCounter stype=avatar win=False'}


sections = ['SpriteSet', 'LevelMapping', 'InteractionSet', 'TerminationSet']

def SelectGame(games):
    ## uniformly random chooses a game from the options
    return np.random.choice(games, size=1)[0]


def ChooseAmountEnemies(maximum = 2, diff = 0):
    import math
    return min(maximum, math.floor(np.random.random() * diff)) + 1


def AddCheckpoint():
    global  gameSprites, gameInteractions
    if (np.random.random() < probExtra):
        del spriteSet['checkpoint']
    else:
        gameSprites += ['checkpoint']
        gameInteractions += ['chav']


def AddAvatarType(avType):
    global spriteSet, avatarTypes
    ty = np.random.choice(avType, size=1)[0]
    spriteSet['avatar'] = spriteSet['avatar']+avatarTypes[ty]+ ' '


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
            cooldown = slowCool - min(slowCool-fastCool, round(np.random.random() * difficulty * 2))
            typeVariables += [[('cooldown', cooldown)]]
        elif ty == 'Missile':  # Now redundant, but could help to keep track of all variable types.
            speedScale = 30
            speed = minSpeed + min(maxSpeed - minSpeed, round(np.random.random()/speedScale * difficulty,3))
            orientation = np.random.choice(orientations, size=1)[0]
            typeVariables += [[('orientation', orientation), ('speed', speed)]]
            isMissile = True
            gameInteractions += ['enwaA']
    return gametypes, typeVariables

def SetResource():
    global difficulty, maxDifficulty
    import math
    minResources = 3
    goalResources = minResources + math.floor(np.random.random()*difficulty)
    limitResources = goalResources + math.floor(np.random.random()*(maxDifficulty-difficulty))
    return limitResources, goalResources

def WriteRules(file="thesis0.txt"):
    global differentEnemies, avatarType, enemyTy, enemyVar, gameSprites, \
        gameTerminations, gameInteractions, possibleSlimeSprites
    print(differentEnemies)
    space = '  '
    f = open(file, "w+")
    f.write('BasicGame\n')
    for section in sections:
        f.write(space+section+'\n')
        if section == 'SpriteSet':
            for value in gameSprites:
                isEnemy = False
                if value == 'avatar':
                    if avatarType != 'ShootAvatar':
                        spriteSet[value] += avatarType + ' '
                    else:
                        spriteSet[value] += avatarType + ' stype=sword '
                        gameInteractions += ['swen']
                elif value == 'enemy':
                    isEnemy = True
                    f.write(space*2+spriteSet[value]+'\n')
                print(value, possibleSlimeSprites, value in possibleSlimeSprites)
                if (value in possibleSlimeSprites) and not isEnemy:
                    f.write(space*2+spriteSet[value]+'img='+sprites.pop()+'\n')
                elif isEnemy:
                    for i in range(1,differentEnemies+1):
                        if enemyVar[i-1][0] is not None:
                            print("HERE: " + enemyTy[i-1])
                            variables = [x[0] + '=' + str(x[1]) for x in enemyVar[i-1]]
                            variables = ' '.join(variables)
                            f.write(space * 3 + enemies[value+str(i)]+ enemyTy[i-1] + ' ' + variables
                                    + ' ' + 'img=' + sprites.pop() + '\n')
                        else:
                            f.write(space * 3 + enemies[value + str(i)] + enemyTy[i-1] + ' '
                                    + 'img=' + sprites.pop() + '\n')
                else:
                    f.write(space * 2 + spriteSet[value]+'\n')
        if section == 'LevelMapping':
            for value in gameSprites:
                if value == 'sword':
                    continue
                if value == 'enemy':
                    for i in range(1,differentEnemies+1):
                        f.write(space * 2 + levelMap[value+str(i)] + '\n')
                else:
                    f.write(space * 2 + levelMap[value]+'\n')
        if section == 'InteractionSet':
            for value in gameInteractions:
                f.write(space * 2 + interactionSet[value]+'\n')
        if section == 'TerminationSet':
            for value in gameTerminations:
                f.write(space * 2 + terminationSet[value]+'\n')
    f.close()



# Could we make this general? I say yes, just make sure the general structure is saved.
sprites = ['oryx/slime1', 'oryx/slime2', 'oryx/slime3', 'oryx/slime4', 'oryx/slime5', 'oryx/slime6']
indices = np.arange(len(sprites))
np.random.shuffle(indices)
sprites = [sprites[i] for i in indices]
avatarTypes = ['ShootAvatar', 'MovingAvatar']
gameSprites = ['floor', 'wall', 'enemy', 'avatar']
gameInteractions = ['avwa', 'aven', 'enwa']
enemyTypes = ['Immovable', 'RandomNPC', 'Missile']
# counter = [2, 4, 8]  # Counter in randomnpc class.
possibleSlimeSprites = ['avatar', 'enemy', 'goal', 'checkpoint', 'resource']
specialTypeSprites = ['avatar', 'enemy']
gameTerminations = ['avatar']

isGoal = False
isResource = False
isMissile = False

maxDifficulty = 5
difficulty = 4
probabilityTreasures = 0.1
probabilityGoal = 0.8
probResourceGGoal = 0.2
if np.random.random() < probabilityGoal:
    isGoal = True
    gameSprites += ['goal']
    gameTerminations += ['goal']
    if np.random.random() < probResourceGGoal: # total probability of 0.16
        isResource = True
        gameSprites += ['resource']
        limitR, goalR = SetResource()
        spriteSet['resource'] += str(limitR)
        interactionSet['avgoR'] += str(goalR)
        gameInteractions += ['avre', 'avgoR']
    else:
        gameInteractions += ['avgo']
else:
    gameTerminations += ['enemy'] # TODO: Make this also have a probability of exist in certain difficulties.

if np.random.random() < probabilityTreasures:
    gameSprites += ['treasure']
    gameInteractions += ['trav']

differentEnemies = ChooseAmountEnemies(diff=difficulty)
if differentEnemies > 1:
    gameInteractions += ['enen']
#spriteWithTypes = ['avatar']
#spriteWithTypes += ['enemy'+str(i+1) for i in range(differentEnemies)]

# TODO: think what is better to be the avatar type when increasing difficulty
avatarType = np.random.choice(avatarTypes, size=1)[0]

enemyTy, enemyVar = SelectEnemyTypes(enemyTypes, differentEnemies)
#goTypes += enemyTy

'''gameTypes = ['moveGoal', 'kill', 'avoid', 'harvest']


game = SelectGame(gameTypes)
# Only optional choice is to have Checkpoint
optionalSets = ['checkpoint']
probExtra = 0.9

if game == 'moveGoal':
    print(game)
    gameTerminations = ['goal', 'avatar']
    gameSprites += ['goal']
    gameInteractions += ['avgo']
    AddCheckpoint()
    possibleEnemyTypes = [1,2]
    probabilityEnemyTypes = [0.9,0.1]
    possibleAvatarTypes = [0]  # probably set avatar > than 1 possible case
    amountEnemies = ChooseAmountEnemies(maximum=2, prob=[0.8, 0.2])
    AddAvatarType(possibleAvatarTypes)
    AddEnemies(amountEnemies, possibleEnemyTypes)
    del spriteSet['resource']
    del spriteSet['sword']
elif game == 'avoid':
    print(game)
    gameTerminations = ['goal', 'avatar']
    gameSprites += ['goal']
    gameInteractions += ['avgo', 'enwaA']
    gameInteractions.remove('enwa')
    AddCheckpoint()
    possibleEnemyTypes = [0]
    possibleAvatarTypes = [0]
    amountEnemies = ChooseAmountEnemies(maximum=2, prob=[0.1, 0.9])

    AddAvatarType(possibleAvatarTypes)
    AddEnemies(amountEnemies, possibleEnemyTypes)
    del spriteSet['resource']
    del spriteSet['sword']
elif game == 'harvest':
    print(game)
    gameTerminations = ['goal', 'avatar']
    gameSprites += ['goal', 'resource']
    gameInteractions += ['avre', 'avgoR']
    possibleEnemyTypes = [1] # only immovable
    possibleAvatarTypes = [0]
    amountEnemies = 1

    AddAvatarType(possibleAvatarTypes)
    AddEnemies(amountEnemies, possibleEnemyTypes)
    del spriteSet['sword']
    del spriteSet['checkpoint']
elif game == 'kill':
    print(game)
    gameTerminations = ['enemy', 'avatar']
    gameSprites += ['sword']
    gameInteractions += ['swen']
    AddCheckpoint()
    possibleEnemyTypes = [2]  # only random
    possibleAvatarTypes = [1]
    amountEnemies = ChooseAmountEnemies()

    AddAvatarType(possibleAvatarTypes)
    AddEnemies(amountEnemies, possibleEnemyTypes)
    del spriteSet['goal']
    del spriteSet['resource']'''

WriteRules()

