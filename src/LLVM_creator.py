import os

class LLVM_Creator:
    def __init__(self):
      self.start_part = """
define i32 @main() {
entry:
"""

    def create_llvm(self, instructions, filename="TEST"):
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        os.makedirs('foo/bar', exist_ok=True)

        with open(f"foo/bar/{base_filename}.ll", mode='w') as file:
            file.write(self.start_part)

            for instruction in instructions:
                file.write(f"  {instruction}\n")
            
            file.write("  ret i32 0\n")
            file.write("}\n")