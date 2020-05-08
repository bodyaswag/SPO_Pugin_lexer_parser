class LinkedList:
    def __init__(self, value=None):
        self.__size = 0
        self.__first = Node()
        self.__last = Node()

    def add(self, value):
        # Если введён самый первый элемент списка
        if (self.__first.value == None):
            self.__first = Node(value, value, value)
            self.__last = self.__first
        else:
            # Запоминаем редыдущий последний элемент
            oldEndNode = self.getLast()
            # Добавялем новый последний элемент
            self.__last = Node(value, self.getFirst(), oldEndNode)
            # Предыдущий последний теперь будет ссылаться на новый послений элемент
            oldEndNode.setNext(self.getLast())
            # Самый первый элемент должен ссылаться на новый последний
            self.getFirst().setPrev(self.getLast())
        self.__size += 1

    def delete(self, node):
        node.getPrev().setNext(node.getNext())
        node.getNext().setPrev(node.getPrev())
        self.__size -= 1

    def getLast(self):
        return self.__last

    def getFirst(self):
        return self.__first

    def getSize(self):
        return self.__size

    def print(self):
        head = self.getFirst()
        for i in range(0, self.getSize()):
            print(str(head.value), end=" ")
            head = head.getNext()


class Node:
    def __init__(self, value=None, next=None, prev=None):
        self.value = value
        self.__next = next
        self.__prev = prev

    def delete(self):
        self.getNext().setPrev(self.getPrev())
        self.getPrev().setNext(self.getNext())

    def getValue(self):
        return self.value

    def setNext(self, next):
        self.__next = next

    def setPrev(self, prev):
        self.__prev = prev

    def getNext(self):
        return self.__next

    def getPrev(self):
        return self.__prev


