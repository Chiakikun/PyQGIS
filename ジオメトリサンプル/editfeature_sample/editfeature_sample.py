﻿# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EditFeatureSample
                                 A QGIS plugin
 フューチャーを編集するサンプルです
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-26
        git sha              : $Format:%H$
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
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QIcon, QTransform
from qgis.PyQt.QtWidgets import QAction, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis.core;
from PyQt5.Qt import pyqtSignal
from qgis.PyQt.QtGui import QColor
import math

class EditFeatureSample:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # プラグインの登録場所
        self.menu_pos = 'サンプル ジオメトリ'


    def initGui(self):
        icon = QIcon(self.plugin_dir+'/icon.png')
        self.action = QAction(icon, '編集サンプル', self.iface.mainWindow())
        self.action.triggered.connect(self.execSample) # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(True)                 # Trueだとアイコンを押下したら次に押下するまで凹んだままになる。
        #self.iface.addToolBarIcon(self.action)         # ツールバーにアイコンを表示させたいなら#外して
        self.iface.addPluginToMenu(self.menu_pos, self.action)


    # このサンプル以外のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, EditFeatureSample):
            try:
                self.mouseEventSample.featureIdentified.disconnect(self.selectedFeature)
            except Exception:
                pass

            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)

            self.action.setChecked(False)


    def execSample(self):
        if self.action.isChecked():
            self.layer = self.iface.activeLayer()

            if (self.layer == None) or (type(self.layer) is not qgis._core.QgsVectorLayer):
                QMessageBox.about(None, '警告', 'ベクタレイヤを選択してから実行してください')
                self.action.setChecked(False)
                return

            self.mouseEventSample = FeatureSelectionTool(self.iface, self.canvas)

            self.previousMapTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.mouseEventSample)
            self.canvas.mapToolSet.connect(self.unsetTool)

            self.mouseEventSample.setLayer(self.iface.activeLayer())
            self.mouseEventSample.featureIdentified.connect(self.selectedFeature)
        else:
            self.mouseEventSample.featureIdentified.disconnect(self.selectedFeature)
            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)
            self.canvas.setMapTool(self.previousMapTool)


    # フューチャーを一つ選択した時に呼ばれる。
    def selectedFeature(self, feature):        
        self.mouseEventSample.setFeature(feature)


