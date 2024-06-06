from tkinter.filedialog import askdirectory

class PathEditing:
    def __init__(self, combobox, pathfile):
        self.cb = combobox
        self.pfile = pathfile

    # Получение путей из paths.txt
    def set(self):
        with open('paths.txt', 'r', encoding='UTF-8') as f:
            paths = f.read().split('\n')
            if paths:
                self.cb.addItems(paths)

    # Добавление пути
    def add(self):
        path = askdirectory(title='Выберите путь для сохранения файла')
        if path:
            print('| Выбран путь: ',path)
            self.cb.addItem(path)
            self.update()

    # Удаление выбранного пути
    def remove(self):
        if self.cb.currentIndex() >= 0:
            self.cb.removeItem(self.cb.currentIndex())
            self.update()

    def update(self):
        # Обновление paths.txt
        allpaths = []
        for i in range(self.cb.count()):
            if not self.cb.itemText(i):
                self.cb.removeItem(i)
            else:
                allpaths.append(str(self.cb.itemText(i)))
        with open('paths.txt', 'w', encoding='UTF-8') as f:
            f.write('\n'.join(allpaths))
        print('| paths.txt обновлен')