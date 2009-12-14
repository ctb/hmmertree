#! /usr/bin/env python
import sys
sys.setrecursionlimit(65000)

class LeafNode(object):
    def __init__(self, name, score):
        self.name = name
        self.score = score

class InnerNode(object):
    def __init__(self, subnodes, score=None):
        self.nodes = subnodes
        self.score = score

class ScoreNode(object):
    def __init__(self, subnodes, score):
        self.nodes = subnodes
        self.score = score

    def __repr__(self):
        return "<ScoreNode(%s)>" % self.score

def print_nodetree(n, indent=0):
    if isinstance(n, LeafNode):
        print ' '*indent + n.name, n.score, 'L'
    elif isinstance(n, ScoreNode):
        for m in n.nodes:
            print_nodetree(m, indent + 1)
        print ' '*indent + 'S', n.score
    else:
        assert 0

def reprint_nodetree(n, fp):
    if isinstance(n, LeafNode):
        fp.write('%s:%s' % (n.name, n.score))
    elif isinstance(n, ScoreNode):
        for m in n.nodes:
            reprint_nodetree(m, fp)
            fp.write(',\n')
        fp.write('%s)\n' % n.score)
    else:
        for m in n.nodes:
            reprint_nodetree(m, fp)
            fp.write(',\n')
        fp.write(')\n')

lineno = 1
def parse_node():
    global lineno
    buf = ''
    nodes = []

    while 1:
        try:
            line = treefp.next()
            lineno += 1
        except StopIteration:
            return ScoreNode(nodes, 'XXX')

        line = line.strip().rstrip(';')
            
#        print '*', line, lineno
        if line == '(':
#            print 'push'
            node = parse_node()
            nodes.append(node)
        elif line[0] == ':':
#            print 'pop', len(nodes)
            assert len(nodes) == 2
            score = line[:-1]
            node = ScoreNode(nodes, score)
            return node
        else:
            name, score = line[:-1].split(':')
            node = LeafNode(name, score)
            nodes.append(node)

def parse_rootnode():
    treefp.next()
    n = parse_node()
    assert n.score == 'XXX'
    return n.nodes
    
treefp = iter(open(sys.argv[1]))

root_nodes = parse_rootnode()

for n in root_nodes:
    print_nodetree(n, 0)
