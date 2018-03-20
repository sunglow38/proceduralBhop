import time
start_time = time.time()

import vdf
import re
import numpy as np

stage0 = r'stages\stage_001.vmf'
stage1 = r'stages\stage_002.vmf'
stage2 = stage0
stage3 = stage1

class Stage(vdf.VDFDict):

    def __init__(self, data=None):    
        if not isinstance(data, vdf.VDFDict): ##checks if data is already a VDFDict
           data = vdf.parse(open(data), mapper=vdf.VDFDict, merge_duplicate_keys=False)
           self.d = vdf.VDFDict(data)
        else: 
            self.d = data

    def __repr__(self):
        return self.d

    def __len__(self):
        return len(self.d)

    def asVDF(self): #returns Stage(obj) call as a VDFDict type rather than a Stage type 
        return self.d

    def get_key_recursive(self, key): #returns list of all values for a specified key in the object
        def gen_dict_extract(key, var):
            if hasattr(var,'iteritems'):
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
        return list(gen_dict_extract(key, self.d))

    def entrance(self):
        if hasattr(self.d, 'iteritems'):
            idx = 0
            for i, j in self.d.iteritems():
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
        if hasattr(self.d, 'iteritems'):
            idx = 0
            for i, j in self.d.iteritems():
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

    def prepare_next(self, stageNext): #If stageA -> stageB then command would be stageA.prepare_next(stageB)
        stripParenth =  r"\((.*?)\)"
        delta = self.exitOrigin() - stageNext.entranceOrigin()
        stageNext = stageNext.asVDF() 
        idCount = len(self.get_key_recursive('id'))

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
                                                    coord = np.array(list(map(int, coord)))
                                                    coord = coord + delta
                                                    coord = map(str, coord)
                                                    coord = ' '.join(coord)
                                                    coord = re.sub(r".*", r'(\g<0>)', coord)
                                                    vertex[i] = coord                                       
                                                vertex = ' '.join(vertex)
                                    del stageNext['world'][solidIdx, 'solid'][sideIdx, 'side']['plane']
                                    stageNext['world'][solidIdx, 'solid'][sideIdx, 'side']['plane'] = vertex
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
            del(stageNext['cameras'], stageNext['cordon'], stageNext['visgroups'], stageNext['viewsettings'], stageNext['versioninfo'])
            return(stageNext)
    
    def append_stage(self, stageN):
        stage = self.d
        del stage[self.exitIndex(), 'entity']        
        for i in stageN['world'].get_all_for('solid'):
            stage['world']['solid'] = i
        for i in stageN.get_all_for('entity'):
            stage['entity'] = i

        return stage

stageMain = Stage(stage0)
stageNext = Stage(stage1)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

stageMain = Stage(stageMain)
stageNext = Stage(stage2)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

stageMain = Stage(stageMain)
stageNext = Stage(stage3)
stageNext = stageMain.prepare_next(stageNext)
stageMain = stageMain.append_stage(stageNext)

vdf.dump(stageMain, open(r'stageGen.vmf', 'w'), pretty=True)
print("--- %s seconds ---" % (time.time() - start_time))