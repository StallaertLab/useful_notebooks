from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QGraphicsPolygonItem
import pyqtgraph as pg
import numpy as np

global viewer

class CustomPlot(pg.PlotItem):

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.lassoPoints = []
        self.lasso = QtGui.QPolygonF()
        self.lassoItem = QGraphicsPolygonItem()
        self.lassoItem.setPen(pg.mkPen('g', width=2))
        self.lassoItem.setBrush(pg.mkBrush(0,255,0,50))
        self.addItem(self.lassoItem, ignoreBounds=True)
        
        self.scatter = pg.ScatterPlotItem(size=10)
        self.addItem(self.scatter)

        if (('xx' in kwargs) and ('yy' in kwargs)):
                self.scatter.addPoints(x=kwargs['xx'], y=kwargs['yy'])
 
        if 'org_brush' in kwargs:
            self.org_brush = kwargs['org_brush']
        else:
            self.org_brush = [pg.mkBrush('b') for _ in range(len(xx))]
      
        for i, point in enumerate(self.scatter.points()):
            point.setBrush(self.org_brush[i])


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Left mouse button: start or continue drawing the lasso
            #if not self.lassoPoints:
            self.lassoPoints = [self.vb.mapSceneToView(event.scenePos())]
            self.lasso = QtGui.QPolygonF(self.lassoPoints)
            self.lassoItem.setPolygon(self.lasso)
            
            self.setMouseEnabled(x=False, y=False)  # Disable default dragging behavior
            event.accept()
        elif event.button() == QtCore.Qt.RightButton:
            
            # Right mouse click
         
            self.lassoPoints = []
            self.lasso.clear()
            self.lassoItem.setPolygon(self.lasso)
            self.setMouseEnabled(x=True, y=True) # Re-enable default dragging behavior
            self.resetPointsColor()
            self.modify_viewer()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.lassoPoints:
            self.lassoPoints.append(self.vb.mapSceneToView(event.scenePos()))
            self.lasso = QtGui.QPolygonF(self.lassoPoints)
            self.lassoItem.setPolygon(self.lasso)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.lassoPoints and event.button() == QtCore.Qt.LeftButton:
            
            self.highlightPointsWithinLasso()
            self.setMouseEnabled(x=True, y=True) # Re-enable default dragging behavior

            self.modify_viewer()

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def highlightPointsWithinLasso(self):
        # Change color of points inside the lasso to red
        for i, point in enumerate(self.scatter.points()):
            if self.lasso.containsPoint(point.pos(), QtCore.Qt.OddEvenFill):
                point.setBrush(pg.mkBrush('r'))

    def resetPointsColor(self):
        # Reset points to their original color
        for i, point in enumerate(self.scatter.points()):
            point.setBrush(self.org_brush[i])

    def modify_viewer(self):

        color_dict = {}
        color_dict[0] = [0,0,0,0]
        for i, point in enumerate(self.scatter.points()):   
            color_dict[i+1] = point.brush().color().getRgb()

        viewer.layers['segmentation'].color = color_dict
        

if __name__ == '__main__':

    app = QApplication([])
    win = pg.GraphicsLayoutWidget(show=True)
    customPlot = CustomPlot(xx= [1,2,3],yy= [1,2,3], org_brush = [pg.mkBrush('r'),pg.mkBrush('g'),pg.mkBrush('b')])
    win.addItem(customPlot)
    
    app.exec_()
