# 「https://gis.stackexchange.com/questions/247425/is-it-possible-get-pixel-value-with-only-pyqgis-and-not-gdal」を参考にさせていただきました
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetRasterPixelValue
        copyright            : (C) 2021 by Chiakikun
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
import qgis
from qgis.core import *
from qgis.gui  import *
import pyproj

class GetRasterPixelValue:

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