# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetRasterPixelValueSample
        copyright            : (C) 2020 by Chiakikun
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

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *

import pyproj


class GetRasterPixelValueSample(QgsMapTool):

    def canvasMoveEvent(self, event):
        print(str(self.gr.getValueInterpolation(self.toMapCoordinates(event.pos()))))


    def start(self):
        self.gr = GetRasterPixelValueClass(self.iface.activeLayer())

        maptool = self

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'ピクセル値取得サンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛形/ダイアログ無し雛形」)
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, GetRasterPixelValueSample):
            self.finish()
            self.action.setChecked(False)


    def initGui(self):
        icon = QIcon(os.path.dirname(__file__)+'/icon.png')
        self.action = QAction(icon, self.plugin_name, self.iface.mainWindow())
        self.action.triggered.connect(self.execSample) # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(self.checkable)       # Trueだとアイコンを押下したら次に押下するまで凹んだままになる
        if self.toolbar:
            self.iface.addToolBarIcon(self.action)     # ツールバーにこのツールのアイコンを表示する
        self.iface.addPluginToMenu(self.menu_pos, self.action)
        

    # このプラグインを無効にしたときに呼ばれる
    def unload(self):
        self.iface.removePluginMenu(self.menu_pos, self.action)
        self.iface.removeToolBarIcon(self.action)


    # このツールのアイコンを押下したときに呼ばれる
    def execSample(self):
        if self.checkable:
            if self.action.isChecked(): # 凹状態になった
                self.previousMapTool = self.canvas.mapTool()  # 現在のマップツールを退避
                self.start()
            else:                       # 凸状態になった
                self.finish()
                self.canvas.setMapTool(self.previousMapTool)  # このツール実行前に戻す
        else:
            self.start()


class GetRasterPixelValueClass:

    def __init__(self, layer: QgsRasterLayer):
        self.__grs80 = pyproj.Geod(ellps='GRS80')

        # ピクセル1つのサイズ
        self.__unitX = layer.rasterUnitsPerPixelX()
        self.__unitY = layer.rasterUnitsPerPixelY()

        # ラスタのサイズ
        self.__height = layer.height()
        self.__width = layer.width()

        # ラスタの原点
        self.__provider = layer.dataProvider()
        self.__extent = self.__provider.extent()
        self.__orgX = self.__extent.xMinimum()
        self.__orgY = self.__extent.yMaximum()

        # ピクセル
        self.block = self.__provider.block(1, self.__extent, self.__width, self.__height)


    def getIndex(self, pos: QgsPointXY):

        pixelIdxX = (pos.x() - self.__orgX) / self.__unitX
        pixelIdxY = (self.__orgY - pos.y()) / self.__unitY
        if (pixelIdxX < 0) or (pixelIdxY < 0):
            return None
        pixelIdxX = int(pixelIdxX)
        pixelIdxY = int(pixelIdxY)
        if (pixelIdxX > self.__width - 1) or (pixelIdxY > self.__height - 1):
            return None

        return [pixelIdxX, pixelIdxY]


    def getGeometry(self, idxX: int, idxY: int):
        if (idxX < 0) or (idxY < 0):
            return None
        if (idxX > self.__width - 1) or (idxY > self.__height - 1):
            return None

        pixelPosX = self.__unitX * idxX + self.__orgX + self.__unitX / 2
        pixelPosY = self.__orgY - self.__unitY * idxY - self.__unitY / 2
        return [pixelPosX, pixelPosY]


    def getValueFromPos(self, pos: QgsPointXY):
        ident = self.__provider.identify(pos, QgsRaster.IdentifyFormatValue )

        if ident.isValid():
            return list(ident.results().values())[0]
        else:
            return None


    def getValueFromIdx(self, idxX: int, idxY: int):
        if (idxX < 0) or (idxY < 0):
            return None
        if (idxX > self.__width - 1) or (idxY > self.__height - 1):
            return None

        return self.block.value(idxY, idxX)


    def getValueInterpolation(self, pos: QgsPointXY):

        pixidx = self.getIndex(pos)
        if pixidx == None:
            return None
        pixelIdxX = pixidx[0]
        pixelIdxY = pixidx[1]

        pixpos = self.getGeometry(pixelIdxX, pixelIdxY)
        pixelPosX = pixpos[0]
        pixelPosY = pixpos[1]

        # 右上
        if (pixelPosX < pos.x()) and (pixelPosY < pos.y()):
            if (pixelIdxX > self.__width - 2) or (pixelIdxY - 1 < 0):
                return None
            a = self.__getXYZ__(pixelIdxX+1, pixelIdxY-1)
            b = self.__getXYZ__(pixelIdxX,   pixelIdxY-1)
            c = self.__getXYZ__(pixelIdxX,   pixelIdxY)
            d = self.__getXYZ__(pixelIdxX+1, pixelIdxY)
        # 左上
        elif (pixelPosX >= pos.x()) and (pixelPosY < pos.y()):
            if (pixelIdxX - 1 < 0) or (pixelIdxY - 1 < 0):
                return None
            a = self.__getXYZ__(pixelIdxX,   pixelIdxY-1)
            b = self.__getXYZ__(pixelIdxX-1, pixelIdxY-1)
            c = self.__getXYZ__(pixelIdxX-1, pixelIdxY)
            d = self.__getXYZ__(pixelIdxX,   pixelIdxY)
        # 左下
        elif (pixelPosX >= pos.x()) and (pixelPosY >= pos.y()):
            if (pixelIdxX - 1 < 0) or (pixelIdxY > self.__height - 2):
                return None
            a = self.__getXYZ__(pixelIdxX,   pixelIdxY)
            b = self.__getXYZ__(pixelIdxX-1, pixelIdxY)
            c = self.__getXYZ__(pixelIdxX-1, pixelIdxY+1)
            d = self.__getXYZ__(pixelIdxX,   pixelIdxY+1)
        # 右下
        elif (pixelPosX < pos.x()) and (pixelPosY >= pos.y()):
            if (pixelIdxX > self.__width - 2) or (pixelIdxY > self.__height - 2):
                return None
            a = self.__getXYZ__(pixelIdxX+1, pixelIdxY)
            b = self.__getXYZ__(pixelIdxX,   pixelIdxY)
            c = self.__getXYZ__(pixelIdxX,   pixelIdxY+1)
            d = self.__getXYZ__(pixelIdxX+1, pixelIdxY+1)

        dist1 = self.__grs80.inv(b.x(), b.y(), a.x(), a.y())[2]
        dist2 = self.__grs80.inv(b.x(), b.y(), pos.x(), b.y())[2]
        delta = (a.z() - b.z()) / dist1
        tmp1 = delta * dist2 + b.z()

        dist1 = self.__grs80.inv(c.x(), c.y(), d.x(), d.y())[2]
        dist2 = self.__grs80.inv(c.x(), c.y(), pos.x(), c.y())[2]
        delta = (d.z() - c.z()) / dist1
        tmp2 = delta * dist2 + c.z()

        dist1 = self.__grs80.inv(d.x(), d.y(), a.x(), a.y())[2]
        dist2 = self.__grs80.inv(d.x(), d.y(), d.x(), pos.y())[2]
        delta = (tmp1 - tmp2) / dist1
        inp = delta * dist2 + tmp2

        return inp


    def __getXYZ__(self, idxX: int, idxY: int):
        x   = self.__unitX * idxX + self.__orgX + self.__unitX / 2
        y   = self.__orgY - self.__unitY * idxY - self.__unitY / 2

        z = self.block.value(idxY, idxX)

        return QgsPoint(x, y, z)