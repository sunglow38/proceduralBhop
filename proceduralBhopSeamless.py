import os
import random
import re
import sys

import vdf

import bhopStageGen

reStage = re.compile(r'.*?.vmf')

def getRandomStage(stage):
    stageDir = sys.argv[1]
    stageDir += '\\' + stage
    stageDir = os.listdir(stageDir)
    stageDir = filter(reStage.match, stageDir)
    stageDir = list(stageDir)

    stageRandom = random.choice(stageDir)

    return stageRandom

def getInitial():
    stagePath = sys.argv[1] + '\\initial\\' + getRandomStage('initial')
    print(stagePath)
    return(stagePath)

def getSegment():
    stagePath = sys.argv[1] + '\\segment\\' + getRandomStage('segment')
    return stagePath

def getFinal():
    stagePath = sys.argv[1] + '\\final\\' + getRandomStage('final')
    return stagePath

parentStage = bhopStageGen.Stage(getInitial())

for i in range(int(sys.argv[2]) - 2):
    childStage = bhopStageGen.Stage(getSegment())
    childStage = parentStage.prepare_next(childStage)
    parentStage = parentStage.append_stage(childStage)

finalStage = bhopStageGen.Stage(getFinal())
finalStage = parentStage.prepare_next(finalStage)
parentStage  = parentStage.append_stage(finalStage)


vdf.dump(parentStage, open(r'stages\output\output.vmf', 'w'), pretty=True)
