# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MultiObjectEditSample
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

from PyQt5.Qt import pyqtSignal
from qgis.PyQt.QtGui import QColor, QTransform
import math

class MultiObjectEditSample(QgsMapTool):

    def selectedFeature(self, feature):        
        self.maptool.setFeature(feature)


    def start(self):
        self.maptool = MultiObjectEditClass(self.iface, self.canvas, 'move') # 移動の場合
        self.maptool.setLayer(self.iface.activeLayer())
        self.maptool.featureIdentified.connect(self.selectedFeature)

        self.canvas.setMapTool(self.maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'マルチオブジェクト編集サンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛形/ダイアログ無し雛形」)
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, MultiObjectEditSample):
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


class MultiObjectEditClass(QgsMapToolIdentifyFeature):
    setFeature = pyqtSignal(QgsGeometry)

    def __init__(self, iface, canvas, edittype): # edittype = 'scale', 'move', 'rotate'
        self.iface = iface
        self.canvas = canvas
        self.layer = self.iface.activeLayer()
        self.objType = self.layer.geometryType()
        self.edittype = edittype

        QgsMapToolIdentifyFeature.__init__(self, self.canvas)
        self.myRubberBand = None


    def canvasPressEvent(self, event): # featureIdentifiedより先に呼ばれる
        self.srcpos = event.pos()

        if self.myRubberBand == None: return

        if event.button() == QtCore.Qt.LeftButton:
            # self.layer.startEditing() # バックアップは取りましたか？バックアップできたなら、#を外してください
            self.changeGeometry(self.layer.selectedFeatures()[0])
            # self.layer.commitChanges() # ここも

        self.myRubberBand.reset()
        self.myRubberBand = None
        self.layer.removeSelection() 


    def setFeature(self, feat):
        if self.myRubberBand != None: return

        self.layer.select(feat.id())

        curpos = QgsGeometry().fromPointXY(self.toMapCoordinates(self.srcpos))

        mpol = self.tolist(feat.geometry())

        # 選択したマルチオブジェクトで、選択位置に一番近いオブジェクト取得
        dist = [pol.distance(curpos) for pol in mpol]
        self.nearidx = dist.index(min(dist))
        self.nearobj = mpol[self.nearidx]

        # ラバーバンドにnearobjを追加する
        self.myRubberBand = QgsRubberBand( self.canvas, self.objType )
        self.myRubberBand.setColor(QColor(255, 0, 0, 255))
        self.myRubberBand.addGeometry(self.nearobj, self.layer)


    def canvasMoveEvent(self, e):
        if self.myRubberBand == None: return

        self.myRubberBand.reset(self.objType)

        dstpos = e.pos()

        if self.edittype == 'move':
            self.moveObject(self.srcpos, dstpos)
        elif self.edittype == 'scale':
            self.scaleObject(self.srcpos, dstpos)
        else:
            self.rotateObject(self.srcpos, dstpos)


    def changeGeometry(self, feat):

        if self.objType == QgsWkbTypes.GeometryType.PolygonGeometry:
            if feat.geometry().isMultipart():
                mpol = feat.geometry().asMultiPolygon()
                mpol[self.nearidx] = self.myRubberBand.asGeometry().asPolygon()
                self.layer.changeGeometry (feat.id(), QgsGeometry().fromMultiPolygonXY(mpol))
            else:
                pol = self.myRubberBand.asGeometry().asPolygon()
                self.layer.changeGeometry (feat.id(), QgsGeometry.fromPolygonXY(pol))

        elif self.objType == QgsWkbTypes.GeometryType.LineGeometry:
            if feat.geometry().isMultipart():
                mline = feat.geometry().asMultiPolyline()
                mline[self.nearidx] = self.myRubberBand.asGeometry().asPolyline()
                self.layer.changeGeometry (feat.id(), QgsGeometry().fromMultiPolylineXY(mline))
            else:
                line = self.myRubberBand.asGeometry().asPolyline()
                self.layer.changeGeometry (feat.id(), QgsGeometry.fromPolylineXY(line))

        elif self.objType == QgsWkbTypes.GeometryType.PointGeometry:
            if feat.geometry().isMultipart():
                mpnt = feat.geometry().asMultiPoint()
                mpnt[self.nearidx] = self.myRubberBand.asGeometry().asMultiPoint()[0]
                self.layer.changeGeometry (feat.id(), QgsGeometry().fromMultiPointXY(mpnt))
            else:
                pnt = self.myRubberBand.asGeometry().asMultiPoint()[0]
                self.layer.changeGeometry (feat.id(), QgsGeometry.fromPointXY(pnt))


    def tolist(self, obj):

        if self.objType == QgsWkbTypes.GeometryType.PolygonGeometry:
            if obj.isMultipart():
                return [QgsGeometry().fromPolygonXY(pol) for pol in obj.asMultiPolygon()]
            else:
                return [QgsGeometry().fromPolygonXY(obj.asPolygon())]

        elif self.objType == QgsWkbTypes.GeometryType.LineGeometry:
            if obj.isMultipart():
                return [QgsGeometry().fromPolylineXY(pline) for pline in obj.asMultiPolyline()]
            else:
                return [QgsGeometry().fromPolylineXY(obj.asPolyline())]

        elif self.objType == QgsWkbTypes.GeometryType.PointGeometry:
            if obj.isMultipart():
                return [QgsGeometry().fromPointXY(pnt) for pnt in obj.asMultiPoint()]
            else:
                return [QgsGeometry().fromPointXY(obj.asPoint())]


    def moveObject(self, srcpos, dstpos):
        temp = QgsGeometry(self.nearobj)

        s = self.toMapCoordinates(srcpos)
        d = self.toMapCoordinates(dstpos)

        self.myRubberBand.addGeometry(self.trans(temp, s, d), self.layer)


    def scaleObject(self, srcpos, dstpos):
        original = QgsPointXY(0, 0)
        centroid = self.nearobj.centroid().asPoint()
        temp = QgsGeometry(self.nearobj)

        s = QgsGeometry().fromPointXY(QgsPointXY(srcpos))
        d = QgsGeometry().fromPointXY(QgsPointXY(dstpos))

        # 一度中心に持ってこないとオブジェクトが変な方向に行ってしまうので
        temp = self.trans(temp, centroid, original)
        temp = self.scale(temp, s, d)
        temp = self.trans(temp, original, centroid)

        self.myRubberBand.addGeometry(temp, self.layer)


    def rotateObject(self, srcpos, dstpos):
        original = QgsPointXY(0, 0)
        centroid = self.nearobj.centroid().asPoint()
        temp = QgsGeometry(self.nearobj)

        s = QgsPointXY(self.toMapCoordinates(srcpos))
        d = QgsPointXY(self.toMapCoordinates(dstpos))

        # 一度中心に持ってこないとオブジェクトが変な方向に行ってしまうので
        temp = self.trans(temp, centroid, original)
        temp = self.rotate(temp, s, d)
        temp = self.trans(temp, original, centroid)

        self.myRubberBand.addGeometry(temp, self.layer)


    def trans(self, obj, srcpos, dstpos):
        x = dstpos.x() - srcpos.x()
        y = dstpos.y() - srcpos.y()

        obj.transform(QTransform(1, 0, 0, 1, x, y))
        return obj


    def scale(self, obj, srcpos, dstpos):
        cent = QgsGeometry().fromPointXY(QgsPointXY(0, 0))
        srclen = cent.distance(srcpos)
        dstlen = cent.distance(dstpos)
        ratio = (dstlen / srclen) * 1.5 # 「1.5」は適当

        obj.transform(QTransform(ratio, 0, 0, ratio, 0, 0))
        return obj


    def rotate(self, obj, srcpos, dstpos):
        centroid = self.nearobj.centroid().asPoint()
        theta = self.radian(centroid, dstpos)
        sin = math.sin(theta)
        cos = math.cos(theta)

        obj.transform(QTransform(cos, sin, -sin, cos, 0, 0))
        return obj


    def radian(self, a, b):
        return math.atan2(b.y() - a.y(), b.x() - a.x())


    def deactivate(self):
        try: # 左クリックで既にNoneしていた場合エラーになるので
            self.myRubberBand.reset()
        except:
            pass
        self.myRubberBand = None
        self.layer.removeSelection() 
