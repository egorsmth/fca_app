import copy
from functools import reduce
import networkx as nx
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import json


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

class Lattice:
    def __init__(self, C, E):
        self.C = C
        self.E = E
    def addToC(self, n):
        self.C.append(n)
        self.C = sorted(self.C, key=lambda node: node.level)
    def hashEdgeToNetwork(self):
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

def nextNeighbours(ctx):
    root = Node(set(ctx.G), derivG(ctx, ctx.G))
    C = [root]
    E = set()
    currentLevel = set({root})
    while len(currentLevel) != 0:
        nextLevel = set()
        for node in currentLevel:
            lowerNeighbours = findLowerNeighbours(node, ctx)
            for lowerNode in lowerNeighbours:
                if lowerNode not in C:
                    C.append(lowerNode)
                    nextLevel.add(lowerNode)
                E.add((lowerNode.__hash__(), node.__hash__())) # add edge loweNode -> node to E
        currentLevel = nextLevel
    C = sorted(C, key=lambda node: node.level)
    return Lattice(C, E)
                
            

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

def findLowerNeighbours(node, ctx):
    candidates = set()
    for m in ctx.M:
        if m in node.M:
            continue
        x1 = node.M.copy()
        x1.add(m)
        x1 = derivM(ctx, x1)
        y1 = derivG(ctx, x1)
        if (Node(x1, y1) not in candidates):
            candidates.add(Node(x1, y1))
    return maxGen(candidates)

def levelsCount(latticeC):
    lengths = dict()
    curLen = 0
    level = 0
    for n in range(len(latticeC)):
        if (level != latticeC[n].level):
            curLen = 1
            level = latticeC[n].level
        else:
            curLen += 1
        lengths[level] = curLen
    return lengths

def draw(lattice, outFileName):
    fig = plt.figure(figsize=(80,80))
    G = nx.Graph()
    G.add_edges_from(lattice.hashEdgeToNetwork())
    #plt.subplot(122)
    
    counts = levelsCount(lattice.C)
    pos={}
    labels = {}
    i = 1
    prevLevel = 0
    levMult = 1
    levelNum = 1
    for n in range(len(lattice.C)):
        labels[n] = lattice.C[n].__str__()
        level = lattice.C[n].level
        if (prevLevel != level):
            levelNum += 1
            levMult = 1
            prevLevel = level
        else:
            levMult += 1
        pos[n] = (i/(counts[level]+1) * levMult, 1 - i * levelNum)

    nx.draw_networkx_labels(G,pos,labels,font_size=30)
    
    nx.draw_networkx_nodes(G,pos, list(filter(lambda n: (not lattice.C[n].changed), range(len(lattice.C)))), node_size=80000,node_color="#e6eeff")
    nx.draw_networkx_nodes(G,pos, list(filter(lambda n: (lattice.C[n].changed), range(len(lattice.C)))), node_size=80000,node_color="#ffd4d4")
    nx.draw_networkx_edges(G,pos)
    affectedEdges = []
    changedNodesIdxs = list(filter(lambda n: (lattice.C[n].changed), range(len(lattice.C))))
    for e in lattice.hashEdgeToNetwork():
        if e[0] in changedNodesIdxs or e[1] in changedNodesIdxs:
            affectedEdges.append(e)

    nx.draw_networkx_edges(G, pos, edgelist=affectedEdges, width=16, alpha=0.5, edge_color="#ffd4d4")
    plt.savefig(outFileName)

def updateCtx(ctx,attrM,attrMI):
    ctx.M.append(attrM)
    for i in range(len(ctx.I)):
        ctx.I[i].append(attrMI[i])
    ctx.updateInner()

def getParentsIdxs(lattice, nodeIdx):
    parents = set()
    for n in lattice.hashEdgeToNetwork():
        if (n[0] == nodeIdx):
            parents.add(n[1])
    return parents
        
def getChildrebIdxs(lattice, nodeIdx):
    children = set()
    for n in lattice.hashEdgeToNetwork():
        if (n[1] == nodeIdx):
            children.add(n[0])
    return children

def FindLowBoundary(newNodeIdx, descendantsIdxs, lattice):
    lowBoundry = set()
    newNode = lattice.C[newNodeIdx]
    for desc in descendantsIdxs:
        lowCond = set()
        parents = getParentsIdxs(lattice, desc)
        for pIdx in parents:
            p = lattice.C[pIdx]
            if newNode.M.intersection(p.M) == newNode.M:
                lowCond.add(pIdx)
        if len(lowCond) == 0:
            lowBoundry.add(desc)
        else:
            lowBoundry = lowBoundry.union(FindLowBoundary(newNodeIdx, lowCond, lattice))
    return lowBoundry

