from dataclasses import dataclass
from typing import Optional, List, Union

# Podstawowa klasa dla instrukcji i wyrażeń
@dataclass
class Instruction:
    pass

# Wyrażenia
@dataclass
class Expression(Instruction):
    pass

@dataclass
class BinaryOperation(Expression):
    left: str  # Tymczasowy rejestr lub zmienna
    operator: str
    right: str
    result: str  # Tymczasowy wynik (np. "t1")

@dataclass
class UnaryOperation(Expression):
    operand: str
    operator: str
    result: str

@dataclass
class LogicalOperation(Expression):
    left: str
    operator: str
    right: str
    result: str

@dataclass
class Variable(Expression):
    name: str  # Nazwa zmiennej

@dataclass
class Literal(Expression):
    value: str  # Wartość literalu (np. "5" lub "true")

# Instrukcje
@dataclass
class Assignment(Instruction):
    variable: str  # Nazwa zmiennej
    value: str  # Wynik wyrażenia

@dataclass
class IFStatement(Instruction):
    condition: str  # Tymczasowy rejestr z wynikiem warunku
    then_body: List[Instruction]
    else_body: Optional[List[Instruction]]

@dataclass
class WhileStatement(Instruction):
    condition: str  # Tymczasowy rejestr z wynikiem warunku
    body: List[Instruction]

@dataclass
class ReturnStatement(Instruction):
    value: Optional[str]  # Zwracana wartość lub None dla "void"

# Program jako lista instrukcji
@dataclass
class Program:
    instructions: List[Instruction]
