import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide2 import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QLabel , QGridLayout, QTextEdit ,QFormLayout , QLineEdit, QPushButton, QHBoxLayout,QVBoxLayout,QApplication, QWidget , QInputDialog
from pyparsing import Literal,CaselessLiteral,Word,Combine,Group,Optional,\
    ZeroOrMore,Forward,nums,alphas
from numpy import *
import operator

fromto = [0,0,""]
exprStack = []

#Parsing code
def pushFirst( strg, loc, toks ):
    exprStack.append( toks[0] )
def pushUMinus( strg, loc, toks ):
    if toks and toks[0]=='-': 
        exprStack.append( 'unary -' )
        #~ exprStack.append( '-1' )
        #~ exprStack.append( '*' )

bnf = None
def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | T | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        point = Literal( "." )
        e     = CaselessLiteral( "E" )
        fnumber = Combine( Word( "+-"+nums, nums ) + 
                           Optional( point + Optional( Word( nums ) ) ) +
                           Optional( e + Word( "+-"+nums, nums ) ) )
        ident = Word(alphas, alphas+nums+"_$")

        plus  = Literal( "+" )
        minus = Literal( "-" )
        mult  = Literal( "*" )
        div   = Literal( "/" )
        lpar  = Literal( "(" ).suppress()
        rpar  = Literal( ")" ).suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal( "^" )
        pi    = CaselessLiteral( "PI" )
        t     = CaselessLiteral( "X" )

        expr = Forward()
        atom = (Optional("-") + ( pi | e | t | fnumber | ident + lpar + expr + rpar ).setParseAction( pushFirst ) | ( lpar + expr.suppress() + rpar )).setParseAction(pushUMinus) 

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( pushFirst ) )

        term = factor + ZeroOrMore( ( multop + factor ).setParseAction( pushFirst ) )
        expr << term + ZeroOrMore( ( addop + term ).setParseAction( pushFirst ) )
        bnf = expr
    return bnf

# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = { "+" : operator.add,
        "-" : operator.sub,
        "*" : operator.mul,
        "/" : operator.truediv,
        "^" : operator.pow }
fn  = { "sin" : sin,
        "cos" : cos,
        "tan" : tan,
        "abs" : abs,
        "trunc" : lambda a: int(a),
        "round" : round,
        "sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}

def evaluateStack( s ):
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack( s )
    if op in "+-*/^":
        op2 = evaluateStack( s )
        op1 = evaluateStack( s )
        return opn[op]( op1, op2 )
    elif op == "PI":
        return math.pi # 3.1415926535
    elif op == "E":
        return math.e  # 2.718281828
    elif op == "X":
        return linspace(int(fromto[0]),int(fromto[1]),int(fromto[1])-int(fromto[0]))
    elif op in fn:
        return fn[op]( evaluateStack( s ) )
    elif op[0].isalpha():
        return 0
    else:
        return float( op )

def compute(s):   
    global exprStack
    exprStack = []
    results = BNF().parseString( s )
    val = evaluateStack( exprStack[:] )
    return val


#genrates the matplot graph
class Canvas(FigureCanvas):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=200)
        super().__init__(fig)
        self.setParent(parent)
        t = np.arange(int(fromto[0]),int(fromto[1]))
        s = compute(fromto[2])
        self.ax.plot(t, s)
        self.ax.set(xlabel='X Axis', ylabel='Y Axis',
               title='Graph')
        self.ax.grid()
        




#checks changes in from the gui
def text_changed(s):
    if s:
        fromto[2]=s
def text_changed2(s):
    if s:
        fromto[0]=s

def text_changed3(s):
    if s:
        fromto[1]=s
#calls the grapher and add it to the app layout
def onButtonClicked():
    demo = AppDemo()
    if(layoutM.itemAt(2)!=None):
        layoutM.removeItem(layoutM.itemAt(2))
    layoutM.addWidget(demo)
        
    

#embeds the graph into a qt widget 
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        chart = Canvas(self)

#genrates the app
app = QApplication(sys.argv)
window = QWidget()
window.setGeometry(50,50,1000,970)
window.setWindowTitle("MyGrapher")
window.show()

#layouts
layoutM = QVBoxLayout(window)
layout = QGridLayout(window)
layoutM.addLayout(layout)

#components
FunctionLabel = QLabel("Function:")
FunctionEdit = QLineEdit()
MinLabel = QLabel("Min:")
MinEdit = QLineEdit()
MaxLabel = QLabel("Max:")
MaxEdit = QLineEdit()
Graphbutton = QPushButton('Graph')

#attach componennts to event listners 
Graphbutton.clicked.connect(onButtonClicked)
FunctionEdit.textChanged.connect(text_changed)
MinEdit.textChanged.connect(text_changed2)
MaxEdit.textChanged.connect(text_changed3)

#add components to layout
layout.addWidget(FunctionLabel, 0, 0)
layout.addWidget(FunctionEdit, 0, 1)
layout.addWidget(MinLabel, 1, 0)
layout.addWidget(MinEdit, 1, 1)
layout.addWidget(MaxLabel, 2, 0)
layout.addWidget(MaxEdit, 2, 1)
layout.setRowStretch(2, 1)
layoutM.addWidget(Graphbutton)

#styling the layout
layoutM.addStretch()
layoutM.setAlignment(Qt.AlignHCenter)



sys.exit(app.exec_())