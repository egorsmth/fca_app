import core
import copy

# add attribute algorythm implementation
# Concept data analysis theory and applications, Claudio Carpineto

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
    genNodes = core.maxGen(upCondNodes)
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

def intersCheck(nIdx, inters, lattice):
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
    k = core.derivG(newCtx, core.derivM(newCtx, set({attrM})))
    kk = core.derivM(newCtx, set({attrM}))
    
    founded = False
    for n in lattice.C:
        if n.G == kk:
            founded = True
            break
    if founded:
        for n in range(len(lattice.C)):
            if kk.intersection(lattice.C[n].G) == lattice.C[n].G:
                lattice.updateCbyIdx(n, core.Node(lattice.C[n].G, lattice.C[n].M.union(k), True))
        updateCtx(ctx,attrM,attrMI)
        return (ctx, lattice)
    
    oldL = copy.deepcopy(lattice)
    rootNode = core.Node(core.derivM(ctx, set(ctx.M)), set(ctx.M))
        
    if kk.intersection(rootNode.G) != rootNode.G:
        n = core.Node(set(), k, True)
        lattice.C.append(n)
        lattice.C = sorted(lattice.C, key=lambda node: node.level)
        lattice.addEdgeIdxs((lattice.C.index(n), lattice.C.index(rootNode)))
    n = core.Node(kk, k, True)
    lattice.C.append(n)
    lattice.C = sorted(lattice.C, key=lambda node: node.level)
    linkConcept(lattice.C.index(n), set({lattice.C.index(rootNode)}), lattice)     
    
    for nIdx in range(len(oldL.C)):
        node = oldL.C[nIdx]
        if node.G.intersection(kk) == node.G:
            M = copy.copy(node.M)
            M = M.union(k)
            lattice.updateCbyIdx(lattice.C.index(node), core.Node(node.G, M, True))
        inters = node.G.intersection(kk)
        if not(len(inters) == 0 or inters == kk or inters == node.G or intersCheck(lattice.C.index(node), inters, lattice)):
            M = copy.copy(node.M)
            M = M.union(k)
            nn = core.Node(inters, M, True)
            lattice.C.append(nn)
            lattice.C = sorted(lattice.C, key=lambda node: node.level)
            linkConcept(lattice.C.index(nn), set({lattice.C.index(n), lattice.C.index(node)}), lattice)
    
    lattice.C = sorted(lattice.C, key=lambda node: node.level)
    updateCtx(ctx,attrM,attrMI)
    return (ctx, lattice)