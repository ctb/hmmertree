#! /usr/bin/env python
"""
Some tools for exploring quicktree-generated trees based on hmmalign.

Focused right now on metagenomic distance matrix stuff.

"""
import tree_parser
import bincount

def print_nodetree(n, indent=0, cutoff=None):
    score = float(n.branch_length)
    if cutoff is not None:
        if score > cutoff:
            return
        
#    b.add(score)
    
    if isinstance(n, tree_parser.LeafNode):
        print ' '*indent + n.name, n.branch_length, 'L'
    elif isinstance(n, tree_parser.BranchNode):
        for m in n.subnodes:
            print_nodetree(m, indent=indent + 1, cutoff=cutoff)
        print ' '*indent + 'S', n.branch_length
    else:
        assert 0

def max_score(node):
    score = float(node.branch_length)

    for m in node.subnodes:
        score = max(score, max_score(m))

    return score

def get_node_in_tree_containing(root_nodes, *seqnames):

    def _find_node(n, name):
        "Return leaf node under 'n' with name 'name'"
        for m in n.subnodes:
            if m.name == name:
                return m
            
            x = _find_node(m, name)
            if x:
                return x
            
    def _count(n):
        "Count number of leaves with name in 'seqnames' under 'n'"
        total = 0
        for m in n.subnodes:
            total += _count(m)

        if n.name:
            for name in seqnames:
                if n.name == name:
                    total += 1

        return total

    def _beneath(n):
        "Return first node under 'n' ..."
        n_found = 0
        for m in n.subnodes:
            if _count(m) == len(seqnames):
                return m

        return None

    for root_node in root_nodes:
        leaf = _find_node(root_node, seqnames[0])
        if leaf:
            break

    n = leaf
    while 1:
        count = _count(n)
        if count == len(seqnames):
            break

        if n.parent is None:
            n = None
            break

        n = n.parent
        
    return n

def count_children(node):
    total = 0
    for m in node.subnodes:
        total += count_children(m)

    return total + 1

def count_leaves(node, cutoff=None):
    if cutoff is not None:
        score = float(node.branch_length)
        if score > cutoff:
            return 0
            
    if node.name:                       # leaf node: +1!
        return 1
    
    total = 0
    for m in node.subnodes:
        total += count_leaves(m, cutoff)
    
    return total

def get_leaf_names(node, cutoff=None):
    if cutoff is not None:
        score = float(node.branch_length)
        if score > cutoff:
            return []
            
    if node.name:
        return [node.name]

    x = list()
    for m in node.subnodes:
        x.extend(get_leaf_names(m, cutoff=cutoff))
    return x

def get_nodes_containing_both(root_nodes, pop_a, pop_b, cutoff):
    def _find_node(n, name):
        "Return leaf node under 'n' with name 'name'"
        for m in n.subnodes:
            if m.name == name:
                return m
            
            x = _find_node(m, name)
            if x:
                return x

    all_collected = []

    pop_b = set(pop_b)
    for name in pop_a:
        for root_node in root_nodes:
            container = _find_node(root_node, name)
            if container:
                break

        assert container

        last_set = set()
        n = container
        found = False
        while 1:
            n = n.parent
            this_set = set(get_leaf_names(n, cutoff))

            if this_set == last_set or n.parent is None:
                break

            if this_set.intersection(pop_b):
                found = True
                break

            last_set = this_set

        if found:
            all_collected.append(n)

    return list(set(all_collected))

if __name__ == '__main__':
    import sys
    treefp = iter(open(sys.argv[1]))

    root_nodes = tree_parser.parse_rootnode(treefp)

    ##

    all_names = []
    for node in root_nodes:
        all_names.extend(get_leaf_names(node))

    ncbi_names = [ z for z in all_names if '|' in z ]
    soil_names = [ z for z in all_names if '|' not in z ]

    cutoff = .2
    print root_nodes
    nodes = get_nodes_containing_both(root_nodes,
                                      ncbi_names, soil_names, cutoff)
    for i, n in enumerate(nodes):
        cnt = count_leaves(n, cutoff=cutoff)
        print i, n, cnt
        if cnt < 20:
            print_nodetree(n, cutoff=cutoff)

    ## 
#    fp = open('xxx', 'w')
#    fp.write("\n".join(get_leaf_names(nodes[47])))

