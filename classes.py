from logging import exception

class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children #list of nodes

    def Evaluate(self, symbol_table):
        pass

class NoOp(Node):
    pass

class IntVal(Node):
    def __init__(self, value, children):
        #super().__init__(value, children) # outra maneira de criar
        self.value = value
        self.children = children # nao vai usar

    def Evaluate(self, symbol_table):
        return (self.value,"i32")

class StrVal(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children # nao vai usar

    def Evaluate(self, symbol_table):
        return (self.value,"String")

class FuncDecl(Node):
    # tem 2 children VarDecl e Statements
    # os argumentos da declaração devem ser 
    # incorporados a VarDecl
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        # os childs todos sao nodes
        return_type = self.value
        FuncTable.create_value(self.children[0].value,self, return_type)


# serve para cuidar de variáveis
class FuncTable:
    table = {}
   
    def get_value(key):
        # vai devolver uma tupla de args e key
        if key in FuncTable.table:
            return FuncTable.table[key]
        else:
            raise Exception(f"Não existe a var {key} na func table")

    def create_value(key, args, type_return):
        if key not in FuncTable.table.keys():
            FuncTable.table[key] = (args, type_return)
        else:
            raise Exception(f"Já existe a key {key}")
    

class FuncCall(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        # verificar se a funcao foi declarada
        func, type_func = FuncTable.get_value(self.value)

        # criando uma nova symbol table local
        localSymbolTable = SymbolTable()
        args_passados = []

        for i in range(1, len(func.children) - 1):
            args_passados.append(func.children[i].children[0])
            func.children[i].Evaluate(localSymbolTable)

        # confirmando o numero de argumentos
        if len(args_passados) != len(self.children):
            raise Exception(f"A função recebeu {len(args_passados)} argumentos e precisa de {len(self.children)}")

        # aqui a ordem importa dos indices
        for i in range(len(args_passados)):
            localSymbolTable.set_value(args_passados[i], self.children[i].Evaluate(symbol_table))

        # o children -1 é o que queremos
        # func vai ser none se for main ou void
        block_node = func.children[-1]
        resultado = block_node.Evaluate(localSymbolTable)
        # print(f"resultado {resultado}")
        # print(f"type func = {type_func}")

        if type_func != "void" and type_func != "main":
            # confirmando se são iguais os tipos
            if type_func == resultado[1]:
                return resultado
            else:
                raise Exception("O tipo da funcao está errado")
        return resultado

class Return(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        # vai receber um node
        resultado = self.children[0]
        return resultado.Evaluate(symbol_table)


class UnOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children # um elemento só
    
    def Evaluate(self, symbol_table):
        if self.value == "+":
            return (+self.children[0].Evaluate(symbol_table)[0],"i32")
        elif self.value == "-":
            return (-self.children[0].Evaluate(symbol_table)[0],"i32")
        elif self.value == "!":
            return (not self.children[0].Evaluate(symbol_table)[0],"i32")
        else:
            raise Exception("UnOp deu errado")

class BinOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        # int só nos comparadores
        if self.value == "+":
            return (self.children[0].Evaluate(symbol_table)[0] + self.children[1].Evaluate(symbol_table)[0],"i32")
        elif self.value == "-":
            return (self.children[0].Evaluate(symbol_table)[0] - self.children[1].Evaluate(symbol_table)[0],"i32")
        elif self.value == "||":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            if left[1] == right[1]:
                return (int(left[0] or right[0]),"i32")
            else:
                raise Exception("Os tipos são diferentes")
        elif self.value == "/":
            return (self.children[0].Evaluate(symbol_table)[0] // self.children[1].Evaluate(symbol_table)[0],"i32")
        elif self.value == "*":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            if left[1] == right[1]:
                return (left[0] * right[0],"i32")
            else:
                raise Exception("Os tipos são diferentes")
        elif self.value == "&&":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            if left[1] == right[1]:
                return (int(left[0] and right[0]),"i32")
            else:
                raise Exception("Os tipos são diferentes")
        elif self.value == ">":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            if left[1] == right[1]:
                return (int(left[0] > right[0]),"i32")
            else:
                raise Exception("Os tipos são diferentes")
        elif self.value == "<":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            if left[1] == right[1]:
                return (int(left[0] < right[0]),"i32")
            else:
                raise Exception("Os tipos são diferentes")
        elif self.value == "==":
            left = self.children[0].Evaluate(symbol_table)
            right = self.children[1].Evaluate(symbol_table)
            return (int(left[0] == right[0]),"i32")
        elif self.value == ".":
            return (str(self.children[0].Evaluate(symbol_table)[0]) + str(self.children[1].Evaluate(symbol_table)[0]),"String")
        else:
            raise Exception("BinOp deu errado")

class Block(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        for child in self.children:
            # funcoes que vao retornar vai realmente retornar
            if child.value == "return":
                return child.Evaluate(symbol_table)
            child.Evaluate(symbol_table)

class Print(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        if self.value == "print":
            print(self.children[0].Evaluate(symbol_table)[0])

class Read(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        if self.value == "read":
            res = input()
            if res.isnumeric():
                return (int(res),"i32")
            else:
                raise Exception("Não é um número")

class While(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        if self.value == "while":
            while self.children[0].Evaluate(symbol_table)[0] == True:
                self.children[1].Evaluate(symbol_table)

class If(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        if self.value == "if":
            if self.children[0].Evaluate(symbol_table)[0] == True:
                self.children[1].Evaluate(symbol_table)
            elif len(self.children) == 3:
                self.children[2].Evaluate(symbol_table)
            
# serve para cuidar de variáveis
# tem que ser dinamica agora
class SymbolTable:

    def __init__(self):
        self.table = {}
   
    def get_value(self, key):
        # vai devolver uma tupla
        if key in self.table.keys():
            return self.table[key]
        else:
            raise Exception(f"Não existe a var {key} na symbol table")

    def set_value(self, key, tuple):
        type = tuple[1]
        # conferir se existe na tabela
        if key in self.table:
            type_registered = self.table[key][1]
            if type == type_registered:
                self.table[key] = tuple
            else:
                raise Exception("O tipo enviado é diferente do registrado")
        else:
            raise Exception(f"A key = {key} do set não existe ainda")

    def create_value(self, key, type):
        if key not in self.table:
            if type == "i32":
                self.table[key] = (0, type)
            elif type == "String":
                self.table[key] = ("", type)
            else:
                raise Exception("O tipo declarado não existe")
        else:
            raise Exception("Já existe essa key")
    
class Identifier(Node):
    # value vai ser o nome da variavel
    # children vazia
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def Evaluate(self, symbol_table):
        # sinalizei que seria funcao colocando no value
        if self.children[0] == "function":
            return FuncTable.get_value(self.value)
        # quando for var vai receber o nome dela como valor
        else:
            tuple = symbol_table.get_value(self.value)
            return (tuple[0],tuple[1])

class VarDecl(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children # nao vai usar

    def Evaluate(self, symbol_table):
        for child in self.children:
            # value é o tipo da variavel
            # cada child é um node identifier
            symbol_table.create_value(child, self.value)


class Assignment(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    # vai receber um value que é um node
    def Evaluate(self, symbol_table):
        if self.value == "=":
            symbol_table.set_value(self.children[0], self.children[1].Evaluate(symbol_table))
