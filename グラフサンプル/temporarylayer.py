# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TemporaryLayer
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
import qgis
from qgis.core import *
from qgis.gui  import *

class TemporaryLayer:
    def __init__(self, iface, canvas, layername, type, fields): # type = Point or LineString, Polygon

        self.canvas = canvas
        self.iface = iface

        fieldsstr = ''
        for f in fields:
            fieldsstr += '&field=' + f

        epsg = iface.mapCanvas().mapSettings().destinationCrs().authid()
        self.layer = QgsVectorLayer(type + '?&crs='+epsg+fieldsstr, layername, 'memory')

        QgsProject.instance().addMapLayer(self.layer)


    def getFeatures(self, arg=None):
        if arg == None:
            return self.layer.getFeatures()
        else:
            return self.layer.getFeatures(arg)


    def selectByExpression(self, query):
        return self.layer.selectByExpression(query)


    def addFeature(self, geometry, attrs):

            qf = QgsFields()
            for field in self.layer.fields():
                qf.append(QgsField(str(field.name()), typeName=field.typeName()))
            record = QgsFeature(qf) 

            # 地物をセットする
            record.setGeometry(geometry) 

            # 属性をセットする
            record.setAttributes(attrs)

            # 作成したレコードをレイヤに追加
            self.layer.dataProvider().addFeatures([record])
            self.layer.updateExtents() # これが無いと『レイヤの領域にズーム』した時に、レイヤの最初のオブジェクト部分しかズームされない

            self.canvas.refreshAllLayers()


    def __del__(self):
        self.canvas.refreshAllLayers()
        QgsProject.instance().removeMapLayer(self.layer.id())