class FeatureSelectionTool(qgis.gui.QgsMapToolIdentifyFeature):
    setFeature = pyqtSignal(qgis.core.QgsGeometry)

    def __init__(self, iface, canvas):
        self.iface = iface
        self.canvas = canvas
        self.layer = self.iface.activeLayer()
        self.objType = self.layer.geometryType()

        qgis.gui.QgsMapToolIdentifyFeature.__init__(self, self.canvas)
        self.myRubberBand = None


    def canvasPressEvent(self, event): # featureIdentifiedより先に呼ばれる
        self.srcpos = event.pos()

        if self.myRubberBand == None: return

        if event.button() == QtCore.Qt.LeftButton:

            self.layer.startEditing()
            self.changeGeometry(self.layer.selectedFeatures()[0])
            self.layer.commitChanges()

        self.myRubberBand.reset()
        self.myRubberBand = None
        self.layer.removeSelection() 


    def setFeature(self, feat):
        if self.myRubberBand != None: return

        self.layer.select(feat.id())

        curpos = qgis.core.QgsGeometry().fromPointXY(self.toMapCoordinates(self.srcpos))
        mpol = self.multiTolist(feat.geometry())

        # 選択したマルチオブジェクトで、選択位置に一番近いオブジェクト取得
        dist = [pol.distance(curpos) for pol in mpol]
        self.nearidx = dist.index(min(dist))
        self.nearobj = mpol[self.nearidx]

        # ラバーバンドにnearobjを追加する
        self.myRubberBand = qgis.gui.QgsRubberBand( self.canvas, self.objType )
        self.myRubberBand.setColor(QColor(255, 0, 0, 255))
        self.myRubberBand.addGeometry(self.nearobj, self.layer)


    def canvasMoveEvent(self, e):
        if self.myRubberBand == None: return

        self.myRubberBand.reset(self.objType)

        dstpos = e.pos()
        #self.moveObject(self.srcpos, dstpos)
        self.scaleObject(self.srcpos, dstpos)
        #self.rotateObject(self.srcpos, dstpos)

    def multiTolist(self, multiobj):

        if self.objType == qgis.core.QgsWkbTypes.GeometryType.PolygonGeometry:
            return [qgis.core.QgsGeometry().fromPolygonXY(pol) for pol in multiobj.asMultiPolygon()]

        elif self.objType == qgis.core.QgsWkbTypes.GeometryType.LineGeometry:
            return [qgis.core.QgsGeometry().fromPolylineXY(pline) for pline in multiobj.asMultiPolyline()]

        elif self.objType == qgis.core.QgsWkbTypes.GeometryType.PointGeometry:
            if multiobj.isMultipart():
                return [qgis.core.QgsGeometry().fromPointXY(pnt) for pnt in multiobj.asMultiPoint()]
            else:
                return [qgis.core.QgsGeometry().fromPointXY(multiobj.asPoint())]


    def changeGeometry(self, feat):

        if self.objType == qgis.core.QgsWkbTypes.GeometryType.PolygonGeometry:
            mpol = feat.geometry().asMultiPolygon()
            mpol[self.nearidx] = self.myRubberBand.asGeometry().asPolygon()
            self.layer.changeGeometry (feat.id(), qgis.core.QgsGeometry().fromMultiPolygonXY(mpol))

        elif self.objType == qgis.core.QgsWkbTypes.GeometryType.LineGeometry:
            mline = feat.geometry().asMultiPolyline()
            mline[self.nearidx] = self.myRubberBand.asGeometry().asPolyline()
            self.layer.changeGeometry (feat.id(), qgis.core.QgsGeometry().fromMultiPolylineXY(mline))

        elif self.objType == qgis.core.QgsWkbTypes.GeometryType.PointGeometry:
            if feat.geometry().isMultipart():
                mpnt = feat.geometry().asMultiPoint()
                mpnt[self.nearidx] = self.myRubberBand.asGeometry().asMultiPoint()[0]
                self.layer.changeGeometry (feat.id(), qgis.core.QgsGeometry().fromMultiPointXY(mpnt))
            else:
                pnt = self.myRubberBand.asGeometry().asMultiPoint()[0]
                self.layer.changeGeometry (feat.id(), qgis.core.QgsGeometry.fromPointXY(pnt))


    def moveObject(self, srcpos, dstpos):
        temp = qgis.core.QgsGeometry(self.nearobj)

        s = self.toMapCoordinates(srcpos)
        d = self.toMapCoordinates(dstpos)

        self.myRubberBand.addGeometry(self.trans(temp, s, d), self.layer)


    def scaleObject(self, srcpos, dstpos):
        original = qgis.core.QgsPointXY(0, 0)
        centroid = self.nearobj.centroid().asPoint()
        temp = qgis.core.QgsGeometry(self.nearobj)

        s = qgis.core.QgsGeometry().fromPointXY(qgis.core.QgsPointXY(srcpos))
        d = qgis.core.QgsGeometry().fromPointXY(qgis.core.QgsPointXY(dstpos))

        # 一度中心に持ってこないとオブジェクトが変な方向に行ってしまうので
        temp = self.trans(temp, centroid, original)
        temp = self.scale(temp, s, d)
        temp = self.trans(temp, original, centroid)

        self.myRubberBand.addGeometry(temp, self.layer)


    def rotateObject(self, srcpos, dstpos):
        original = qgis.core.QgsPointXY(0, 0)
        centroid = self.nearobj.centroid().asPoint()
        temp = qgis.core.QgsGeometry(self.nearobj)

        s = qgis.core.QgsPointXY(self.toMapCoordinates(srcpos))
        d = qgis.core.QgsPointXY(self.toMapCoordinates(dstpos))

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
        cent = qgis.core.QgsGeometry().fromPointXY(qgis.core.QgsPointXY(0, 0))
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
