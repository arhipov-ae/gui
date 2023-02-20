import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter


class Selector_bbox(QWidget):
    def __init__(self, Pixmap, size, bboxes):
        super(Selector_bbox, self).__init__()
        self.setMinimumSize(size, size)
        self.pix = Pixmap
        self.list_bbox = bboxes

        self.begin, self.destination = QPoint(), QPoint()

    def check_intersection(self, rectangle):
        for bbox in self.list_bbox:
            if bbox.human_change != 'delete':
                if rectangle.contains(bbox.rect().toRect()):
                    bbox.upload_flag()
                else:
                    bbox.reset_flag()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)

        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            self.check_intersection(rect)
            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            self.begin, self.destination = QPoint(), QPoint()
            self.update()


if __name__ == '__main__':
    # don't auto scale when drag app to a different monito
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    myApp = Selector_bbox()
    myApp.show()

    # grview = QGraphicsView()
    # scene = Selector_bbox()
    # scene.setSceneRect(0, 0, 680, 459)
    # grview.setScene(scene)
    # grview.setMouseTracking(True)
    # grview.show()


    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
