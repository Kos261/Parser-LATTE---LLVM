import os
from lark import Lark, Transformer, v_args
from TreeVisitorLLVM import TreeVisitorLLVM
from SemanticVisitors import SygnatureAnalyzer, FunctionCallAnalyzer



class LLVM_Creator:
    def __init__(self):
        self.printf_decl = 'declare i32 @printf(i8*, ...)\n'
        self.format_str = '@.fmt = constant [12 x i8] c"%s\\0A\\00"\n'

        self.start_part = """
define i32 @main() {
entry:
"""




    def create_llvm(self, instructions, printable_registers, filename="TEST"):
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        os.makedirs('foo/bar', exist_ok=True)

        with open(f"foo/bar/{base_filename}.ll", mode='w') as file:
            file.write(self.printf_decl)
            file.write(self.format_str)
            file.write(self.start_part)

            for instruction in instructions:
                file.write(f"  {instruction}\n")
            
            file.write("  ret i32 0\n")
            file.write("}\n")

def load_ins(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program







if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()


    # try:
    parser = Lark(grammar, parser='lalr', start='start')
    code = load_ins('examples/Hello.lt')
    tree = parser.parse(code)
    print(tree.pretty())
    # except:
    #     Exception("Unable to parse file. Something went wrong")
    
    
    SIG_analyzer = SygnatureAnalyzer()   

    SIG_analyzer.visit(tree)
    SIG_analyzer.display_function_table()
    # SIG_analyzer.check_main()


    Call_analyzer = FunctionCallAnalyzer(SIG_analyzer.func_table)
    Call_analyzer.visit(tree)

