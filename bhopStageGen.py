import re

import numpy as np
import vdf


def translatePlane(data, xyz):
    '''translatePlane(plane, vertex array)
        Takes an array in the format of a Vertex (X Y Z) and adds it to a Plane'''
    # regexPlane = re.compile(r"""
    #                             (\d+\.?\d*)\s #X [Group 0]
    #                             (\d+\.?\d*)\s #Y [Group 1]
    #                             (\d+\.?\d*) #Z [Group 2]
    #                             """, re.VERBOSE)
    stripParenth = re.compile(r"\((.*?)\)")
    vertex = stripParenth.findall(data) #The first character in string is skipped to check whether its a plane or origin object
    if vertex:
        for i in range(0, len(vertex)):
            coord = vertex[i]
            coord = coord.split(' ')
            coord = np.array(
                list(map(float, coord)))
            coord = coord + xyz
            coord = map(str, coord)
            coord = ' '.join(coord)
            coord = re.sub(
                r".*", r'(\g<0>)', coord)
            vertex[i] = coord
        vertex = ' '.join(vertex)

    return vertex

def translateOrigin(data, xyz):
    coord = data.split(' ')
    coord = np.array(
        list(map(float, coord)))
    coord = coord + xyz
    coord = map(str, coord)
    coord = ' '.join(coord)
    return coord

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
                            entryOrigin = np.array(list(map(float, entryOrigin)))
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
                            exitOrigin = np.array(list(map(float, exitOrigin)))
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
        delta = self.exitOrigin() - stageNext.entranceOrigin()
        stageWorld = Stage(self['world'])
        stageIDs = stageWorld.idMax()
        #Solid and Side ID's start at the max of the previous stage so that each ID is unique
        idCount = 0

        del stageNext[stageNext.entranceIndex(), 'entity']

        if hasattr(stageNext, 'iteritems'):
            solidIdx = 0
            sideIdx = 0
            entityIdx = 0
            for i, j in stageNext.iteritems():
                if i == 'world':
                    for k, n in j.iteritems():
                        if k == 'solid':
                            idCount += 1
                            for m, x in n.iteritems():
                                if m == 'side':
                                    idCount += 1
                                    for p, v in zip(x.iterkeys(), x.itervalues()):
                                        if p == 'plane':
                                            newPlane = translatePlane(v, delta)
                                    del stageNext['world'][solidIdx, 'solid'][sideIdx, 'side']['id']
                                    stageNext['world'][solidIdx, 'solid'][sideIdx, 'side']['id'] = stageIDs + 1 + idCount
                                    del stageNext['world'][solidIdx,'solid'][sideIdx, 'side']['plane']
                                    stageNext['world'][solidIdx,'solid'][sideIdx, 'side']['plane'] = newPlane
                                    sideIdx += 1
                            del stageNext['world'][solidIdx, 'solid']['id']
                            stageNext['world'][solidIdx, 'solid']['id'] = stageIDs + 1 + idCount
                            solidIdx += 1
                            sideIdx = 0

                if i == 'entity':
                    solidIdx = 0
                    sideIdx = 0
                    idCount += 1
                    origin = False
                    for x, n in j.iteritems():
                        if x == 'origin':
                            origin = translateOrigin(n, delta)
                        if x == 'solid':
                            idCount += 1
                            for m, x in n.iteritems():
                                if m == 'side':
                                    idCount += 1
                                    for p, v in zip(x.iterkeys(), x.itervalues()):
                                        if p == 'plane':
                                            newPlane = translatePlane(v, delta)
                                    del stageNext[entityIdx, i][solidIdx, 'solid'][sideIdx, 'side']['id']
                                    stageNext[entityIdx, i][solidIdx, 'solid'][sideIdx, 'side']['id'] = stageIDs + 1 + idCount
                                    del stageNext[entityIdx, i][solidIdx,'solid'][sideIdx, 'side']['plane']
                                    stageNext[entityIdx, i][solidIdx,'solid'][sideIdx, 'side']['plane'] = newPlane
                                    sideIdx += 1
                            del stageNext[entityIdx, i][solidIdx, 'solid']['id']
                            stageNext[entityIdx, i][solidIdx, 'solid']['id'] = stageIDs + 1 + idCount
                            solidIdx += 1
                            sideIdx = 0

                    del stageNext[entityIdx, i]['id']
                    stageNext[entityIdx, i]['id'] = stageIDs + 1 + idCount
                    if origin:
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
