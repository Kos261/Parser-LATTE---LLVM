from lark.visitors import Visitor
from lark import Tree, Token
from src.IRdataclasses import *
from src.LLVM_frontend import FunctionCallAnalyzer


class ScopeHandler:
    def __init__(self):
        self.symbol_table_stack = [{}]
        self.temp_types = {} # Na typy rejestrów żeby pamiętać o nich
        self.block_counter = 0

    def enter_block(self):
        self.symbol_table_stack.append({})
        self.block_counter += 1

    def exit_block(self):
        if len(self.symbol_table_stack) > 1:
            self.symbol_table_stack.pop()
        else:
            raise Exception("Attempted to exit global scope")

    def declare_variable(self, var_name, var_type, value_tree=None):
        current_scope = self.symbol_table_stack[-1]

        if var_name in current_scope:
            raise Exception(f"Variable {var_name} already declared in this scope")
        
        unique_name = f"{var_name}_block{self.block_counter}"
        current_scope[unique_name] = var_type
        return unique_name

    def get_variable_type(self, var_name):    
        if var_name.startswith('"') and var_name.endswith('"'):
            return 'string'
        if var_name.isdigit():
            return 'int'

        # Obsługa rejestrów tymczasowych
        if var_name in self.temp_types:
            return self.temp_types[var_name]
        try:
            for scope in reversed(self.symbol_table_stack):
                if var_name in scope:
                    return scope[var_name]
        except:
            raise Exception(f"Variable '{var_name}' not declared")
        

    def set_temp_type(self, temp, var_type):
        self.temp_types[temp] = var_type

    def reset(self):
        self.symbol_table_stack = [{}]


