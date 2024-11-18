class TreeVisitorLLVM:
    def __init__(self) -> None:
        self.instructions = []
        self.variable_index = {}
        self.counter = 0
        self.last_register = None
        self.printable_registers = []

    def visit(self, node):
        node_type = node[0]
        method_name = f"visit_{node_type}"
        visitor = getattr(self, method_name, self.default_visit)
        return visitor(node)

    def default_visit(self, node):
        for child in node[1:]:
            if isinstance(child, tuple):
                self.visit(child)

    def visit_program(self, node):
        for child in node[1]:
            self.visit(child)

    def visit_function_def(self, node):
        func_type, func_name, args, block = node[1], node[2], node[3], node[4]
        # Możesz dodać obsługę funkcji tutaj
        self.visit(block)

    def visit_block(self, node):
        for stmt in node[1:]:
            self.visit(stmt)

    def visit_var_decl(self, node):
        var_type, var_decls = node[1], node[2]
        for decl in var_decls:
            if decl[0] == 'init':
                var_name, expr = decl[1], decl[2]
                self.visit(('assignment', var_name, expr))
            else:
                var_name = decl
                if var_name not in self.variable_index:
                    self.instructions.append(f"%{var_name} = alloca i32")
                    self.variable_index[var_name] = True
                    self.instructions.append(f"store i32 0, i32* %{var_name}")

    def visit_assignment(self, node):
        _, var_name, expr = node
        value_reg = self.visit(expr)
        if var_name not in self.variable_index:
            self.instructions.append(f"%{var_name} = alloca i32")
            self.variable_index[var_name] = True
        self.instructions.append(f"store i32 {value_reg}, i32* %{var_name}")

    def visit_expr_stmt(self, node):
        _, expr = node
        result_register = self.visit(expr)
        if result_register:
            self.printable_registers.append(result_register)

    def visit_ret(self, node):
        _, expr = node
        ret_reg = self.visit(expr)
        self.instructions.append(f"ret i32 {ret_reg}")

    def visit_expr(self, node):
        node_type = node[0]
        method_name = f"expr_{node_type}"
        expr_method = getattr(self, method_name, self.default_visit)
        return expr_method(node)

    def expr_or(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = or i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_and(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = and i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_equals(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp eq i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_not_equals(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp ne i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_lt(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp slt i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_lte(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp sle i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_gt(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp sgt i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_gte(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = icmp sge i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_add(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = add i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_sub(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = sub i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_mul(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = mul i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_div(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = sdiv i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_mod(self, node):
        _, left, right = node
        left_reg = self.visit(left)
        right_reg = self.visit(right)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = srem i32 {left_reg}, {right_reg}")
        return result_reg

    def expr_not(self, node):
        _, expr = node
        expr_reg = self.visit(expr)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = xor i32 {expr_reg}, 1")
        return result_reg

    def expr_neg(self, node):
        _, expr = node
        expr_reg = self.visit(expr)
        result_reg = f"%result_{self.counter}"
        self.counter += 1
        self.instructions.append(f"{result_reg} = sub i32 0, {expr_reg}")
        return result_reg

    def expr_inc(self, node):
        _, expr = node
        if expr[0] != 'var':
            raise Exception("Increment operatorem może być tylko zmienna")
        var_name = expr[1]
        if var_name not in self.variable_index:
            self.instructions.append(f"%{var_name} = alloca i32")
            self.variable_index[var_name] = True
            self.instructions.append(f"store i32 0, i32* %{var_name}")
        loaded_reg = f"%loaded_{self.counter}"
        self.instructions.append(f"{loaded_reg} = load i32, i32* %{var_name}")
        self.counter += 1
        inc_reg = f"%inc_{self.counter}"
        self.instructions.append(f"{inc_reg} = add i32 {loaded_reg}, 1")
        self.counter += 1
        self.instructions.append(f"store i32 {inc_reg}, i32* %{var_name}")
        return inc_reg

    def expr_dec(self, node):
        _, expr = node
        if expr[0] != 'var':
            raise Exception("Decrement operatorem może być tylko zmienna")
        var_name = expr[1]
        if var_name not in self.variable_index:
            self.instructions.append(f"%{var_name} = alloca i32")
            self.variable_index[var_name] = True
            self.instructions.append(f"store i32 0, i32* %{var_name}")
        loaded_reg = f"%loaded_{self.counter}"
        self.instructions.append(f"{loaded_reg} = load i32, i32* %{var_name}")
        self.counter += 1
        dec_reg = f"%dec_{self.counter}"
        self.instructions.append(f"{dec_reg} = sub i32 {loaded_reg}, 1")
        self.counter += 1
        self.instructions.append(f"store i32 {dec_reg}, i32* %{var_name}")
        return dec_reg

    def expr_func_call(self, node):
        _, func_name, args = node
        arg_regs = [self.visit(arg) for arg in args]
        # Zakładamy, że funkcja printString jest zdefiniowana jako printf
        if func_name == 'printString':
            fmt_str = '@.fmt = constant [12 x i8] c"%s\\0A\\00"\n'
            self.instructions.append(fmt_str)
            fmt_ptr = f"%fmt_ptr_{self.counter}"
            self.instructions.append(f"{fmt_ptr} = getelementptr [12 x i8], [12 x i8]* @.fmt, i32 0, i32 0")
            self.instructions.append(f"call i32 (i8*, ...) @printf(i8* {fmt_ptr}, i8* {arg_regs[0]})")
            self.counter += 1
            return None
        else:
            raise Exception(f"Nieznana funkcja: {func_name}")

    def get_instructions(self):
        return self.instructions, self.printable_registers
