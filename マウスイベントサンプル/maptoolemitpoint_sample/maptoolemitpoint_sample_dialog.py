# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapToolEmitPointSampleDialog
                                 A QGIS plugin
 MapToolEmitPointを使ったサンプルです。
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2019 by unemployed
        email                : chiakikungm@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

import qgis.core
from qgis.PyQt import QtCore

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'maptoolemitpoint_sample_dialog_base.ui'))


class MapToolEmitPointSampleDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MapToolEmitPointSampleDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.mouseEventSample = qgis.gui.QgsMapToolEmitPoint(qgis.utils.iface.mapCanvas())
        
    def showEvent(self, e):
        self.isrun = False

    def pushExec(self):
        self.mouseEventSample.canvasClicked.connect(self.mouseClick)
        self.mouseEventSample.canvasMoveEvent = self.canvasMoveEvent        
        qgis.utils.iface.mapCanvas().setMapTool(self.mouseEventSample)
        self.isrun = True

    def pushClose(self):
        if self.isrun:
            self.mouseEventSample.canvasClicked.disconnect(self.mouseClick)
            qgis.utils.iface.mapCanvas().unsetMapTool(self.mouseEventSample)

        self.close()

    def canvasMoveEvent(self, event):
        print('マウス移動:' + str(qgis.utils.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(event.pos())))
 
    def mouseClick(self, currentPos, clickedButton ):
        if clickedButton == QtCore.Qt.LeftButton: 
            print('左クリック!' + str(qgis.core.QgsPointXY(currentPos)))

        if clickedButton == QtCore.Qt.RightButton:
            print('右クリック!' + str(qgis.core.QgsPointXY(currentPos)))
