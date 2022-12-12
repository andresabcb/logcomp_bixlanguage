# -*- coding: utf-8 -*-
from lib2to3.pgen2 import token
import sys
from classes import *

# arg = sys.argv
# file = arg[1]
file = "exemplos/exemplo1.txt"
open_file = open(file, "r")
source = open_file.read()

class Prepro:
    @staticmethod
    def filter(source):
        new_source_list = []
        for s in source.split("\n"):
            if "//" in s:
                s = s.partition("//")[0]
            new_source_list.append(s)
        if "\n" in new_source_list:
            new_source_list.remove("\n")
        new_source = "".join(new_source_list)
        return new_source

class Token:
    def __init__(self, ttype, value):
        self.type = ttype # string
        self.value = value # int

class Tokenizer:
    def __init__(self, source):
        self.source = Prepro.filter(source) # string
        self.position = 0 # int
        self.next = None
        
    def selectNext(self):
        present = ''
        while self.position < len(self.source) and self.source[self.position] == " ":
            self.position +=1
        value = ''
        if self.position == len(self.source):
            self.next = Token("eof",value)
        else:
            present = self.source[self.position]
            if present.isdigit():
                value = present
                self.position += 1
                type = "int"
                while self.position < len(self.source) and self.source[self.position].isdigit():
                    value += self.source[self.position]
                    self.position += 1
                self.next = Token(type,int(value))
            # se for variável
            elif present.isalpha():
                value = present
                self.position += 1
                type = "identifier"
                while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == "_"):
                    value += self.source[self.position]
                    self.position += 1
                if value == "Imprimir":
                    self.next = Token("print",value)
                elif value == "Ler":
                    self.next = Token("read",value)
                elif value == "se":
                    self.next = Token("if",value)
                elif value == "então":
                    self.next = Token("else",value)
                elif value == "enquanto":
                    self.next = Token("while",value)
                elif value == "String":
                    self.next = Token("type",value)
                elif value == "i32":
                    self.next = Token("type",value)
                elif value == "var":
                    self.next = Token("var",value)
                elif value == "fn":
                    self.next = Token("fn",value)
                elif value == "devolver":
                    self.next = Token("return",value)
                else:
                    self.next = Token(type,value)
            # se forem símbolos ou outra coisa
            else:
                value = None
                if present == "+":
                    type = "plus"
                elif present == "-":
                    if self.source[self.position+1] == ">":
                        type = "setinha"
                        self.position += 1 # vai andar 2 vezes
                    else:
                        type = "minus"
                elif present == "*":
                    type = "mult"
                elif present == "/":
                    type = "div"
                elif present == "(":
                    type = "abre parenteses"
                elif present == ")":
                    type = "fecha parenteses"
                elif present == "{":
                    type = "abre chaves"
                elif present == "}":
                    type = "fecha chaves"   
                elif present == ";":
                    type = "ponto virgula"
                elif present == "!":
                    type = "not"
                elif present == "<":
                    type = "menor"
                elif present == ">":
                    type = "maior"
                elif present == ".":
                    type = "ponto"
                elif present == ":":
                    type = "dois pontos"
                elif present == ",":
                    type = "virgula"           
                elif present == "=":
                    if self.source[self.position+1] == "=":
                        type = "igual igual"
                        self.position += 1 # vai andar 2 vezes
                    else:
                        type = "igual"
                elif present == "&":
                    if self.source[self.position+1] == "&":
                        type = "and"
                        self.position += 1
                    else:
                        raise TypeError("Faltou um segundo caractere '&'")
                elif present == "|":
                    if self.source[self.position+1] == "|":
                        type = "or"
                        self.position += 1
                    else:
                        raise TypeError("Faltou um segundo caractere '|'")
                elif present == '"':
                    self.position += 1
                    value = ''
                    type = 'value_string'
                    while self.source[self.position] != '"':
                        value += self.source[self.position]
                        self.position += 1
                else:
                    raise TypeError("A expressão tem caracteres nao registrados")
                self.position += 1
                self.next = Token(type,value)

        # print(f"{self.next.type}")
        # print(f"{self.next.value}\n")