def FindUpBoundary(newNodeIdx, lowBoundaryIdxs, lattice):
    firstLevelIdxs = set()
    for i in lowBoundaryIdxs:
        firstLevelIdxs = firstLevelIdxs.union(getParentsIdxs(lattice, i))
    
    upCond = FindNextLevel(newNodeIdx, firstLevelIdxs, lattice)
    upCondNodes = set()
    for i in upCond:
        upCondNodes.add(lattice.C[i])
    genNodes = maxGen(upCondNodes)
    genIdxs = set()
    for n in genNodes:
        for i in range(len(lattice.C)):
            if lattice.C[i].__hash__() ==  n.__hash__():
                genIdxs.add(i)
                break
    if len(genIdxs) != len(genNodes):
        raise Exception("num of indexes should be equal to nodes")
    return genIdxs

def FindNextLevel(newNodeIdx, currLevelIdxs, lattice):
    upCond = set()
    newNode = lattice.C[newNodeIdx]
    
    for nIdx in currLevelIdxs:
        node = lattice.C[nIdx]
        if node.M.intersection(newNode.M) == node.M:
            upCond.add(nIdx)
        else:
            parentsIdxsOfnode = getParentsIdxs(lattice, nIdx)
            upCond = upCond.union(FindNextLevel(newNodeIdx, parentsIdxsOfnode, lattice))
    return upCond
            
        
def linkConcept(newNodeIdx, descendantsIdxs, lattice):
    lowBoundaryIdxs = FindLowBoundary(newNodeIdx, descendantsIdxs, lattice)
    upBoundaryIdxs = FindUpBoundary(newNodeIdx, lowBoundaryIdxs, lattice)
    # Remove edges between lowBoundary and upBoundary, if any
    for i in lowBoundaryIdxs:
        for j in upBoundaryIdxs:
            lattice.E.discard((lattice.C[i].__hash__(), lattice.C[j].__hash__()))            
            lattice.E.discard((lattice.C[j].__hash__(), lattice.C[i].__hash__()))
    # Add edges between any concept in lowBoundary and newNode
    for i in lowBoundaryIdxs:
        lattice.addEdgeIdxs((i, newNodeIdx))
    # Add edges between newNode and any concept in upBoundary
    for j in upBoundaryIdxs:
        lattice.addEdgeIdxs((newNodeIdx, j))

def someShit(nIdx, inters, lattice):
    childrenIdxs = getChildrebIdxs(lattice, nIdx)
    for cIdx in childrenIdxs:
        if lattice.C[cIdx].G.intersection(inters) == inters:
            return True
    return False

def addAttr(ctx, lattice, attrM, attrMI):
    if (len(attrMI) != len(ctx.G)):
        raise Exception("there should be same number of objects parameters")
    
    newCtx = copy.deepcopy(ctx)
    updateCtx(newCtx, attrM, attrMI)
    k = derivG(newCtx, derivM(newCtx, set({attrM})))
    kk = derivM(newCtx, set({attrM}))
    
    founded = False
    for n in lattice.C:
        if n.G == kk:
            founded = True
            break
    if founded:
        for n in range(len(lattice.C)):
            if kk.intersection(lattice.C[n].G) == lattice.C[n].G:
                lattice.updateCbyIdx(n, Node(lattice.C[n].G, lattice.C[n].M.union(k), True))
        updateCtx(ctx,attrM,attrMI)
        return (ctx, lattice)
    
    oldL = copy.deepcopy(lattice)
    rootNode = Node(derivM(ctx, set(ctx.M)), set(ctx.M))
        
    if kk.intersection(rootNode.G) != rootNode.G:
        n = Node(set(), k, True)
        lattice.C.append(n)
        lattice.C = sorted(lattice.C, key=lambda node: node.level)
        lattice.addEdgeIdxs((lattice.C.index(n), lattice.C.index(rootNode)))
    n = Node(kk, k, True)
    lattice.C.append(n)
    lattice.C = sorted(lattice.C, key=lambda node: node.level)
    linkConcept(lattice.C.index(n), set({lattice.C.index(rootNode)}), lattice)     
    
    for nIdx in range(len(oldL.C)):
        node = oldL.C[nIdx]
        if node.G.intersection(kk) == node.G:
            M = copy.copy(node.M)
            M = M.union(k)
            lattice.updateCbyIdx(lattice.C.index(node), Node(node.G, M, True))
        inters = node.G.intersection(kk)
        if not(len(inters) == 0 or inters == kk or inters == node.G or someShit(lattice.C.index(node), inters, lattice)):
            M = copy.copy(node.M)
            M = M.union(k)
            nn = Node(inters, M, True)
            lattice.C.append(nn)
            lattice.C = sorted(lattice.C, key=lambda node: node.level)
            linkConcept(lattice.C.index(nn), set({lattice.C.index(n), lattice.C.index(node)}), lattice)
    
    lattice.C = sorted(lattice.C, key=lambda node: node.level)
    updateCtx(ctx,attrM,attrMI)
    return (ctx, lattice)