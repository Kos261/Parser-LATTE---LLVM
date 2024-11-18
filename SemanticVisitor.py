from lark.visitors import Visitor
from lark import Tree

class SygnatureAnalyzer(Visitor):
    def __init__(self):
        super().__init__()
        self.func_table = {}

    def topdef(self, tree):
        func_name = tree.children[1]  
        return_type_node = tree.children[0] 
        return_type = return_type_node.data.replace("_type", "")
        children = tree.children[2:]

        # Ustalanie parametrów
        if isinstance(children[0], Tree) and children[0].data == 'arg_list':
            params = children[0].children
            block = children[1]
        else:
            params = []  # Funkcja bez parametrów
            block = children[0]

        param_types = [(param.children[0].data.replace("_type", ""), param.children[1]) for param in params]

        # Zapisanie sygnatury funkcji
        if func_name in self.func_table:
            raise Exception(f"Function {func_name} is already defined")

        self.func_table[func_name] = {
            'return_type': return_type,
            'params': param_types
        }

        

    def check_main(self):
        if 'main' not in self.func_table:
            raise Exception('Function "main" is missing')
        
        if self.func_table['main']['return_type'] != 'int':
            raise Exception('Function "main" should return integer')
        
        if self.func_table['main']['params'] != []:
            raise Exception("Function 'main' doesn't allow any arguments")
        
        print("Everything is good with main")
        

    def display_function_table(self):
        for func, sig in self.func_table.items():
            print(f"Function {func}: returns {sig['return_type']} with params {sig['params']} \n")




class FunctionCallAnalyzer(Visitor):
    def __init__(self, function_table):
        super().__init__()
        self.function_table = function_table


    def func_call_expr(self, tree):
        func_name = tree.children[0]
        args = tree.children[1:]

        if func_name not in self.function_table:
            raise Exception(f"Undefined function: {func_name}")
        
        func_signature = self.function_table[func_name]
        expected_params = func_signature['params']

        if len(args) != len(expected_params):
            raise Exception(f"Function {func_name} expects {len(expected_params)} number of arguments, got {len(args)}")
        
        
        for i, (arg, (expected_type, _)) in enumerate(zip(args, expected_params)):
            print(arg)
            print(expected_type)
            
            # if not self.check_type(arg, expected_type):
            #     raise Exception(f"Argument {i+1} of {func_name} has incorrect type")
            
        


    def check_type(self, arg, expected_type):
        pass