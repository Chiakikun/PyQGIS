# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ScreenShotSampleDialog
 ベクタレイヤをフューチャー毎にスクリーンショットで保存するサンプルです
        copyright            : (C) 2019 by Chiakikun
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
from qgis.PyQt import QtCore
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

import os
import qgis.core

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'screenShot_sample_dialog_base.ui'))


class ScreenShotSampleDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, iface, action, parent=None):
        super(ScreenShotSampleDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = action

        self.savedir = 'c:/users/〇〇/desktop' # 画像の保存先
        self.scale = 250000                    # スクリーンショット撮るときのマップの縮尺


    def exportMap(self):
        self.canvas.saveAsImage( self.savedir + "/{}.png".format( self.ids.pop() ) )

        if self.ids:
            self.setNextFeatureExtent()
        else:
            self.canvas.mapCanvasRefreshed.disconnect( self.exportMap )


    def setNextFeatureExtent(self): # この関数が終わるとself.exportMapが呼ばれます(リフレッシュが終わるので)
        self.canvas.zoomToFeatureIds( self.layer, [self.ids[-1]] ) # -1 しているのは、exportMapでpopしているから
        self.canvas.zoomScale(self.scale) # 縮尺 


    def pushExec(self):
        self.layer = self.iface.activeLayer()
        if type(self.layer) is not qgis.core.QgsVectorLayer:
            return
        self.ids = self.layer.allFeatureIds()

        self.canvas.mapCanvasRefreshed.connect( self.exportMap )

        self.setNextFeatureExtent() # setNextFeatureExtent -> exportMap -> ...のループに突入

        self.close()