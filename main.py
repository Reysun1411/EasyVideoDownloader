import json
import os.path

from mainwindow import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from tkinter.filedialog import askdirectory, asksaveasfilename
from tkinter import messagebox
import yt_dlp
import sys
from PIL import Image
from io import BytesIO
import requests
import subprocess
import webbrowser
from pathediting import PathEditing

path = 'paths.txt'

url = ''
forbiddenchar = set('/\\*"<>:|?')

class MyWin(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        global pathEditor
        pathEditor = PathEditing(combobox=self.ui.pathComboBox,
                                 pathfile=path)
        # Получение путей из path.txt
        pathEditor.set()
        # Инициализация GUI
        self.ui.applylinkButton.clicked.connect(self.applyVideo)
        self.ui.addpathButton.clicked.connect(self.addPath)
        self.ui.removepathButton.clicked.connect(self.removePath)
        self.ui.downloadVideoAudioButton.clicked.connect(self.save)
        self.ui.downloadVideoButton.clicked.connect(self.save)
        self.ui.downloadAudioButton.clicked.connect(self.save)
        self.ui.thumbnailDownloadButton.clicked.connect(self.saveThumbnail)

    def addPath(self):
        pathEditor.add()
    def removePath(self):
        pathEditor.remove()

    def applyVideo(self):
        preurl = self.ui.ytlinkLine.text()
        self.setProgress(10)
        try:
            ydl_opts = {}
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(preurl, download=False)
        except Exception as e:
            print('| Ошибка! ', e)
            messagebox.showinfo("Ошибка",
                                'Видео недоступно, '
                                'или сайт, на который вы сослались, не поддерживается библиотекой yt-dlp.\n')
            return self.setProgress(0)

        global url
        url = preurl

        try:
            # Получение названия видео
            if self.ui.nameLine.text() == '':
                name = info.get('title')
                name = ''.join(char for char in name if char not in forbiddenchar)
                self.ui.nameLine.setText(name)
            self.setProgress(50)
            # Получение ссылки на превью видео
            thumbUrl = info.get('thumbnail')
            global thumb
            thumb = requests.get(thumbUrl).content
            self.setProgress(75)
            # Установка превью в программу
            image = QImage()
            image.loadFromData(thumb)
            self.ui.thumbnailLabel.setPixmap(QPixmap(image))
            self.setProgress(90)

            self.ui.updateButtons(True)
        except Exception as e:
            print('| Ошибка! ',e)
            messagebox.showinfo("Ошибка", 'Произошла ошибка обработки видео.\nСообщение об ошибке:\n'+str(e))
        self.setProgress(0)

    # Сохранение файла
    def save(self):
        try:
            haveFfmpeg = self.checkFfmpeg()
            if not haveFfmpeg:
                IWannaFFmpeg = messagebox.askyesnocancel('Предупреждение',
                    'На вашем компьютере не установлен набор библиотек FFmpeg. '
                    'Это коснется следующих функций программы:\n'
                    '- Видео не будет скачиваться вместе с аудио, вместо этого '
                    'скачается два отдельных файла: видеоряд в mp4 и аудиоряд в m4a;'
                    '- Аудио будут скачиваться в формате m4a, а не mp3.\n'
                    'Хотите перейти на сайт установки FFmpeg?\n\n'
                    '"Да" - перейти на ffmpeg.org и отменить скачивание;\n'
                    '"Нет" - продолжить скачивание;\n"Отмена" - отменить скачивание.', icon='warning')
                if IWannaFFmpeg is True:
                    webbrowser.open('https://ffmpeg.org')
                    return
                elif IWannaFFmpeg is None:
                    return

            downloadPath = self.ui.pathComboBox.currentText()
            downloadName = self.ui.nameLine.text()
            buttonName = str(self.sender().objectName())

            if not downloadPath:
                messagebox.showinfo("Кринжанул", "Укажите путь для сохранения файла")
                return
            elif not downloadName:
                messagebox.showinfo("Кринжанул", "Отсутствует название файла")
                return
            for i in downloadName:
                if i in forbiddenchar:
                    messagebox.showinfo("Кринжанул", "В названии присутствуют запрещенные символы")
                    return

            add_opt = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'}
            ext = ''
            if buttonName == "downloadVideo":
                add_opt['format'] = 'bestvideo'
                ext = '.mp4'
            elif buttonName == 'downloadAudio':
                add_opt['format'] = 'bestaudio/best'
                add_opt['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '0'}]
                if not haveFfmpeg:
                    ext = '.m4a'

            opt = {'outtmpl': f'{downloadPath}/{downloadName}{ext}',
                   'progress_hooks': [self.downloadingHook],
                   'verbose': True,
                   'ignoreerrors': True,
                   'noplaylist': True}
            opt.update(add_opt)

            self.setProgress(30)

            print('| НАЧАЛО СКАЧИВАНИЯ')
            ydl = yt_dlp.YoutubeDL(opt)
            ydl.download([url])
            print('| СКАЧИВАНИЕ ЗАВЕРШЕНО')
        except yt_dlp.utils.PostProcessingError as e:
            print(e)
            messagebox.showinfo("Ошибка", 'В процессе сохранение файла произошла ошибка.'
                                          '\nСообщение об ошибке:\n' + str(e))
        self.setProgress(0)

    def checkFfmpeg(self):
        try:
            subprocess.check_output('ffmpeg -version',
                                    shell=True, stderr=subprocess.STDOUT)
            return True
        except Exception as e:
            print('| FFMPEG не найден! ', e)
            return False

    # Скачивание превью
    def saveThumbnail(self):
        data = [("Image Files", "*.png *.jpg")]
        filename = asksaveasfilename(filetypes=data, defaultextension=data,
                                     confirmoverwrite=True)
        self.setProgress(50)
        if filename:
            try:
                im = Image.open(BytesIO(thumb))
                im.save(filename)
            except Exception as e:
                print('| Ошибка! ',e)
                messagebox.showinfo("Ошибка", 'В процессе сохранение файла произошла ошибка.'
                                              '\nСообщение об ошибке:\n' + str(e))
        self.setProgress(0)

    # Отслеживание прогресса скачивания
    # Этот метод привязан к параметру скачивания YoutubeDL "progress_hook".
    # Он получает текущий статус скачивания в процентах
    # и выводит его в прогресс-бар.
    def downloadingHook(self, d):
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = p.replace('%', '')
            p = p.replace(' ', '')
            try:
                self.setProgress(int(float(p)))
            except ValueError:
                return

    # Установка значения прогресс-бара
    def setProgress(self, progress):
        self.ui.progressBar.setValue(progress)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Main = MyWin()
    Main.show()
    sys.exit(app.exec_())