from LinkedList import LinkedList


class HashSet:
    def __init__(self):
        self.count = 16  # Определяет количество индексов для hash set
        # инициализация списка из LinkedList в количестве count
        self.list = [LinkedList() for i in range(self.count)]
        self.__size = 0

    def add(self, element):
        indx = abs(hash(element)) % self.count
        head = self.list[indx].getFirst()
        # Идём до конца списка на конкретном индексе
        for i in range(self.list[indx].getSize()):
            # Если попытка добавить уже существующий элемент, просто выходим
            if element == head.getValue():
                return
            else:
                # иначе дальше движемся до конца списка
                head = head.getNext()
        # Если прошли по всему списку, то идентичных элементов нет и новый можно добавлять
        self.list[indx].add(element)
        self.__size += 1

    def getSize(self):
        return self.__size

    def inSet(self, element):
        indx = abs(hash(element)) % self.count
        head = self.list[indx].getFirst()
        for i in range(self.list[indx].getSize()):
            if element == head.getValue():
                return True
            else:
                head = head.getNext()
        return False

    def print(self):
        for i in range(self.count):
            print(str(i) + " : ", end="")
            head = self.list[i].getFirst()
            for j in range(self.list[i].getSize()):
                print(str(head.getValue()), end=" ")
                head = head.getNext()
            print("")

