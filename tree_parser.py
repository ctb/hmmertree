"""
A simple parser for the newick format output by quicktree.

newick: http://evolution.genetics.washington.edu/phylip/newicktree.html
quicktree: http://www.sanger.ac.uk/Software/analysis/quicktree
"""
import sys
sys.setrecursionlimit(65000)

class LeafNode(object):
    """
    A node representing a sequence.

    Should have non-empty name & branch_length attribute; 'parent', if
    it is not None, refers to parent node.  'subnodes' is empty and
    present for simplicity when traversing trees.
    
    """
    def __init__(self, name, branch_length):
        self.name = name
        self.branch_length = float(branch_length)
        self.subnodes = []
        self.parent = None
        self.originals = None           # @CTB

    def __repr__(self):
        return '%s:%.2f' % (self.name, self.branch_length)

class BranchNode(object):
    """
    A node representing a branch point.  Should have non-empty 'subnodes' and
    'branch_length'.  'name' is empty.  'parent', if it is not None, refers
    to parent node.
    
    """
    def __init__(self, subnodes, branch_length):
        self.name = ''
        self.subnodes = subnodes
        self.branch_length = float(branch_length)
        self.parent = None

    def __repr__(self):
        return ':%.2f' % (self.branch_length)

def _parse(treefp):
    """
    Recursively parse the interior of a newick-tree formatted file.
    
    """
    subnodes = []

    while 1:
        try:
            line = treefp.next()
        except StopIteration:
            return BranchNode(subnodes, -1.0) # end of file => goodbye

        line = line.strip().rstrip(';')
            
        if line == '(':                 # ^( => recurse
            node = _parse(treefp)
            subnodes.append(node)
        elif line[0] == ':':            # ^: => BranchNode
            assert len(subnodes) == 2
            
            branch_length = line[1:-1]
            node = BranchNode(subnodes, branch_length)
            for m in node.subnodes:        # assign parent
                m.parent = node
            return node
        else:                           # name:branch_length => LeafNode
            
            line = line[:-1]            # remove )$
            name, branch_length = line.rsplit(':', 1)
            node = LeafNode(name, branch_length)
            subnodes.append(node)

def parse_rootnode(fp):
    """
    Load a newick-tree formatted file into a tree of BranchNode and LeafNode
    objects.  Return the children of the root node as a list.

    BranchNodes will have exactly two children, and LeafNodes will have zero.
    
    """
    fp = iter(fp)
    line = fp.next()                    # ignore first line
    assert line.strip() == '('
    
    root = _parse(fp)
    assert root.branch_length == -1.0   # root node list => no branch length
    return root.subnodes

if __name__ == '__main__':
    fp = open(sys.argv[1])
    parse_rootnode(fp)
    print '** parsing did not fail.'
