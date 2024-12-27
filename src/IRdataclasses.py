from dataclasses import dataclass

@dataclass
class Node:
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class BinaryOperation(Expression):
    left:Expression
    operator: str
    right: Expression

@dataclass
class Variable(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: str

@dataclass
class Assignment(Node):
    variable: Variable
    value: Expression

@dataclass
class IFStatement(Expression):
    condition: Expression
    then_body: Expression
    else_body: Expression    