from sys import exit


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # набор токенов после лексера
        self.pos = 0  # показывает текущий номер токена(позицию) в наборе токенов
        self.poliz = []  # итоговая польская инверсная запись
        self.buffer = []  # буферный стек для операций
        self.addrsForFilling = []  # хранит адреса ПОЛИЗa, куда потом нужно будет записать адрес перехода
        self.addrsJumps = []  # хранит адреса перехода в начало условия(только для while)
        self.calls = []  # стек вызовов операций while, if, else

    def parseExeption(self, expected, detected):
        print("\nParse error: detected " + "'" + detected +
              "', but " + "'" + expected + "' are expected!")
        exit(0)

    def endScript(self):
        return self.pos == len(self.tokens)

    def parse(self):
        return self.lang()

    # lang -> expr*
    def lang(self):
        while (not self.endScript()):
            if (not self.expr()):
                self.parseExeption("expression", self.tokens[self.pos][0])
        return True

        # expr -> assign | while_stmt | if_stmt | io

    def expr(self):
        if not (
                self.assign() or
                self.while_stmt() or
                self.if_stmt() or
                self.io()
        ):
            return False
        return True

        # io -> printing | inputting

    def io(self):
        if (self.printing() or
                self.inputting()):
            return True
        else:
            return False

    # assign -> var (assign_op (obj_create | obj_mulref | arif_stmt)) | obj_addVal semicolon
    def assign(self):
        if (not self.var()):
            return False
        elif (self.assign_op()):
            if not (self.obj_create() or self.obj_mulref() or self.arif_stmt()):
                self.parseExeption("arifmetical expression or object initialization", self.tokens[self.pos][0])
                return False
        elif not self.obj_addVal():
            self.parseExeption("var or object initialization", self.tokens[self.pos][0])
            return False
        if (not self.semicolon()):
            self.parseExeption(";", self.tokens[self.pos][0])
            return False
        return True

    # obj_addVal -> obj_ref obj_add
    def obj_addVal(self):
        if not (
                self.obj_ref() and
                self.obj_add()
        ):
            return False
        else:
            return True

    # obj_create -> KW_LL | KW_HS
    def obj_create(self):
        if (
                self.tokens[self.pos][1] == "LL" or
                self.tokens[self.pos][1] == "HS"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

            # obj_mulref -> var (obj_ref obj_simp_method)+

    def obj_mulref(self):
        if (not self.var()):
            return False
        elif (self.obj_ref() and self.obj_simp_method()):
            while (True):
                if not (
                        self.obj_ref() and
                        self.obj_simp_method()
                ):
                    return True
            return True
        else:
            # если условние всё же не выполнилось, нужно вытлкнуть переменную
            # которую успели занести в полиз
            self.poliz.pop()
            self.pos -= 1
            return False

    # obj_add -> KW_ADD bkt_open arif_stmt bkt_close
    def obj_add(self):
        if (not self.tokens[self.pos][1] == "ADD"):
            return False
        self.pushInStack(self.tokens[self.pos])
        self.pos += 1
        if (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.arif_stmt()):
            self.parseExeption("arithmetic expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        return True

        # obj_simp_method -> KW_GSIZE | KW_GNEXT | KW_GPREV | KW_GETVAL | KW_GFIRST | KW_GLAST | obj_inset

    def obj_simp_method(self):
        if (
                self.tokens[self.pos][1] == "GSIZE" or
                self.tokens[self.pos][1] == "GNEXT" or
                self.tokens[self.pos][1] == "GPREV" or
                self.tokens[self.pos][1] == "GVALUE" or
                self.tokens[self.pos][1] == "GFIRST" or
                self.tokens[self.pos][1] == "GLAST"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        elif (self.obj_inset()):
            return True
        else:
            return False

            # obj_inset -> KW_INSET bkt_open arif_stmt bkt_close

    def obj_inset(self):
        if (not self.tokens[self.pos][1] == "INSET"):
            return False
        self.pushInStack(self.tokens[self.pos])
        self.pos += 1
        if (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.arif_stmt()):
            self.parseExeption("arithmetic expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        return True

    def obj_ref(self):
        if self.tokens[self.pos][1] == "OBJ_REF":
            # В стек не добавляем намерено, чтобы не было мусора
            # данный символ нужен только для соответвия грамматике
            # self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def var(self):
        if self.tokens[self.pos][1] == "ID":
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def assign_op(self):
        if (
                self.tokens[self.pos][1] == "ASSIGN" or
                self.tokens[self.pos][1] == "PLUS_ASSIGN" or
                self.tokens[self.pos][1] == "MINUS_ASSIGN" or
                self.tokens[self.pos][1] == "MULT_ASSIGN" or
                self.tokens[self.pos][1] == "DIVISION_ASSIGN" or
                self.tokens[self.pos][1] == "MOD_ASSIGN"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # arif_stmt -> value (arif_op value)*
    def arif_stmt(self):
        if (not self.value()):
            return False
        while (True):  # эквивалентно (arif_op value)*
            if (not self.arif_op() and not self.value()):
                break
        return True

    # value -> var | number | bkt_expr
    def value(self):
        if not (
                self.var() or
                self.number() or
                self.bkt_expr()
        ):
            return False
        return True

        # number -> int | float | bool

    def number(self):
        if (
                self.tokens[self.pos][1] == "INT" or
                self.tokens[self.pos][1] == "FLOAT" or
                self.tokens[self.pos][1] == "BOOL"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # bkt_expr -> bkt_open arif_stmt bkt_close
    def bkt_expr(self):
        if (not self.bkt_open()):
            return False
        elif (not self.arif_stmt()):
            self.parseExeption("arithmetic expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        return True

    # log_stmt -> comp_expr (log_op comp_expr)*
    def log_stmt(self):
        if (not self.comp_expr()):
            return False
        while (True):
            if (self.log_op()):
                if (not self.comp_expr()):
                    self.parseExeption("compare expression", self.tokens[self.pos][0])
                    break
            else:
                break
        return True

    # comp_expr -> [log_not] (arif_stmt comp_op arif_stmt)
    def comp_expr(self):
        if (self.log_not()):
            pass
        if (self.arif_stmt()):
            if (not self.comp_op()):
                self.parseExeption("compare expression", self.tokens[self.pos][0])
                return False
            elif (not self.arif_stmt()):
                self.parseExeption("arithmetic expression", self.tokens[self.pos][0])
                return False
        else:
            return False
        return True

        # if_stmt -> KW_IF bkt_open log_stmt bkt_close brace_open expr* brace_close [else_stmt]

    def if_stmt(self):
        if (not self.KW_IF()):
            return False
        elif (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.log_stmt()):
            self.parseExeption("logical expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        elif (not self.brace_open()):
            self.parseExeption("{", self.tokens[self.pos][0])
            return False
        while (True):  # эквивалентно expr* - выполняется 0 или более раз
            if (not self.expr()):
                break
        if (not self.brace_close()):
            self.parseExeption("}", self.tokens[self.pos][0])
            return False
        # Выполнение else_stmt не обязательно и не повлияет на выполнение if_stmt
        if (self.tokens[self.pos][1] == "ELSE"):
            if (not self.else_stmt()):
                return False
        return True

    # else_stmt -> KW_ELSE brace_open expr* brace_close
    def else_stmt(self):
        if (not self.KW_ELSE()):
            return False
        elif (not self.brace_open()):
            self.parseExeption("{", self.tokens[self.pos][0])
            return False
        while (True):  # эквивалентно expr* - выполняется 0 или более раз
            if (not self.expr()):
                break
        if (not self.brace_close()):
            self.parseExeption("}", self.tokens[self.pos][0])
            return False
        return True

    def KW_IF(self):
        if (self.tokens[self.pos][1] == "IF"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def KW_ELSE(self):
        if (self.tokens[self.pos][1] == "ELSE"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

            # printing -> KW_PRINT bkt_open arif_stmt bkt_close semicolon

    def printing(self):
        if (not self.KW_PRINT()):
            return False
        elif (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.str_stmt()):
            self.parseExeption("string or arithmetic expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        elif (not self.semicolon()):
            self.parseExeption(";", self.tokens[self.pos][0])
            return False
        else:
            return True

    def KW_PRINT(self):
        if (self.tokens[self.pos][1] == "PRINT"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # str_stmt -> substr (concat substr)*
    def str_stmt(self):
        if (not self.substr()):
            return False
        while (True):  # эквивалентно (concat substr)*
            if (not self.concat() and not self.substr()):
                break
        return True

    # substr -> string | arif_stmt
    def substr(self):
        if (
                self.string() or
                self.arif_stmt()
        ):
            return True
        else:
            return False

    def string(self):
        if (self.tokens[self.pos][1] == "STRING"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def concat(self):
        if (self.tokens[self.pos][1] == "CONCAT"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # inputting -> KW_INPUT bkt_open var bkt_close semicolon
    def inputting(self):
        if (not self.KW_INPUT()):
            return False
        elif (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.var()):
            self.parseExeption("variable", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        elif (not self.semicolon()):
            self.parseExeption(";", self.tokens[self.pos][0])
            return False
        else:
            return True

    def KW_INPUT(self):
        if (self.tokens[self.pos][1] == "INPUT"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # while_stmt -> KW_WHILE bkt_open log_stmt bkt_close brace_open expr* brace_close
    def while_stmt(self):
        if (not self.KW_WHILE()):
            return False
        elif (not self.bkt_open()):
            self.parseExeption("(", self.tokens[self.pos][0])
            return False
        elif (not self.log_stmt()):
            self.parseExeption("logical expression", self.tokens[self.pos][0])
            return False
        elif (not self.bkt_close()):
            self.parseExeption(")", self.tokens[self.pos][0])
            return False
        elif (not self.brace_open()):
            self.parseExeption("{", self.tokens[self.pos][0])
            return False
        while (True):  # эквивалентно expr* - выполняется 0 или более раз
            if (not self.expr()):
                break
        if (not self.brace_close()):
            self.parseExeption("}", self.tokens[self.pos][0])
            return False
        return True

    def KW_WHILE(self):
        if (self.tokens[self.pos][1] == "WHILE"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def brace_open(self):
        if (self.tokens[self.pos][1] == "BRACE_OPEN"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def brace_close(self):
        if (self.tokens[self.pos][1] == "BRACE_CLOSE"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def bkt_open(self):
        if (self.tokens[self.pos][1] == "BRACKET_OPEN"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def bkt_close(self):
        if (self.tokens[self.pos][1] == "BRACKET_CLOSE"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

            # Не обязателен, поэтому всегда возвращает True, чтобы не прерывать программу, главное

    # что он запишется в список токенов если есть
    def inc_dec(self):
        if (
                self.tokens[self.pos][1] == "INC" or
                self.tokens[self.pos][1] == "DEC"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        return False

    def arif_op(self):
        if (
                self.tokens[self.pos][1] == "MULT" or
                self.tokens[self.pos][1] == "PLUS" or
                self.tokens[self.pos][1] == "MINUS" or
                self.tokens[self.pos][1] == "DIVISION" or
                self.tokens[self.pos][1] == "MOD" or
                self.tokens[self.pos][1] == "POW"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def log_op(self):
        if (
                self.tokens[self.pos][1] == "AND" or
                self.tokens[self.pos][1] == "OR" or
                self.tokens[self.pos][1] == "XOR"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def comp_op(self):
        if (
                self.tokens[self.pos][1] == "GRATER_EQ" or
                self.tokens[self.pos][1] == "GRATER" or
                self.tokens[self.pos][1] == "LESS_EQ" or
                self.tokens[self.pos][1] == "LESS" or
                self.tokens[self.pos][1] == "EQUAL" or
                self.tokens[self.pos][1] == "NOT_EQUAL"
        ):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def log_not(self):
        if (self.tokens[self.pos][1] == "NOT"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    def semicolon(self):
        if (self.tokens[self.pos][1] == "SEMICOLON"):
            self.pushInStack(self.tokens[self.pos])
            self.pos += 1
            return True
        else:
            return False

    # Возвращает значение в его изначальном типе для полиза
    def valInTruthType(self, value):
        if (value[1] == "INT"):
            return int(value[0])
        elif (value[1] == "FLOAT"):
            return float(value[0])
        elif (value[1] == "BOOL"):
            if value[0] == "True":
                return True
            else:
                return False
        else:
            return value[0]

    # Если входной токен число, переменная или ключ.слова ветвлений\циклов,
    # то добавляем его в общий стек. Иначе, добавляем токен в промежуточный стек(buffer)
    # buffer хранит операции, чтобы в правильном порядке формировать ПОЛИЗ в основном стеке
    def pushInStack(self, el):
        # print(self.poliz)
        # print(str(self.buffer) + "\n====")
        if (el[1] in
                ["INT", "FLOAT", "BOOL", "ID", "STRING", "LL", "HS",
                 "GSIZE", "GVALUE", "GFIRST", "GLAST", "GNEXT", "GPREV"]):
            self.poliz.append(self.valInTruthType(el))
        elif (el[1] in ["WHILE", "IF", "ELSE"]):
            self.calls.append(el[1])
            self.buffer.append(el)
            if (el[1] in ["ELSE"]):
                self.buffer.pop()
                self.addrsForFilling.append(len(self.poliz))
                self.poliz.append(0)  # Добавляем любые элементы, для адреса перехода
                self.poliz.append("!")  # И специального символа перехода
            elif (el[1] == "WHILE"):
                self.addrsJumps.append(len(self.poliz))
        else:
            if (el[0] == ")"):  # выталкиваем всё в основной буфер до первой (
                while (self.endEl(self.buffer)[0] != "("):
                    value = self.buffer.pop()
                    self.poliz.append(value[0])
                self.buffer.pop()  # убрали саму "("
                # если в буффере были оператторы ветвления, что фиксируем адрес для заполнения далее
                if (self.endEl(self.buffer)[1] in ["IF", "WHILE"]):
                    self.buffer.pop()
                    self.addrsForFilling.append(len(self.poliz))
                    self.poliz.append(0)  # Добавляем любые элементы, для адреса перехода
                    self.poliz.append("!F")  # И специальный символа перехода
            elif (el[0] == "}"):  # выталкиваем всё в основной буфер до первой {
                while (self.endEl(self.buffer)[0] != "{"):
                    value = self.buffer.pop()
                    self.poliz.append(value[0])
                self.buffer.pop()  # убрали саму "{"
                lastCall = self.calls.pop()
                if (lastCall == "WHILE"):
                    self.poliz.append(self.addrsJumps.pop())
                    self.poliz.append("!")
                    self.poliz[self.addrsForFilling.pop()] = len(self.poliz)
                elif (lastCall == "IF"):
                    self.poliz[self.addrsForFilling.pop()] = len(self.poliz)
                elif (lastCall == "ELSE"):
                    self.poliz[self.addrsForFilling.pop()] = len(self.poliz)
                else:
                    # выполнится только если было IF без ELSE и для нормального ветвления,
                    # нужная заглушка. Если ELSE был, то на этот адрес будет записан адрес безусловного перехода
                    self.poliz.append(None)
            elif (el[0] != "(" and el[0] != "{" and len(self.buffer) != 0):
                # Если новый токен имеет меньший приоритет, чем последний в буффере, то
                # последний из буффера добавялется в основной стек, а новый заносится в буффер
                if (el[2] < self.endEl(self.buffer)[2]):
                    if (el[1] == "SEMICOLON"):
                        # если встретился конец выражения, то переносим всё из буфера в основнйо стек
                        while (not self.endEl(self.buffer)[0] in
                                   ["=", "-=", "+=", "*=", "/=", "//=", "print", ".", "input", "add"]):
                            val = self.buffer.pop()
                            self.poliz.append(val[0])
                    val = self.buffer.pop()
                    self.poliz.append(val[0])

            if (not el[0] in [";", ")", "}"]):
                self.buffer.append(el)

    def endEl(self, n):
        return 0 if (len(n) == 0) else n[len(n) - 1]


def do_parse(tokens):
    p = Parser(tokens)
    if (p.parse()):
        return p.poliz