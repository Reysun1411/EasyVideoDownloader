from tkinter.filedialog import askdirectory

class PathEditing:
    def __init__(self, combobox, pathsfile):
        self.cb = combobox
        self.pathsfile = pathsfile

    # Получение путей из paths.txt
    def set(self):
        with open('paths.txt', 'r', encoding='UTF-8') as f:
            paths = f.read().split('\n')
            for path in paths:
                if not path:
                    paths.remove(path)
            if paths:
                print('| Загружены пути из paths.txt: ',paths)
                self.cb.addItems(paths)

    # Добавление пути
    def add(self):
        path = askdirectory(title='Выберите путь для сохранения файла')
        if path:
            self.cb.addItem(path)
            index = self.cb.findText(path)
            self.cb.setCurrentIndex(index)
            print('| Добавлен путь: ',path)
            self.update()

    # Удаление выбранного пути
    def remove(self):
        currentIndex = self.cb.currentIndex()
        currentName = self.cb.itemText(currentIndex)
        if currentIndex >= 0:
            self.cb.removeItem(currentIndex)
            print('| Удален путь: ', currentName)
            self.update()

    # Обновление paths.txt
    def update(self):
        allpaths = []
        try:
            for i in range(self.cb.count()):
                if self.cb.itemText(i):
                    allpaths.append(str(self.cb.itemText(i)))

            if not allpaths:
                towrite = ''
            elif allpaths.count == 1:
                towrite = allpaths[0]
            else:
                towrite = '\n'.join(allpaths)

            with open('paths.txt', 'w', encoding='UTF-8') as f:
                f.write(towrite)
            print('| paths.txt обновлен')
        except Exception as e: print(e)