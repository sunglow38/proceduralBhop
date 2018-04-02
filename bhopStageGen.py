import re
import time

import numpy as np
import vdf

start_time = time.time()

stage0 = r'stages\stage_001.vmf'
stage1 = r'stages\stage_002.vmf'
stage2 = stage0
stage3 = stage1

class Vertex(obj):
    def __init__(self, data=None):


class Plane(str):
    def __init__(self, data=None):
        super().__init__()

    # def __len__(self):
    #     return len(self.plane)

    def __add__(self, other):
        return

    # def __getitem__(self, idx):
    #     return self.plane[idx]

p = '(-1 0 0) (0 0 0) (0 0 0)'
p2 = '(0 -12 0) (18 43 0) (0 20 30)'
print(Plane(p))

class Stage(vdf.VDFDict):

    def __init__(self, data=None):
        super().__init__()
        if not isinstance(data, vdf.VDFDict):  # checks if data is not already a VDFDict
            data = vdf.parse(open(data), mapper=vdf.VDFDict, merge_duplicate_keys=False)
            self.update(data)
        else:
            self.update(data)

    # returns list of all values for a specified key in the object
    def get_key_recursive(self, key):
        def gen_dict_extract(key, var):
            if hasattr(var, 'iteritems'):
                for k, v in var.iteritems():
                    if k == key:
                        yield v
                    if isinstance(v, dict):
                        for result in gen_dict_extract(key, v):
                            yield result
                    elif isinstance(v, list):
                        for d in v:
                            for result in gen_dict_extract(key, d):
                                yield result
        return list(gen_dict_extract(key, self))

    def entrance(self):
        if hasattr(self, 'iteritems'):
            idx = 0
            for i, j in self.iteritems():
                if i == 'entity':
                    for k in j.itervalues():
                        if k == 'entry':
                            entryOrigin = j['origin'].split(' ')
                            entryOrigin = np.array(list(map(int, entryOrigin)))
                            return{'idx': idx, 'entryOrigin': entryOrigin}
                    idx += 1

    def entranceOrigin(self):
        return self.entrance()['entryOrigin']

    def entranceIndex(self):
        return self.entrance()['idx']

    def exit(self):
        if hasattr(self, 'iteritems'):
            idx = 0
            for i, j in self.iteritems():
                if i == 'entity':
                    for k in j.itervalues():
                        if k == 'exit':
                            exitOrigin = j['origin'].split(' ')
                            exitOrigin = np.array(list(map(int, exitOrigin)))
                            return{'idx': idx, 'exitOrigin': exitOrigin}
                    idx += 1

    def exitOrigin(self):
        return self.exit()['exitOrigin']

    def exitIndex(self):
        return self.exit()['idx']

    def ids(self):
        idList = self.get_key_recursive('id')
        for i in range(len(idList)):
            if isinstance(idList[i], str):
                idList[i] = int(idList[i])
        return idList

    def idLen(self):
        return len(self.ids())

    def idMax(self):
        return max(self.ids())

    # If stageA -> stageB then command would be stageA.prepare_next(stageB)
    def prepare_next(self, stageNext):
        stripParenth = r"\((.*?)\)"
        delta = self.exitOrigin() - stageNext.entranceOrigin()
        stageWorld = Stage(self['world'])
        idCount = stageWorld.idMax()

        del stageNext[self.entranceIndex(), 'entity']

        if hasattr(stageNext, 'iteritems'):
            solidIdx = 0
            sideIdx = 0
            entityIdx = 0
            for i, j in stageNext.iteritems():
                if i == 'world':
                    for k, n in j.iteritems():
                        if k == 'solid':
                            for m, x in n.iteritems():
                                if m == 'side':
                                    for p, v in zip(x.iterkeys(), x.itervalues()):
                                        if p == 'plane':
                                            vertex = re.findall(stripParenth, v)
                                            if vertex:
                                                for i in range(0, len(vertex)):
                                                    coord = vertex[i]
                                                    coord = coord.split(' ')
                                                    coord = np.array(
                                                        list(map(int, coord)))
                                                    coord = coord + delta
                                                    coord = map(str, coord)
                                                    coord = ' '.join(coord)
                                                    coord = re.sub(
                                                        r".*", r'(\g<0>)', coord)
                                                    vertex[i] = coord
                                                vertex = ' '.join(vertex)
                                    del stageNext['world'][solidIdx,'solid'][sideIdx, 'side']['plane']
                                    stageNext['world'][solidIdx,'solid'][sideIdx, 'side']['plane'] = vertex
                                    sideIdx += 1
                            del stageNext['world'][solidIdx, 'solid']['id']
                            stageNext['world'][solidIdx, 'solid']['id'] = idCount + 1 + solidIdx
                            solidIdx += 1
                            sideIdx = 0

                if i == 'entity':
                    for x, n in j.iteritems():
                        if x == 'origin':
                            origin = n.split(' ')
                            origin = np.array(list(map(int, origin)))
                            origin = origin + delta
                            origin = map(str, origin)
                            origin = ' '.join(origin)
                    del stageNext[entityIdx, i]['origin']
                    stageNext[entityIdx, i]['origin'] = origin
                    entityIdx += 1
            del(stageNext['cameras'], stageNext['cordon'], stageNext['visgroups'],
                stageNext['viewsettings'], stageNext['versioninfo'])
            return(stageNext)

    def append_stage(self, stageN):
        """
        Hammer will take multiple World class definitions and merge solids and groups
        Properties are taken from the last instance of a World class
        Thus the newest stages properties will be the main stage properties
        """

        stage = self
        del stage[self.exitIndex(), 'entity']
        stage['world'] = stageN['world']
        for i in stageN.get_all_for('entity'):
            stage['entity'] = i

        return stage



stageMain = Stage(stage0)
stageNext = Stage(stage1)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

stageNext = Stage(stage2)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

stageNext = Stage(stage3)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

open(r'stages\stageGen.vmf', 'w').close()
vdf.dump(stageMain, open(r'stages\stageGen.vmf', 'w'), pretty=True)
print("--- %s seconds ---" % (time.time() - start_time))
