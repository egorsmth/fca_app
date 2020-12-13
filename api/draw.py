import networkx as nx
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


###
# input: concept from lattice
# returns: level of concept that is basically representation of vertical position on image
###
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

###
# input: lattice structure and output image filename
# returns: nothing
#
# generates image with networkx python lybrary and saves it to file
###
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

