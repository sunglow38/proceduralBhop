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
    themes = []
    if tFile: ##TODO: Let user choose to use a file containing a theme on each line
        for line in open(tFile):
            themes.append(line.rstrip())
    themeChoice = random.choice(themes)
    return themeChoice


def pickSegment(theme):
    segListDir = r'stages\segment_stages\\'
    segListDir += theme
    segList = os.listdir(segListDir)
    segList = filter(reStage.match, segList)
    segList = list(segList)

    segStage = random.choice(segList)

    return segStage

print(pickTheme('themes.txt'))

