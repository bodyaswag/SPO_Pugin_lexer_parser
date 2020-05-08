from HashSet import HashSet
from LinkedList import LinkedList


# Стек-машина, которая выполняет сам код
class StackMachine:
    def __init__(self, poliz):
        self.poliz = poliz  # ПОльская ИНверсная запись, полученная после парсера
        self.stack = []  # основной стек для выполнения операций
        self.variables = {}  # cловарь c переменными: varID -> varValue
        self.pos = 0  # номер текущего элемента полиза

    # выполняет вычисление на стек машине, пока не дошли до конца ПОЛИЗа
    def process(self):
        while (self.pos < len(self.poliz)):
            self.stack.append(self.poliz[self.pos])
            self.pos += 1
            stackHead = self.stack.pop()

            if (stackHead == "!"):
                self.pos = self.stack.pop()  # безусловный переход по адресу
            elif (stackHead == "!F"):
                adr = self.stack.pop()
                if (not self.stack.pop()):
                    self.pos = adr
            elif (stackHead == "print"):
                self.printing(self.stack.pop())
            elif (stackHead == "input"):
                self.inputting(self.stack.pop())
            elif (stackHead != None):
                # если на вершине стека какая-то операция над операндами, то выполняем
                if (stackHead in
                        ["+=", "+", "//=", "//", "/=", "/", "**", "*=", "*", "-=", "-",
                         "not", "and", "or", "xor", ">=", ">", "<=", "<", "==",
                         "=", "!=", "add", "inSet", "getValue", "getSize",
                         "getFirst", "getLast", "getNext", "getPrev", "."]):
                    self.calculate(stackHead)
                else:
                    self.stack.append(stackHead)
            else:
                self.pushError("Error: unexpected " + stackHead)

    def printing(self, value):
        if (self.variables.get(value) != None):
            print("> " + str(self.variables.get(value)))
        else:
            print("> " + str(value))

    def inputting(self, var):
        if (self.variables.get(var) != None):
            v = str(input(">>"))
            self.variables[var] = self.convertType(v)
        else:
            print("Error: variable '" + var + "' is not defined")
            exit(0)

    def convertType(self, value):
        try:
            if (value.find('"') != -1):
                return str(value)
            elif (value == "True"):
                return True
            elif (value == "False"):
                return False
            elif (value.find('.') != -1):
                return float(value)
            else:
                return int(value)
        except:
            print("Error: unknown type of value '" + value + "'")
            exit(0)

    def calculate(self, op):
        # для унарных операторов берём только 1 значение из стека
        if (not op in ["not", "getFirst", "getLast",
                       "getNext", "getPrev", "getValue", "getSize"]):
            b = self.stack.pop()
            a = self.stack.pop()
        else:
            a = self.stack.pop()

            # Если операция с обхектом, что нужно узнать его адрес
            # Он может быть напрямую в стеке или быть в переменной
            obj_ref = self.variables.get(a) if self.variables.get(a) != None else a

            if op == "getFirst":
                self.stack.append(self.getFirst(obj_ref))
            elif op == "getLast":
                self.stack.append(self.getLast(obj_ref))
            elif op == "getSize":
                self.stack.append(self.getSize(obj_ref))
            elif op == "getNext":
                self.stack.append(self.getNext(obj_ref))
            elif op == "getPrev":
                self.stack.append(self.getPrev(obj_ref))
            elif op == "getValue":
                self.stack.append(self.getValue(obj_ref))
            return

        # сначала проверяем, если это оператор присвоения,
        # то переменная будет перезаписана или проинициализирована
        if (op == "="):
            if b == "LinkedList":
                self.initLL(a)
            elif b == "HashSet":
                self.initHS(a)
            else:
                # Берём имя переменной для инициализации
                b = self.variables.get(b) if type(b) == str else b
                self.assign(a, b)
        # В противном случае, в других операциях будут использоваться уже сущ. переменные или числа
        else:
            # для операторов которые меняют значение переменной, нужно имя переменной для обращения и второе число
            b = self.variables.get(b) if self.variables.get(b) != None else b

            if op == "inSet":
                self.stack.append(self.inSet(a, b))
            elif op == "add":
                self.add(a, b)
            elif (op == "-="):
                self.minusAssign(a, b)
            elif (op == "+="):
                self.plusAssign(a, b)
            elif (op == "*="):
                self.multAssign(a, b)
            elif (op == "/="):
                self.divAssign(a, b)
            elif (op == "//="):
                self.modAssign(a, b)
            else:
                # для других операторов нужно только значение двух операндов,
                # получаем значение второго и выполняем
                a = self.variables.get(a) if self.variables.get(a) != None else a

                if (op == "."):
                    self.stack.append(self.concat(a, b))
                elif (op == "+"):
                    self.stack.append(self.plus(a, b))
                elif (op == "-"):
                    self.stack.append(self.minus(a, b))
                elif (op == "*"):
                    self.stack.append(self.mult(a, b))
                elif (op == "**"):
                    self.stack.append(self.pow(a, b))
                elif (op == "/"):
                    self.stack.append(self.div(a, b))
                elif (op == "//"):
                    self.stack.append(self.mod(a, b))
                elif (op == "and"):
                    self.stack.append(self.l_and(a, b))
                elif (op == "or"):
                    self.stack.append(self.l_or(a, b))
                elif (op == "xor"):
                    self.stack.append(self.l_xor(a, b))
                elif (op == ">"):
                    self.stack.append(self.l_greater(a, b))
                elif (op == ">="):
                    self.stack.append(self.l_greaterEq(a, b))
                elif (op == "<"):
                    self.stack.append(self.l_less(a, b))
                elif (op == "<="):
                    self.stack.append(self.l_lessEq(a, b))
                elif (op == "!="):
                    self.stack.append(self.l_notEq(a, b))
                elif (op == "=="):
                    self.stack.append(self.l_equal(a, b))
                elif (op == "not"):
                    self.stack.append(self.l_not(a))

    def concat(self, val1, val2):
        return str(val1) + str(val2)

    def assign(self, num1, num2):
        try:
            self.variables[num1] = self.variables[num2] if self.variables.get(num2) != None else num2
        except:
            self.pushError("Error: " + str(num1) + " are not defined")

    def plus(self, num1, num2):
        try:
            return num1 + num2
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " + " + str(num2))

    def minus(self, num1, num2):
        try:
            return num1 - num2
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " - " + str(num2))

    def mult(self, num1, num2):
        try:
            return num1 * num2
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " * " + str(num2))

    def pow(self, num1, num2):
        try:
            return num1 ** num2
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " ** " + str(num2))

    def div(self, num1, num2):
        if num2 == 0:
            self.pushError("Error: division by zero")
        try:
            return float(num1) / float(num2)
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " / " + str(num2))

    def mod(self, num1, num2):
        if (type(num1) == float or type(num2) == float):
            self.pushError("Error: modulus from float")
        elif num2 == 0:
            self.pushError("Error: modulus by zero")
        try:
            return num1 % num2
        except:
            self.pushError("Error: impossible operation: " + str(num1) + " // " + str(num2))

    def minusAssign(self, var, num):
        self.variables[var] = self.minus(self.variables.get(var), num)

    def plusAssign(self, var, num):
        self.variables[var] = self.plus(self.variables.get(var), num)

    def multAssign(self, var, num):
        self.variables[var] = self.mult(self.variables.get(var), num)

    def divAssign(self, var, num):
        self.variables[var] = self.div(self.variables.get(var), num)

    def modAssign(self, var, num):
        self.variables[var] = self.mod(self.variables.get(var), num)

    def l_greater(self, num1, num2):
        try:
            return num1 > num2,
        except:
            self.compareException(num1, num2)

    def l_greaterEq(self, num1, num2):
        try:
            return num1 >= num2
        except:
            self.compareException(num1, num2)

    def l_less(self, num1, num2):
        try:
            return num1 < num2
        except:
            self.compareException(num1, num2)

    def l_lessEq(self, num1, num2):
        try:
            return num1 <= num2
        except:
            self.compareException(num1, num2)

    def l_notEq(self, num1, num2):
        try:
            return num1 != num2
        except:
            self.compareException(num1, num2)

    def l_equal(self, num1, num2):
        try:
            return num1 == num2
        except:
            self.compareException(num1, num2)

    def l_not(self, num):
        if (type(num) == bool):
            return not num
        else:
            self.pushError("Error: using LOGICAL NOT for non-logical expression")

    def l_or(self, num1, num2):
        if (type(num1) == bool and type(num2) == bool):
            return num1 or num2
        else:
            self.pushError("Error: using LOGICAL OR for non-logical expression")

    def l_and(self, num1, num2):
        if (type(num1) == bool and type(num2) == bool):
            return num1 and num2
        else:
            self.pushError("Error: using LOGICAL AND for non-logical expression")

    def l_xor(self, num1, num2):
        if (type(num1) == bool and type(num2) == bool):
            return ((not num1) and num2) or ((num1 and (not num2)))
        else:
            self.pushError("Error: using LOGICAL XOR for non-logical expression")

    def initLL(self, var):
        try:
            self.variables[var] = LinkedList()
        except:
            self.pushError("Error: impossible initialization Linked List")

    def initHS(self, var):
        try:
            self.variables[var] = HashSet()
        except:
            self.pushError("Error: impossible initialization Hash Set")

    def add(self, obj, val):
        try:
            self.variables[obj].add(val)
        except:
            self.pushError("Error: " + str(obj) + " has no add method")

    def inSet(self, obj, val):
        try:
            return self.variables[obj].inSet(val)
        except:
            self.pushError("Error: " + str(obj) + " has no inSet method")

    def getSize(self, obj):
        try:
            return obj.getSize()
        except:
            self.pushError("Error: " + str(obj) + " has no getSize method")

    def getFirst(self, obj):
        try:
            return obj.getFirst()
        except:
            self.pushError("Error: " + str(obj) + " has no getFirst method")

    def getLast(self, obj):
        try:
            return obj.getLast()
        except:
            self.pushError("Error: " + str(obj) + " has no getLast method")

    def getNext(self, obj):
        try:
            return obj.getNext()
        except:
            self.pushError("Error: " + str(obj) + " has no getNext method")

    def getPrev(self, obj):
        try:
            return obj.getPrev()
        except:
            self.pushError("Error: " + str(obj) + " has no getPrev method")

    def getValue(self, obj):
        try:
            return obj.getValue()
        except:
            self.pushError("Error: " + str(obj) + " has no getValue method")

    def pushError(self, error):
        print(error)
        exit(0)

    def compareException(self, n1, n2):
        self.pushError("Error: impossible to compare '" +
                       str(n1) + "' and '" + str(n2) + "' values")


def do_calculate(poliz):
    machine = StackMachine(poliz)
    machine.process()