class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer(source)

    @staticmethod
    def parseProgram(tokenizer):
        node = Block("program",[])
        while tokenizer.next.type != "eof":
            child = Parser.parseDeclaration(tokenizer)
            node.children.append(child)
        node.children.append(FuncCall("Principal", []))
        return node


    @staticmethod
    def parseDeclaration(tokenizer):
        if tokenizer.next.type == "fn":
            tokenizer.selectNext()
            if tokenizer.next.type == "identifier":
                func_id = tokenizer.next.value
                child = Identifier(func_id, ["function"])
                node = FuncDecl("",[])
                # mas tem que ser o primeiro filho sim
                node.children.append(child)
                tokenizer.selectNext()
                if tokenizer.next.type == "abre parenteses":
                    tokenizer.selectNext()
                    while tokenizer.next.type != "fecha parenteses":
                        # nao precisa de next pq nao consumiu nada
                        identifiers = []
                        if tokenizer.next.type == "identifier":
                            # lista de nodes identifiers
                            name_id = tokenizer.next.value
                            # node_identifier = Identifier(name_id,["variable"])
                            identifiers.append(name_id)
                            tokenizer.selectNext()
                            # virgula de dentro #1 - primeira passada
                            # tive que repetir aqui para nao dar problema na lista de ids
                            if tokenizer.next.type == "virgula":
                                tokenizer.selectNext()
                            # no caso de já ser dois pontos
                            elif tokenizer.next.type == "dois pontos":
                                tokenizer.selectNext()
                                if tokenizer.next.type == "type":
                                    for id in identifiers:     
                                        type_ids = tokenizer.next.value # tipo da variavel
                                        child = VarDecl(type_ids, id)
                                        # colocando esse node como filho da funcdecl
                                        node.children.append(child)
                                        tokenizer.selectNext()
                                        if tokenizer.next.type == "virgula":
                                            tokenizer.selectNext()
                                else:
                                    raise Exception("Não tem o tipo depois dos dois pontos")
                            else:
                                raise Exception("Não tem dois pontos depois do argumento")
                        else:
                            raise Exception("Não recebemos um id")
                    # quando receber o fecha parenteses
                    tokenizer.selectNext()
                    # se tiver setinha precisa atualizar o tipo
                    if func_id == "Principal":
                        type_return = "main"
                    else:
                        type_return = "void"
                    if tokenizer.next.type == "setinha":
                        tokenizer.selectNext()
                        if tokenizer.next.type == "type":
                            type_return = tokenizer.next.value
                            if type_return != "i32" and type_return != "String":
                                raise Exception("O tipo declarado não é aceito")
                            tokenizer.selectNext()
                        else:
                            raise Exception("Faltou o type após a setinha")
                    node.value = type_return
                    last_child = Parser.parseBlock(tokenizer)
                    node.children.append(last_child)
                    return node
            else:
                raise Exception("A fn não recebeu identifier")
        else:
            raise Exception("Não abriu chaves")

    @staticmethod
    def parseBlock(tokenizer):
        if tokenizer.next.type == "abre chaves":
            tokenizer.selectNext()
            node = Block("",[])
            while tokenizer.next.type != "fecha chaves":
                child = Parser.parseStatement(tokenizer)
                node.children.append(child)
            tokenizer.selectNext()
            # if node.children[0] != None:
            #     return node
        else:
            raise Exception("Não abriu chaves")
        return node

    # vai cuidar de prints e variáveis
    @staticmethod
    def parseStatement(tokenizer):
        node = tokenizer.next.value # dúvida sobre isso
        if tokenizer.next.type == "ponto virgula":
            tokenizer.selectNext()
            node = NoOp(tokenizer,[])
            return node

        elif tokenizer.next.type == "identifier":
            token_id = tokenizer.next.value
            identifier = token_id
            tokenizer.selectNext()
            if tokenizer.next.type == "igual":
                tokenizer.selectNext()
                node = Assignment("=",[identifier,Parser.parseRelationalExpression(tokenizer)])
                if tokenizer.next.type == "ponto virgula":
                    tokenizer.selectNext()
                    return node
                else:
                    raise Exception("Não tem ponto e vírgula")

            # chamada de função
            elif tokenizer.next.type == "abre parenteses":
                node = FuncCall(token_id,[])
                tokenizer.selectNext()
                while tokenizer.next.type != "fecha parenteses":
                    while tokenizer.next.type == "virgula":
                        tokenizer.selectNext()
                        child = Parser.parseRelationalExpression(tokenizer)
                        node.children.append(child)
                        #tokenizer.selectNext()
                    if tokenizer.next.type == "ponto virgula":
                        tokenizer.selectNext()
                        return node
                    else:
                        raise Exception("Não tem ponto e vírgula")
                tokenizer.selectNext()
            else:
                raise Exception("Faltou um sinal de igual ou um abre parenteses depois do id")

        elif tokenizer.next.type == "return":
            tokenizer.selectNext()
            child = Parser.parseRelationalExpression(tokenizer)
            node = Return("return",[])
            node.children.append(child)
            #tokenizer.selectNext()
            return node

        elif tokenizer.next.type == "print":
            tokenizer.selectNext()
            if tokenizer.next.type == "abre parenteses":
                tokenizer.selectNext() # vai achar a expression
                node = Print("print",[Parser.parseRelationalExpression(tokenizer)])
                if tokenizer.next.type == "fecha parenteses":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "ponto virgula":
                        tokenizer.selectNext()
                        return node
                    else:
                        raise Exception("Não tem ponto e vírgula")
                else:
                    raise Exception("Não fechou parenteses")
            else:
                raise Exception("Não colocou parenteses")
        
        elif tokenizer.next.type == "var":
            tokenizer.selectNext()
            node = VarDecl("",[]) # CRIAR
            if tokenizer.next.type == "identifier":
                child = tokenizer.next.value
                node.children.append(child)
                tokenizer.selectNext()
                while tokenizer.next.type == "virgula":
                    tokenizer.selectNext() #nome da outra variavel
                    child = tokenizer.next.value
                    node.children.append(child)
                    tokenizer.selectNext() #virgula de novo se tiver (ou dois pontos)
                if tokenizer.next.type == "dois pontos":
                    tokenizer.selectNext() 
                    # preenchendo o tipo - vardecl
                    if tokenizer.next.type == "type":
                        node.value = tokenizer.next.value
                        tokenizer.selectNext()
                        if tokenizer.next.type == "ponto virgula":
                            tokenizer.selectNext()
                            return node
                        else:
                            Exception("Não tem ponto e vírgula")
                else:
                    raise Exception("Não colocou dois pontos")
            else:
                raise Exception("Não colocou o nome da variavel")

        elif tokenizer.next.type == "while":
            tokenizer.selectNext()
            if tokenizer.next.type == "abre parenteses":
                tokenizer.selectNext() # vai achar a expression
                child = Parser.parseRelationalExpression(tokenizer)
                if tokenizer.next.type == "fecha parenteses":
                    tokenizer.selectNext()
                    node = While("while",[child, Parser.parseStatement(tokenizer)])
                    return node
                else:
                    raise Exception("Não fechou parenteses")
            else:
                raise Exception("Não colocou parenteses")

        elif tokenizer.next.type == "if":
            tokenizer.selectNext()
            if tokenizer.next.type == "abre parenteses":
                tokenizer.selectNext() # vai achar a expression
                child0 = Parser.parseRelationalExpression(tokenizer)
                if tokenizer.next.type == "fecha parenteses":
                    tokenizer.selectNext()
                    child1 = Parser.parseStatement(tokenizer)
                    if tokenizer.next.type == "else":
                        tokenizer.selectNext()
                        node = If("if",[child0, child1, Parser.parseStatement(tokenizer)])
                    else:
                        node = If("if",[child0, child1])
                    return node
                else:
                    raise Exception("Não fechou parenteses")
            else:
                raise Exception("Não colocou parenteses")

        else:
            return Parser.parseBlock(tokenizer)

    # vai cuidar de ints, positivos e negativos
    @staticmethod
    def parseFactor(tokenizer):
        node = tokenizer.next.value
        if tokenizer.next.type == "int":
            node = IntVal(tokenizer.next.value, [])
            tokenizer.selectNext()
        elif tokenizer.next.type == "value_string":
            node = StrVal(tokenizer.next.value, [])
            tokenizer.selectNext()
        elif tokenizer.next.type == "plus":
            tokenizer.selectNext()
            node = UnOp("+",[Parser.parseFactor(tokenizer)])
        elif tokenizer.next.type == "minus":
            tokenizer.selectNext()
            node = UnOp("-",[Parser.parseFactor(tokenizer)])
        elif tokenizer.next.type == "not":
            tokenizer.selectNext()
            node = UnOp("!",[Parser.parseFactor(tokenizer)])
        # O QUE FAZER COM PARENTESES - ignorar, a profundidade já resolve
        elif tokenizer.next.type == "abre parenteses":
            tokenizer.selectNext()
            node = Parser.parseRelationalExpression(tokenizer)
            if tokenizer.next.type == "fecha parenteses":
                tokenizer.selectNext()
            else:
                raise Exception("Não fechou o parênteses")
        # essa parte precisa ser arrumada
        elif tokenizer.next.type == "identifier":
            token_id = tokenizer.next.value
            tokenizer.selectNext()
            if tokenizer.next.type == "abre parenteses":
                arguments = []
                tokenizer.selectNext()
                while tokenizer.next.type != "fecha parenteses":
                    argu = Parser.parseRelationalExpression(tokenizer)
                    arguments.append(argu)
                    while tokenizer.next.type == "virgula":
                        tokenizer.selectNext()
                        argu = Parser.parseRelationalExpression(tokenizer)
                        arguments.append(argu)
                tokenizer.selectNext()
                node = FuncCall(token_id,arguments)
                return node
            else:
                node = Identifier(token_id,["variable"])
                return node
                #tokenizer.selectNext()
        elif tokenizer.next.type == "read":
            node = Read("read",[])
            tokenizer.selectNext()   
            if tokenizer.next.type == "abre parenteses":
                tokenizer.selectNext()
                if tokenizer.next.type == "fecha parenteses":
                    tokenizer.selectNext()
                else:
                    raise Exception("Read incompleto")
            else:
                raise Exception("Read incompleto")
        else:
            raise Exception("Não tem nenhum token que cabe no factor")
        return node

    # vai calcular divisões e multiplicações
    @staticmethod
    def parseTerm(tokenizer):
        node = Parser.parseFactor(tokenizer)
        while tokenizer.next.type == "div" or tokenizer.next.type == "mult" or tokenizer.next.type == "and":
            if tokenizer.next.type == "div":
                tokenizer.selectNext()
                node = BinOp("/",[node, Parser.parseFactor(tokenizer)])
            if tokenizer.next.type == "mult":
                tokenizer.selectNext()
                node = BinOp("*",[node,Parser.parseFactor(tokenizer)])
            if tokenizer.next.type == "and":
                tokenizer.selectNext()
                node = BinOp("&&",[node,Parser.parseFactor(tokenizer)])
        return node

    # vai calcular somas e subtrações
    @staticmethod
    def parseExpression(tokenizer):
        node = Parser.parseTerm(tokenizer)
        while tokenizer.next.type == "plus" or tokenizer.next.type == "minus" or tokenizer.next.type == "or":
            if tokenizer.next.type == "plus":
                tokenizer.selectNext()
                node = BinOp("+",[node,Parser.parseTerm(tokenizer)])
            if tokenizer.next.type == "minus":
                tokenizer.selectNext()
                node = BinOp("-",[node,Parser.parseTerm(tokenizer)])
            if tokenizer.next.type == "or":
                tokenizer.selectNext()
                node = BinOp("||",[node,Parser.parseTerm(tokenizer)])
        return node

    @staticmethod
    def parseRelationalExpression(tokenizer):
        node = Parser.parseExpression(tokenizer)
        while tokenizer.next.type == "igual igual" or tokenizer.next.type == "menor" or tokenizer.next.type == "maior" or tokenizer.next.type == "ponto":
            if tokenizer.next.type == "igual igual":
                tokenizer.selectNext()
                node = BinOp("==",[node,Parser.parseExpression(tokenizer)])
            if tokenizer.next.type == "menor":
                tokenizer.selectNext()
                node = BinOp("<",[node,Parser.parseExpression(tokenizer)])
            if tokenizer.next.type == "maior":
                tokenizer.selectNext()
                node = BinOp(">",[node,Parser.parseExpression(tokenizer)])
            if tokenizer.next.type == "ponto":
                tokenizer.selectNext()
                node = BinOp(".",[node,Parser.parseExpression(tokenizer)])
        return node
    
    @staticmethod
    def run(source):
        filtered_source = Prepro.filter(source)
        tokenizer = Tokenizer(filtered_source)
        tokenizer.selectNext()
        return_res = Parser.parseProgram(tokenizer)
        if tokenizer.next.type != "eof":
            raise Exception("Nao consumiu tudo")
        return return_res

symbol_table = SymbolTable()
resultado = Parser.run(source).Evaluate(symbol_table)