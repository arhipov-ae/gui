import sys
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen, QPixmap, QFont
from PyQt5.QtWidgets import QGraphicsRectItem, QApplication, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QLabel


class Bbox(QGraphicsRectItem):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, *args):
        super(Bbox, self).__init__(*args)
        """ Инициализируйте форму. """

        super().__init__(*args)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None

        self.flagPress = 0
        self.name_class = 'metal'
        self.id = ''
        self.line = ''
        self.predict = {}
        self.width_src = 0
        self.height_src = 0
        self.human_change = 'ok'  # class, delete, ok

        self.color = QColor(0, 0, 0)
        self.label_class = QLabel(self.scene())

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()



    def handleAt(self, point):
        """ Возвращает маркер изменения размера ниже заданной точки. """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def reset_flag(self):
        self.flagPress = 0
        self.scene().update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset_flag()

    def upload_flag(self):
        self.flagPress = 1
        self.scene().update()

    def mousePressEvent(self, mouseEvent):
        """ Выполняется при нажатии мыши на элемент. """

        if self.flagPress == 1:
            self.flagPress = 0
        else:
            self.flagPress = 1
        self.scene().update()

    def boundingRect(self):
        """ Возвращает ограничивающий прямоугольник фигуры
            (включая маркеры изменения размера). """
        o = self.handleSize + self.handleSpace

        return self.rect().adjusted(-o, -o, o, o)
    #
    def updateHandlesPos(self):
        """ Обновите текущие маркеры изменения размера
            в соответствии с размером и положением фигуры. """

        s = self.handleSize
        b = self.boundingRect()

        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)


    def shape(self):
        """ Возвращает форму этого элемента в виде QPainterPath в локальных координатах. """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """ Нарисуйте узел в графическом представлении. """
        if self.flagPress == 1:
            painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0, 0)))

        painter.setPen(QPen(self.color, 1.0, Qt.SolidLine))
        painter.drawRect(self.rect())
        painter.setFont(QFont("Arial", 20))

        painter.drawText(self.rect().bottomLeft(), self.name_class)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))



        for handle, rect in self.handles.items():
            if self.handleSelected is None or handle == self.handleSelected:
                painter.drawEllipse(rect)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    grview = QGraphicsView()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)
    grview.setScene(scene)
    grview.show()
    item = Bbox(0, 300, 100, 600)
    scene.addItem(item)


    sys.exit(app.exec_())
