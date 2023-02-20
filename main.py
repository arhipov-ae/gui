import os
import cv2
import shutil
import numpy as np
import sys
import json
import math
import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QImage, QFont, QResizeEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
    QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QMainWindow, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint, QRect
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import (QGraphicsRectItem, QApplication, QGraphicsView,
                             QGraphicsScene, QGraphicsItem, QAction)
from test_with_so import Bbox
from select_bbox import Selector_bbox

class SetupWindow(QMainWindow):
    def __init__(self):
        super(SetupWindow, self).__init__()
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.labels = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'rock',
                       'textile', 'wood']
        self.colors = {
            0: QColor(255, 0, 0),
            1: QColor(255, 215, 0),
            2: QColor(0, 255, 0),
            3: QColor(0, 250, 154),
            4: QColor(0, 0, 255),
            5: QColor(148, 0, 211),
            6: QColor(139, 69, 19),
            7: QColor(0, 255, 255),
        }
        # Size area with images
        self.size_one_img = 900
        self.size_frame = 10
        self.size_place_img = self.size_frame + self.size_one_img

        # Size window
        self.width = self.size_place_img + 250
        self.height = self.size_place_img + 50

        # initialize list to save all label buttons
        self.label_buttons = []
        self.label_image = QLabel(self)
        self.label_predicts = []
        self.list_bbox = []
        self.scale_x = 1.0
        self.scale_y = 1.0


        #self.selec = Selector_bbox()
        self.source_dir = '/home/lab5017/dataset_myTrash/stend/img_for_gui'
        self.save_dir = 'dataset'
        self.name_annotation = 'inference.json'
        self.name_folders = os.listdir(self.source_dir)
        self.counter = -1

        self.grview = QGraphicsView()
        self.lay = QGridLayout()
        self.grview.setBaseSize(self.size_place_img, self.size_place_img)

        scene = QGraphicsScene(self.grview)
        scene.setSceneRect(0, 0, self.size_one_img, self.size_one_img)
        self.grview.setScene(scene)

        self.cent_wid = QWidget()
        self.setCentralWidget(self.cent_wid)
        self.lay.addWidget(self.grview)

        self.progress_bar = QLabel()
        self.name_folder = QLabel()
        self.init_ui()

        self.begin, self.destination = QPoint(), QPoint()

    def init_ui(self):
        # self.setMinimumSize(self.width, self.height)
        self.setGeometry(0, 0, self.width, self.height)
        self.old_w = self.size().width()
        self.old_h = self.size().height()
        self.init_buttons()

        self.progress_bar.setFont(QFont("Arial", 10))
        self.progress_bar.setText((f'folder 0 of {len(self.name_folders)}'))

        self.name_folder.move(0, 20)
        self.name_folder.setFont(QFont("Arial", 10))

    def init_buttons(self):

        self.but_widgest = QWidget()

        self.lay_but = QGridLayout()
        self.lay_but.addWidget(self.progress_bar, 0, 0)
        self.lay_but.addWidget(self.name_folder, 1, 0)

        # Add "Prev" and "Next" buttons
        prev_im_btn = QtWidgets.QPushButton("Prev", self)
        prev_im_btn.clicked.connect(self.show_prev)

        self.lay_but.addWidget(prev_im_btn, 2, 0)

        next_im_btn = QtWidgets.QPushButton("Next", self)
        next_im_btn.clicked.connect(self.show_next)

        self.lay_but.addWidget(next_im_btn, 2, 1)

        # Add keyboard shortcuts
        prev_im_kbs = QShortcut(QKeySequence("left"), self)
        prev_im_kbs.activated.connect(self.show_prev)

        next_im_kbs = QShortcut(QKeySequence("right"), self)
        next_im_kbs.activated.connect(self.show_next)

        next_im_kbs = QShortcut(QKeySequence("escape"), self)
        next_im_kbs.activated.connect(self.reset_flag_bbox)

        # Create button for each label
        x_shift = 0  # variable that helps to compute x-coordinate of button in UI
        y_shift = 0
        for i, label in enumerate(self.labels):
            self.label_buttons.append(QtWidgets.QPushButton(label, self))     #QRadioButton
            button = self.label_buttons[i]
            button.setStyleSheet("background-color:rgb{}".format(self.colors[i].getRgb()[0:3]))

            # create click event (set label)
            button.clicked.connect(lambda state, x=label: self.set_label(x))

            # create keyboard shortcut event (set label)
            # shortcuts start getting overwritten when number of labels >9
            label_kbs = QShortcut(QKeySequence(f"{i + 1 % 10}"), self)
            label_kbs.activated.connect(lambda x=label: self.set_label(x))

            # place button in GUI (create multiple columns if there is more than 10 button)
            y_shift = (30 + 10) * (i % 10)
            if (i != 0 and i % 10 == 0):
                x_shift += 120
                y_shift = 0

            self.lay_but.addWidget(button, i + 3, 0)

        del_bbox_bt = QtWidgets.QPushButton("delete", self)

        del_bbox_bt.clicked.connect(self.delete_bbox)

        del_bbox_kbs = QShortcut(QKeySequence("delete"), self)
        del_bbox_kbs.activated.connect(self.delete_bbox)

        self.lay_but.setSpacing(20)
        self.lay_but.addWidget(del_bbox_bt, len(self.labels) + 4, 0)

        res_bbox_bt = QtWidgets.QPushButton("reset", self)
        res_bbox_bt.clicked.connect(self.reset_predict)
        self.lay_but.addWidget(res_bbox_bt, len(self.labels) + 5, 0)

        self.lay_but.setRowStretch(self.lay_but.rowCount(), 1)

        self.but_widgest.setLayout(self.lay_but)
        self.lay.addWidget(self.but_widgest, 0, 1)
        self.cent_wid.setLayout(self.lay)

    def resizeEvent(self, QResizeEvent):
        """ Если пользователь меняет рамзер окна, то растягивается картинка """

        super().resizeEvent(QResizeEvent)
        scale_w = self.size().width() / self.old_w
        scale_h = self.size().height() / self.old_h
        print(scale_w)
        print(scale_h)
        self.grview.scale(scale_w, scale_h)
        self.old_w = self.size().width()
        self.old_h = self.size().height()

    def delete_bbox(self):
        """ Удаляются все выделенные объекты """

        bbox_flags = []
        for bbox in self.list_bbox:
            if bbox.flagPress == 1:
                bbox.human_change = 'delete'
                bbox_flags.append(bbox)
        for bbox_delete in bbox_flags:
            self.grview.scene().removeItem(bbox_delete)
            #self.list_bbox.remove(bbox_delete)
        self.grview.scene().update()

    def set_label(self, label):
        """ Изменение пользователем лейблов для Bbox"""

        bbox_flags = []
        for bbox in self.list_bbox:
            if bbox.flagPress == 1:
                bbox_flags.append(self.list_bbox.index(bbox))
        if len(bbox_flags) == 1:
            bbox_reset = self.list_bbox[bbox_flags[0]]
            bbox_reset.name_class = label
            bbox_reset.color = self.colors[self.labels.index(label)]
            line = bbox_reset.line.rsplit('=', 1)[0]
            bbox_reset.line = line + '=' + label + '\n'
            bbox_reset.human_change = 'class'
            bbox_reset.reset_flag()

    def reset_flag_bbox(self):
        """ Убираются все выделения с Bbox """

        self.grview.scene().items().clear()
        for Bbox in self.list_bbox:
            Bbox.reset_flag()


    def inference(self):
        """Симулияция инференса """

        confidence = np.random.rand(len(self.labels))
        confidence[np.random.randint(len(self.labels))] += 4
        conf_softmax = np.exp(confidence) / np.sum(np.exp(confidence))
        assert len(conf_softmax) == len(self.labels)
        return dict(zip(self.labels, list(conf_softmax)))

    def reset_predict(self):
        """ Удаление разметки и запуск нового предсказания"""
        path_to_file = os.path.join(self.source_dir, self.name_folders[self.counter],
                                    self.name_annotation)
        if os.path.isfile(path_to_file) == True:
            self.save_previous_state()
            os.remove(path_to_file)
            self.load_new_state()
            #self.save_previous_state()



    def convert_coord(self, ccord):
        """ Пребразование координат с поворотом в координаты с горизонтальными и вертикальными сторонами """

        x_old = [ccord[0], ccord[2], ccord[4], ccord[6]]
        y_old = [ccord[1], ccord[3], ccord[5], ccord[7]]
        x1 = int(min(x_old) / self.scale_x)
        y1 = int(max(y_old) / self.scale_y)

        x2 = int(max(x_old) / self.scale_x)
        y2 = int(min(y_old) / self.scale_y)
        return x1, y1, x2 - x1, y2 - y1

    def load_bbox(self):
        """Парсит исходный txt-файл с прямоугольниками от сегментации и вызывает для каждой inference """

        path = os.path.join(self.source_dir, self.name_folders[self.counter])
        infer = False
        if os.path.isfile(os.path.join(path, self.name_annotation)) == True:
            annot_txt = open(os.path.join(path, self.name_annotation), 'r')
            annot = json.load(annot_txt)
            infer = True

        file = open(os.path.join(self.source_dir, self.name_folders[self.counter],
                                 self.name_folders[self.counter] + '.txt'), 'r')

        lines = file.readlines()
        for line in lines:
            id_txt = line.split('=')[0]
            coord_list_txt = line.split('=')[1].split(':')
            coord_src = [int(i) for i in coord_list_txt]
            l1 = int(math.sqrt((coord_src[3] - coord_src[1]) ** 2 + (coord_src[2] - coord_src[0]) ** 2))
            l2 = int(math.sqrt((coord_src[5] - coord_src[3]) ** 2 + (coord_src[4] - coord_src[2]) ** 2))

            coord = self.convert_coord(coord_src)
            item = Bbox(*coord)
            item.width_src = min(l1, l2)
            item.height_src = max(l1, l2)

            if infer:
                if id_txt in list(annot['objects'].keys()):
                    name_class = annot['objects'][id_txt]['name_class']
                    item.human_change = annot['objects'][id_txt]['human_change']
                    item.predict = annot['objects'][id_txt]['predict']

            else:
                predict = self.inference()
                item.predict = predict
                max_class = np.argmax(list(predict.values()))
                name_class = self.labels[max_class]
                line = line.replace('\n', '') + '=' + name_class + '\n'

            item.name_class = name_class
            item.line = line
            item.id = id_txt
            item.color = self.colors[self.labels.index(name_class)]
            self.list_bbox.append(item)
        file.close()

    def save_previous_state(self):
        """ Перед тем как отобразить следующее состояние сохраняется предыдущая разметка"""

        output = open(os.path.join(self.source_dir, self.name_folders[self.counter], self.name_annotation), 'w')
        to_json = {}
        to_json['folder'] = self.name_folders[self.counter]
        to_json['date'] = datetime.datetime.fromtimestamp(int(self.name_folders[self.counter])/1000.0).strftime('%m/%d/%Y')
        to_json['architecture'] = 'ConvNeXt_large'
        to_json['weights'] = '/home/lab5017/mmclassification/work_dirs/convnext_large_our_data_1666952342.2279491/latest.pth'
        to_json['config'] = '/home/lab5017/mmclassification/convnext_large.py'
        to_json['objects'] = {}
        for Bbox in self.list_bbox:
            object_descr = {}
            #object_descr['id'] = Bbox.id
            object_descr['width'] = Bbox.width_src
            object_descr['height'] = Bbox.height_src
            object_descr['name_class'] = Bbox.name_class
            object_descr['human_change'] = Bbox.human_change
            object_descr['predict'] = Bbox.predict

            to_json['objects'][Bbox.id] = object_descr

        output.write(json.dumps(to_json))
        output.close()
        self.list_bbox = []
       # self.update()
        self.grview.scene().items().clear()


    def draw_bbox(self):
        """ Добавляются на сценну BBox и отображаются"""

        for Bbox in self.list_bbox:
            if Bbox.human_change != 'delete':
                self.grview.scene().addItem(Bbox)

    def load_new_state(self):
        """ Отображет картинку и Bbox по вызову пользователя"""

        path_to_img = os.path.join(self.source_dir, self.name_folders[self.counter],
                                   self.name_folders[self.counter] + '.jpg')

        img = cv2.imread(path_to_img)
        img_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.scale_x = img_np.shape[1] / self.size_one_img
        self.scale_y = img_np.shape[0] / self.size_one_img

        self.load_bbox()
        img_np = cv2.resize(img_np, (self.size_one_img, self.size_one_img))
        height, width, channel = img_np.shape
        bytesPerLine = 3 * width
        qImg = QImage(img_np.data, width, height, bytesPerLine, QImage.Format_RGB888)


        #self.grview.scene().addPixmap(QPixmap.fromImage(qImg))
        # ToDO надо реализовать функцию для определения внутреннних прямоугольников
        self.grview.scene().addWidget(Selector_bbox(QPixmap.fromImage(qImg), self.size_one_img, self.list_bbox))

        self.progress_bar.setText(f'folder {self.counter} of {len(self.name_folders)}')
        self.name_folder.setText(self.name_folders[self.counter])
        self.draw_bbox()

    def show_prev(self):
        """ Уменьшает счетчик на 1 и азпускает отображение картинок с bbox """

        if self.counter >= 1:
            self.save_previous_state()

            self.counter -= 1
            if not os.path.isfile(os.path.join(self.source_dir, self.name_folders[self.counter],
                                               self.name_folders[self.counter] + '.txt')):
                self.counter -= 1  # Возникают случаи, когда в папке есть только картинка со сценой,
                                   # но сегментация объектов не нашла
            self.load_new_state()

    def show_next(self):
        """ Функция по нажатию кнопки или по клавише изменяет счетчик с папкой и
        вызывает функцию отображения картинки с предсказаниями  """

        if self.counter < len(self.name_folders) - 1:
            self.save_previous_state()

            self.counter += 1
            if not os.path.isfile(os.path.join(self.source_dir, self.name_folders[self.counter],
                                               self.name_folders[self.counter] + '.txt')):
                self.counter += 1
            self.load_new_state()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SetupWindow()
    ex.show()
    sys.exit(app.exec_())
