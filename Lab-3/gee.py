import re, sys, string

# Expression and Statement base classes

# Expression class
class Expression(object):
    def __str__(self):
        return ""

# Statement class
class Statement(object):
    def __str__(self):
        return ""

# Expression subclass
class BinaryExpr(Expression):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def __str__(self):
        return f"{self.op} {self.left} {self.right}"


class Number(Expression):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class String(Expression):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f'"{self.value}"'

class VarRef(Expression):
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name


class Assign(Statement):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def __str__(self):
        return f"= {self.name} {self.expr}"


class IFstatement(Statement):
    def __init__(self, expr, IFblock):
        self.expr = expr
        self.IFblock = IFblock
    def __str__(self):
        return f"if {self.expr}\n{self.IFblock}\nendif"

# Statement subclass
class WHILEstatement(Statement):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block
    def __str__(self):
        return f"while {self.expr}\n{self.block}\nendwhile"

# Statement subclass
class Block(Statement):
    def __init__(self, stmts):
        self.stmts = stmts
    def __str__(self):
        return "\n".join(str(s) for s in self.stmts)

# Statement subclass
class StmtList(Statement):
    def __init__(self, stmts):
        self.stmts = stmts
    def __str__(self):
        return "\n".join(str(s) for s in self.stmts)

# Error and matching

def error(msg):
    sys.exit(msg)

def match(matchtok):
    tok = tokens.peek()
    if tok != matchtok:
        error("Expecting " + matchtok)
    tokens.next()
    return tok

# Parsing expressions

def factor():
    tok = tokens.peek()
    
    if re.match(Lexer.number, tok):
        
        tokens.next()
        return Number(tok)
    elif re.match(Lexer.string, tok):
        
        val = tok[1:-1]
        tokens.next()
        
        return String(val)
    
    elif re.match(Lexer.identifier, tok):
        tokens.next()
        
        return VarRef(tok)
    
    elif tok == '(':
        tokens.next()
        expr = expression()
        match(')')
        return expr


def term():
    left = factor()
    tok = tokens.peek()
    

    while tok in ('*', '/'): 
        tokens.next()
        right = factor()
        left = BinaryExpr(tok, left, right)
        tok = tokens.peek()
    return left

# start of code lmao 


def addExpr():
    
    start = term()
    tok = tokens.peek()
    while tok in ('+', '-'):  
        tokens.next()
        right = term()
        start = BinaryExpr(tok, start, right)
        tok = tokens.peek()
    return start


def expression():
    
    start = addExpr()
    tok = tokens.peek()
    
    if tok and re.match(Lexer.relational, tok):
        op = tok
        tokens.next()
        right = addExpr()
        start = BinaryExpr(op, start, right)
    return start


def andExpr():
    

    start = expression()
    tok = tokens.peek()
    
    while tok == 'and':
        
        tokens.next()
        end = expression()
        start = BinaryExpr(tok, start, end)
        tok = tokens.peek()
        
    return start

# Parsing statements

def parseAssign():
    
    x = tokens.peek()
    if not re.match(Lexer.identifier, x):
        error(f"Assignment must start with an identifier, got: {x}")
    tokens.next()
    
    match('=')
    
    value_expr = expression()
    
    match(';')
    return Assign(x, value_expr)


def parseIf():
    match('if')
    expr = expression()
    block_if = parseBlock()
    return IFstatement(expr, block_if)


def parseWhile():
    match('while')
    
    ex = expression()
    peice = parseBlock()
    
    return WHILEstatement(ex, peice)


def parseBlock():
    match(':'); match(';'); match('@')
    statements = []
    
    while tokens.peek() != '~':
        statements.append(parseStmt())
    match('~')
    return Block(statements)


def parseStmt():
    
    token = tokens.peek()
    

    if token == 'if':
        return parseIf()
    elif token == 'while':
        return parseWhile()
    else:
        return parseAssign()




def parseStmtList():
    states = []
    while tokens.peek() is not None: states.append(parseStmt())
    return StmtList(states)



    
def parse( text ) :
	global tokens
	tokens = Lexer( text )
	#expr = addExpr( )
	#print (str(expr))
	#     Or:
	stmtlist = parseStmtList( )
	print (str(stmtlist))
	return

# done


class Lexer:
    special    = r"\(|\)|\[|\]|,|:|;|@|~|\$"
    relational = r"<=?|>=?|==?|!="
    arithmetic = r"\+|\-|\*|/"
    string     = r"'[^']*'|\"[^\"]*\""
    number     = r"-?\d+(?:\.\d+)?"
    literal    = string + "|" + number
    identifier = r"[a-zA-Z]\w*"
    lexRules   = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier

    def __init__(self, text):
        self.tokens   = re.findall(Lexer.lexRules, text)
        self.position = 0

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def next(self):
        self.position += 1
        return self.peek()

    def __str__(self):
        return f"<Lexer at {self.position} in {self.tokens}>"

# Utilities for indentation-based blocks

def chkIndent(line):
    ct = 0
    for ch in line:
        if ch != ' ': return ct
        ct += 1
    return ct


def delComment(line):
    pos = line.find('#')
    if pos > -1:
        return line[:pos].rstrip()
    return line


def mklines(filename):
    inn = open(filename, 'r')
    lines, pos, ct = [], [0], 0
    for line in inn:
        ct += 1
        line = line.rstrip() + ';'
        line = delComment(line)
        if not line or line == ';': continue
        indent = chkIndent(line)
        line = line.lstrip()
        if indent > pos[-1]:
            pos.append(indent); line = '@' + line
        elif indent < pos[-1]:
            while indent < pos[-1]:
                pos.pop()
                line = '~' + line
        print(ct, "\t", line)
        lines.append(line)
    undent = ''
    for _ in pos[1:]: undent += '~'
    lines.append(undent)
    return lines


def main():
    ct = 0
    for opt in sys.argv[1:]:
        if not opt.startswith('-'): break
        ct += 1
    if len(sys.argv) < 2 + ct:
        print(f"Usage: {sys.argv[0]} filename")
        return
    parse(''.join(mklines(sys.argv[1 + ct])))

if __name__ == '__main__':
    main()
