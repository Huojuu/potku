import math
import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from dialogs.measurement import import_selection

__SELECT_RADIUS2__ = 0.02


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        self.coord = []
        self.all_xy = []
        self.read_data()
        self.midpoint_coord= self.calculate_midpoints(self.coord)

        self.point_to_move = None
        self.move_handler_id = None

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.axes.fill(*zip(*self.coord), zorder=1, fill=False, color='orange')
        self.sc.axes.scatter(*zip(*self.coord), zorder=3, marker='s', color='orange')
        self.sc.axes.scatter(*zip(*self.midpoint_coord), zorder=2, marker='o', color='gold')
        self.plot()

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.sc.mpl_connect('button_press_event', self.button_press_handler)
        self.sc.mpl_connect('button_release_event', self.button_release_handler)
        self.show()


    def read_data(self):
        f = open(self.import_selection.SelectionDialog.filename, "r")
        lines = f.readlines()
        result = []
        for line in lines:
            k=0
            n=0
            word = ''
            for char in line:
                if char == "#":
                    n = 1
                if n == 1:
                    k = k+1
                    if k >= 12:
                        word = word + char
            word.replace('\n', '')
            result.append(word)
        all_coord = []
        all_xy = []
        for el in result:
            el_coord = el.split(';')
            x_coord = el_coord[0].split(',')
            y_coord = el_coord[1].split(',')
            coord = []
            all_x = []
            all_y = []
            n=0
            for num in x_coord:
                y_point = str(y_coord[n])
                if "\n" in y_point:
                    y_point.replace('\n', '')
                point = [int(x_coord[n]), int(y_point)]
                coord.append(point)
                all_x.append(int(x_coord[n]))
                all_y.append(int(y_point))
                n = n+1
            all_coord.append(coord)
            all_xy.append([all_x, all_y])
        print(all_coord)
        self.coord = all_coord[0]
        self.all_xy = all_xy


    def button_press_handler(self, event):
        point = (event.xdata, event.ydata)
        print(self.find_closest_point(self.coord, point))

        if self.find_closest_point(self.coord, point) and (event.button == 1):
            print("start move point")
            cPoint = self.find_closest_point(self.coord, point)
            self.point_to_move = cPoint[1]
            self.move_handler_id = self.sc.mpl_connect('motion_notify_event', self.point_move_handler)

        if self.find_closest_point(self.midpoint_coord, point) and (event.button == 1):
            print("Midpoint")
            mid_point = self.find_closest_point(self.midpoint_coord, point)
            self.coord.insert(mid_point[1]+1, list(mid_point[2]))
            self.midpoint_coord= self.calculate_midpoints(self.coord)

        if self.find_closest_point(self.coord, point) and (event.button == 3):
            print("remove point")
            cPoint = self.find_closest_point(self.coord, point)
            del self.coord[cPoint[1]]
            self.midpoint_coord= self.calculate_midpoints(self.coord)

        self.plot()
        self.show()

    def button_release_handler(self, event):
        if self.point_to_move and (event.button == 1):
            print("end move point")
            self.point_to_move = None
            self.sc.mpl_disconnect(self.move_handler_id)
            self.move_handler_id = None


    def point_move_handler(self, event):
        if not event.xdata or not event.ydata:
            return
        self.coord[self.point_to_move] = [event.xdata, event.ydata]
        self.midpoint_coord = self.calculate_midpoints(self.coord)
        self.plot()
        self.show()

    def find_closest_point(self, plist, point):
        closest_point = sorted([(self.point_point_distance(x, point), list(enumerate(x))) for x in plist if self.point_point_distance(x, point) < __SELECT_RADIUS2__])
        temp_point_list = []
        for i, x in enumerate(plist):
            print(f'{self.point_point_distance(x, point)}, {i}, {x}')
            temp_point_list.append((self.point_point_distance(x, point), i, x))
        closest_point = sorted([x for x in temp_point_list if x[0] < __SELECT_RADIUS2__])
        return closest_point[0] if closest_point else None


    def point_point_distance(self, point1, point2):
        cPoint1 = self.sc.axes.transLimits.transform(point1)
        cPoint2 = self.sc.axes.transLimits.transform(point2)
        return math.sqrt((cPoint1[0]-cPoint2[0])**2+(cPoint1[1]-cPoint2[1])**2)

    def calculate_midpoints(self, points):
        mid_points = []
        for i in range(len(points)): #calculates middle points (between first and last also
            mid_points.append((((points[i][0] + points[(i+1)%len(points)][0])/2),
                               (points[i][1] + points[(i+1)%len(points)][1])/2))

        return mid_points

    def update_closed_coords(self, points):
        closed_coord = points
        closed_coord.append(points[0])  # repeat the first point to create a 'closed loop'
        return closed_coord

    def plot(self):
        self.sc.axes.clear()
        for el in self.all_xy:
            self.sc.axes.plot(el[0], el[1]) #some backgroung
        self.sc.axes.fill(*zip(*self.coord), zorder=1, fill=False, color='orange')
        self.sc.axes.scatter(*zip(*self.coord), zorder=3, marker='s', color='orange')
        self.sc.axes.scatter(*zip(*self.midpoint_coord), zorder=2, marker='o', color='gold')
        self.sc.draw()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()