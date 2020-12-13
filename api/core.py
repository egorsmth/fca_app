from functools import reduce

import json

###
# Context class with additional methods for preactical usage
# and inner representation. Inner representation is hash table of context for faster lookup of attributes and objects in context
#
# updateInner: update inner representation of context after it is changed from outside or inside
# getRowByG: get hashes of attribures by object
# getColByM: get hashes of objects by attribute
# toJson: returns json representation of context
#
###
class Context:
    def __init__(self, G, M, I):
        self.G = G
        self.I = I
        self.M = M
        self.updateInner()
        
    def updateInner(self):
        inner = dict()
        for idxg in range(len(self.G)):
            row = dict()
            for idxm in range(len(self.M)):
                row[self.M[idxm]] = self.I[idxg][idxm]
            inner[self.G[idxg]] = row
        self.inner = inner
        
    def getRowByG(self, g):
        return self.inner[g]
    def getColByM(self,m):
        res = dict()
        for (key, val) in enumerate(self.inner):
            res[val] = self.inner[val][m]
        return res
    def __repr__(self):
        res = "X "
        for i in self.M:
            res += i + " "
        res += "\n"
        for i in range(len(self.G)):
            res += self.G[i] + " "
            res += " ".join(list(map(str, self.I[i])))
            res += "\n"
        return res
    def toJson(self):
        return dict({
            'G': list(self.G),
            'M': list(self.M),
            'I': list(self.I)
        })

###
# Node class is concept with hash representation for inner usage and toJson method
###
class Node:
    def __init__(self, G, M, changed = False):
        self.G = G
        self.M = M
        # for view
        self.level = len(M)
        self.changed = changed
    def __hash__(self):
        return hash(frozenset(self.G)) + hash(frozenset(self.M))
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.G == other.G and self.M == other.M
    def __repr__(self):
        return"{" + ", ".join(self.G) + "}\n{" + ", ".join(sorted(self.M)) + "}"
        
    def toJson(self):
        return dict({
            'G': list(self.G),
            'M': list(self.M),
            'changed': self.changed
        })

###
# Lattice class
#
# addToC: adds new concept 
# hashEdgeToNetwork: generates hash map of edges for faster nodes lookup
# addEdgeIdxs: add edge
# 
###
class Lattice:
    def __init__(self, C, E):
        self.C = C
        self.E = E
    def addToC(self, n):
        self.C.append(n)
        self.C = sorted(self.C, key=lambda node: node.level)
    def hashEdgeToNetwork(self):
        # hash based node storage for fast lookup
        indxTohash = {}
        for i in range(len(self.C)):
            indxTohash[self.C[i].__hash__()] = i
        edges = set()
        for p in self.E:
            edges.add((indxTohash[p[0]], indxTohash[p[1]]))
        return edges
    def updateCbyIdx(self, idx, newNode):
        oldHash = self.C[idx].__hash__()
        self.C[idx] = newNode
        self.C = sorted(self.C, key=lambda node: node.level)
        newHash = newNode.__hash__()
        newE = set()
        for i in self.E:
            if (i[0] == oldHash):
                newE.add((newHash, i[1]))
            elif (i[1] == oldHash): 
                newE.add((i[0], newHash))
            else:
                newE.add(i)
        self.E = newE
        
    def addEdgeIdxs(self, edge):
        self.E.add((self.C[edge[0]].__hash__(), self.C[edge[1]].__hash__()))

    def toJson(self):
        return dict({
            'C': list(map(lambda x : x.toJson(), self.C)),
            'E': list(map(lambda x: [str(x[0]), str(x[1])], list(self.E))),
        })

###
# derivative by objects set
# returns set of common attributes
###
def derivG(ctx, G1):
    res = set()
    rows = []
    for g in G1:
        rows.append(ctx.getRowByG(g))
    for m in ctx.M:
        temp = True
        for row in rows:
            if (row[m] == 0):
                temp = False
                break
        if temp:
            res.add(m)
    return res

###
# derivative by attributes set
# returns set of common objects
###    
def derivM(ctx, M1):
    res = set()
    cols = []
    for m in M1:
        cols.append(ctx.getColByM(m))
    for g in ctx.G:
        temp = True
        for col in cols:
            if col[g] == 0:
                temp = False
                break
        if temp:
            res.add(g)
    return res

###
# retunrs maximum general concepts of candidates concepts
###
def maxGen(candidates):
    res = set()
    for c in candidates:
        general = True
        for cc in candidates:
            if c == cc:
                continue
            if len(cc.G.intersection(c.G)) == len(c.G):
                general = False
                break
        if general:
            res.add(c)
    return res
