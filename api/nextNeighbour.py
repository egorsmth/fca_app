import core

# NextNeighbours algorythm implementation
# from Concept data analysis theory and applications, Claudio Carpineto, 2004 book

###
# input: context
# returns: lattice data structure
#
# for detail explanation of algorythm
# and background theory see Concept data analysis theory and applications book page 34
###
def nextNeighbours(ctx):
    root = core.Node(set(ctx.G), core.derivG(ctx, ctx.G))
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
    return core.Lattice(C, E)

###
# input: context
# returns: maximum general candidates for concepts
#
# for detail explanation of algorythm
# and background theory see Concept data analysis theory and applications book page 34
###
def findLowerNeighbours(node, ctx):
    candidates = set()
    for m in ctx.M:
        if m in node.M:
            continue
        x1 = node.M.copy()
        x1.add(m)
        x1 = core.derivM(ctx, x1)
        y1 = core.derivG(ctx, x1)
        if (core.Node(x1, y1) not in candidates):
            candidates.add(core.Node(x1, y1))
    return core.maxGen(candidates)