class LLVM_QuadCode(Visitor):
    def __init__(self, function_table):
        self.instructions = []
        self.quadruples = []


        self.variable_index = {}
        self.temp_counter = 0
        self.label_counter = 0
        self.register_counter = 0
        self.last_register = None

        self.function_table = function_table
        self.scope_handler = ScopeHandler()
        self.function_call_analyzer = FunctionCallAnalyzer(self.function_table, self.scope_handler)
        self.current_function = (None, False)

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def visit(self, tree):
        handlers = {
            'topdef': self.topdef,
            'ret_stmt': self.ret_stmt,
            'vret_stmt': self.vret_stmt,
            'if_stmt': self.if_stmt,
            'if_else_stmt': self.if_else_stmt,
            'decr_stmt': self.decr_stmt,
            'incr_stmt': self.incr_stmt,
            'while_stmt': self.while_stmt,
            'decl_stmt':self.decl_stmt,
            'block':self.block,
            'int_expr': self.eval_expr,
            'boolean_expr': self.eval_expr,
            'true_expr': self.eval_expr,
            'false_expr': self.eval_expr,
            'string_expr': self.eval_expr,
            'var_expr': self.eval_expr,
            'add_expr': self.eval_expr,
            'sub_expr': self.eval_expr,
            'and_expr': self.eval_expr,
            'or_expr': self.eval_expr,
            'not_expr': self.eval_expr,
            'mul_expr': self.eval_expr,
            'div_expr': self.eval_expr,
            'rel_expr': self.eval_expr,
            'paren_expr': self.eval_expr,
            'func_call_expr': self.eval_expr,
            'neg_expr': self.eval_expr,
        }


        # Węzły, które wymagają odwiedzenia poddrzew
        self.passthrough_nodes = {'start', 'program', 'stmt', 'item', 'item_list', 'stmt_list', 'expr_list', 'expr_stmt'}

        if tree.data in handlers:
            return handlers[tree.data](tree)

        elif tree.data in self.passthrough_nodes:
            for child in tree.children:
                if isinstance(child, Tree):
                    self.visit(child)

        else:
            raise Exception(f"Unhandled node type: {tree.data}")

    def eval_expr(self, tree):
        handlers = {
            'int_expr': self.eval_int_expr,
            'boolean_expr': self.eval_boolean_expr,
            'string_expr':self.eval_string_expr,
            'true_expr': self.eval_boolean_literal,
            'false_expr': self.eval_boolean_literal,
            'var_expr': self.eval_var_expr,

            'add_expr': self.Binary_expr,
            'sub_expr': self.Binary_expr,
            'mul_expr': self.Binary_expr,
            'div_expr': self.Binary_expr,

            'and_expr': self.Logical_expr,
            'or_expr': self.Logical_expr,

            'not_expr': self.Unary_expr,
            'neg_expr': self.Unary_expr,

            'rel_expr': self.eval_rel_expr,
            'paren_expr': self.eval_paren_expr,
            'func_call_expr': self.func_call_expr,
        }

        if tree.data in handlers:
            return handlers[tree.data](tree)

        elif tree.data in self.passthrough_nodes:
            for child in tree.children:
                if isinstance(child, Tree):
                    return self.eval_expr(child)  

        else:
            raise Exception(f"Unsupported expression type: {tree.data}")
     
    def eval_int_expr(self, tree):
        value = tree.children[0].value
        return value

    def eval_boolean_expr(self, tree): # To nie jest w ogóle teraz używane?
        value = tree.children[0].value
        return value

    def eval_boolean_literal(self, tree):
        if tree.data == 'true_expr':
            return 'true'
        elif tree.data == 'false_expr':
            return 'false'
        else:
            raise Exception(f"Nieznany węzeł logiczny: {tree.data}")

    def eval_string_expr(self, tree):
        value = tree.children[0].value
        return value

    def eval_var_expr(self, tree):
        var_name = tree.children[0].value
        return var_name  

    def eval_add_expr(self, tree):
        return self.Binary_expr(tree)

    def Binary_expr(self, tree):
        left_tree = tree.children[0]
        operator = tree.children[1].data
        right_tree = tree.children[2]

        left_result = self.eval_expr(left_tree)
        right_result = self.eval_expr(right_tree)

        left_type = self.scope_handler.get_variable_type(left_result)
        right_type = self.scope_handler.get_variable_type(right_result)
      

        result = self.new_temp()

        if operator == 'plus_op' and left_type == 'string' and right_type == 'string':
            self.quadruples.append(FunctionCall(
                name='Concat',
                params=[left_result, right_result],
                result=result
            ))
            self.scope_handler.set_temp_type(result, 'string')

        else:
            self.quadruples.append(BinaryOperation(
                left=left_result,
                operator=operator,
                right=right_result,
                result=result
            ))
            self.scope_handler.set_temp_type(result, 'int')

        return result

    def Logical_expr(self, tree):
        left_tree = tree.children[0]
        right_tree = tree.children[1]

        left_result = self.eval_expr(left_tree)
        result = self.new_temp()

        false_label = self.new_label()
        end_label = self.new_label()

        # Krótkie spięcie dla &&
        if tree.data == 'and_expr':
            # Jeśli lewy operand jest false -> L1
            self.quadruples.append(
                LogicalOperation(
                    left=left_result,
                    operator='if_false',
                    right=None,
                    result=false_label
                )
            )
            # Skok na koniec wyrażenia
            self.quadruples.append(
                LogicalOperation(
                    left=None,
                    operator='goto',
                    right=None,
                    result=end_label
                )
            )
            # Jeśli lewy operand jest false -> t1=false
            self.quadruples.append(
                LogicalOperation(
                    left=None,
                    operator='label',
                    right=None,
                    result=false_label
                )
            )
            self.quadruples.append(
                Assignment(
                    variable=result,
                    value='false'
                )
            )
            self.quadruples.append(
                LogicalOperation(
                    left=None,
                    operator='label',
                    right=None,
                    result=end_label
                )
            )

        elif tree.data == 'or_expr':
            # Krótkie spięcie dla ||
            true_label = self.new_label()

            # Jeśli lewy operand jest true -> L1
            self.quadruples.append(
                LogicalOperation(
                    left=left_result,
                    operator='if_true',
                    right=None,
                    result=true_label
                )
            )
            # Ewaluacja prawego operand
            right_result = self.eval_expr(right_tree)
            self.quadruples.append(
                Assignment(
                    variable=result,
                    value=right_result
                )
            )
            # Skok na koniec wyrażenia
            self.quadruples.append(
                LogicalOperation(
                    left=None,
                    operator='goto',
                    right=None,
                    result=end_label
                )
            )
            # Jeśli lewy operand jest true -> t1=true
            self.quadruples.append(
                Assignment(
                    variable=result,
                    value='true'
                )
            )
            self.quadruples.append(
                LogicalOperation(
                    left=None,
                    operator='label',
                    right=None,
                    result=end_label
                )
            )

        return result

    def Unary_expr(self, tree):
        expr = tree.children[0]
        operand = self.eval_expr(expr)
        result = self.new_temp()

        if tree.data == 'not_expr':
            self.quadruples.append(UnaryOperation(
                operator='!',
                operand=operand,
                result=result
            ))

        elif tree.data == 'neg_expr':
            self.quadruples.append(UnaryOperation(
                            operator='-',
                            operand=operand,
                            result=result
                        ))
        return result

    def Declaration_expr(self, tree):
        var_type = tree.children[0].data
        items = tree.children[1].children  

        default_values = {
            'int_type': '0',
            'boolean_type': 'false',
            'string_type': '""'
        }

        for item in items:
            var_name = item.children[0].value
            self.scope_handler.declare_variable(var_name, var_type.replace("_type", ""))

            if len(item.children) > 1:
                expr = item.children[1]
                value = self.eval_expr(expr)
            else:
                value = default_values[var_type]

            unique_var_name = self.scope_handler.declare_variable(var_name, var_type)

            self.quadruples.append(Assignment(
                variable=unique_var_name,
                value=value
            ))
     
    def eval_and_expr(self, tree):
        return self.Logical_expr(tree)
        
    def eval_or_expr(self, tree):
        return self.Logical_expr(tree)
       
    def eval_not_expr(self, tree):
        return self.Unary_expr(tree)

    def eval_rel_expr(self, tree):
        left = self.eval_expr(tree.children[0])  
        operator = tree.children[1].data             # <, >, ==, !=
        right = self.eval_expr(tree.children[2])  
        result = self.new_temp()

        self.quadruples.append(LogicalOperation(
            left=left,
            operator=operator,
            right=right,
            result=result
        ))

        return result

    def eval_paren_expr(self, tree):
        return self.eval_expr(tree.children[0])

    def func_call_expr(self, tree):
        result = self.new_temp()

        func_name = tree.children[0].value
        args = [self.eval_expr(arg) for arg in tree.children[1].children]

        if func_name in {'printInt', 'printString', 'error'}:
            self.quadruples.append(FunctionCall(
                name=func_name,
                params=args,
                result=None
            ))
        else:
            result = self.new_temp()
            self.quadruples.append(FunctionCall(
                name=func_name,
                params=args,
                result=result
            ))

        ret_type = self.function_table[func_name]['return_type']
        self.scope_handler.set_temp_type(result, ret_type)
        return result

    def block(self, tree):
        self.scope_handler.enter_block()
        self.quadruples.append(Label(name='block_start'))
        for stmt in tree.children:  
            self.visit(stmt) 
        self.quadruples.append(Label(name='block_end'))
        self.scope_handler.exit_block()

    def decl_stmt(self, tree):       
        return self.Declaration_expr(tree)

    def variable(self, tree):
        var_name = tree.children[0].value
        var_type = self.scope_handler.get_variable_type(var_name)
     
    def decr_stmt(self, tree):
        var_name = tree.children[0].value
        var_type = self.scope_handler.get_variable_type(var_name)
        
    def incr_stmt(self, tree):
        var_name = tree.children[0].value
        var_type = self.scope_handler.get_variable_type(var_name)
         
    def neg_expr(self, tree):
        expr = tree.children[0]
        expr_type = self.eval_expr(expr)

        return 'int'

    def var_decl_with_expr(self, tree):
        var_type = tree.children[0]
        var_name = tree.children[1].value
        expr = tree.children[2]
        expr_type = self.eval_expr(expr)

        self.scope_handler.declare_variable(var_name, var_type)

    def topdef(self, tree):
        func_name = tree.children[1].value
        self.current_function = (func_name, False)
        return_type = tree.children[0].data.replace("_type", "")
        block = tree.children[-1]

        params = self.function_table[func_name]['params']

        if func_name not in self.function_table:
            self.function_table[func_name] = {
                'return_type': return_type,
                'params': params
            }

        self.quadruples.append(FunctionDefinition(
        name=func_name,
        params=params
        ))


        self.scope_handler.enter_block()

        for param_type, param_name in params:
            self.scope_handler.declare_variable(param_name, param_type)

        self.visit(block)
        self.quadruples.append(EndFunction(name=func_name))

        self.scope_handler.exit_block()
        self.current_function = (None, False)

    def ret_stmt(self, tree):
        if len(tree.children) > 0:
            value = self.eval_expr(tree.children[0])
        else:
            value = None #'void'?

        self.quadruples.append(ReturnStatement(value=value))

        current_function = self.current_function[0]
        expected_type = self.function_table[current_function]['return_type']
        
    def vret_stmt(self, tree):
        self.ret_stmt(tree)

    def if_stmt(self, tree):
        condition = self.eval_expr(tree.children[0])
        then_block = tree.children[1]
        end_label = self.new_label()

        # Skok warunkowy do końca, jeśli warunek fałszywy
        self.quadruples.append(ConditionalJump(
            condition=condition,
            target=end_label
        ))

        # Kod bloku "then"
        self.visit(then_block)

        if len(tree.children) == 3:
            # Jeśli istnieje "else"
            else_block = tree.children[2]
            else_label = self.new_label()

            # Dodaj skok do bloku "else"
            self.quadruples.append(Jump(target=else_label))
            self.quadruples.append(Label(name=end_label))
            self.visit(else_block)
            self.quadruples.append(Label(name=else_label))
        else:
            # Dodaj etykietę końcową tylko dla "then"
            self.quadruples.append(Label(name=end_label))

    def if_else_stmt(self, tree):
        condition = self.eval_expr(tree.children[0])
        then_block = tree.children[1]  
        else_block = tree.children[2]

        else_label = self.new_label()
        end_label = self.new_label()

        self.quadruples.append(ConditionalJump(
                    condition=condition,
                    target=else_label
                ))
        
        self.visit(then_block)
        self.quadruples.append(Jump(target=end_label))

        
        self.quadruples.append(Label(name=else_label))
        self.visit(else_block)

        self.quadruples.append(Label(name=end_label))

    def while_stmt(self, tree):
        start_label = self.new_label()
        end_label = self.new_label()

        self.quadruples.append(Label(name=start_label))

        condition_result = self.eval_expr(tree.children[0])
        self.quadruples.append(ConditionalJump(
            condition=condition_result,
            target=end_label
        ))

        # Ciało pętli
        self.visit(tree.children[1])

        # Skok z powrotem do początku pętli
        self.quadruples.append(Jump(target=start_label))

        # Koniec pętli
        self.quadruples.append(Label(name=end_label))

    def get_instructions(self):
        return self.quadruples

