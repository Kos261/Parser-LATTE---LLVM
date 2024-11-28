import os

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