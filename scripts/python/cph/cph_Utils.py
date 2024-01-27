import hou

def Test():
    print('This is my python module!')

def get_digits(node):
    return int(''.join(filter(str.isdigit, node.name())))

