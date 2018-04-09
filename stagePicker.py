import os
import random
import re

reStage = re.compile(r'(.+)_(\d+)\.vmf')
stageDir = r'stages\\'
initDir = stageDir + r'initial_stages\\'
segDir = stageDir + r'segment_stages\\'
finDir = stageDir + r'final_stages\\'
outDir = stageDir + r'output_stages\\'


def pickTheme(tFile=None):
    if tFile: ##TODO: Let user choose to use a file containing a theme on each line
        open(r'tFile', 'r')
    else:
        themeList = filter(reStage.match, os.listdir(initDir))
        themeList = list(themeList)

    return themeList


def pickSegment(theme):
    segListDir = r'stages\segment_stages\\'
    segListDir += theme
    segList = os.listdir(segListDir)
    segList = filter(reStage.match, segList)
    segList = list(segList)

    segStage = random.choice(segList)

    return segStage

print(pickTheme())
