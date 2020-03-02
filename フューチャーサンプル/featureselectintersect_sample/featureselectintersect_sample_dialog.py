# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FeatureSelectIntersectSampleDialog
                                 A QGIS plugin
 選択したフューチャーと交差するフューチャーを選択するサンプル
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-02-11
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
from qgis.PyQt import QtCore
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QAction, QMessageBox

import os
import qgis.core

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'featureselectintersect_sample_dialog_base.ui'))


class FeatureSelectIntersectSampleDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(FeatureSelectIntersectSampleDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = qgis.utils.iface
        self.canvas = self.iface.mapCanvas()


    def pushCancel(self):
        self.close()


    def showEvent(self, e):
        self.comboSelectLayer.clear()
        self.comboTargetLayer.clear()

        layers = qgis.core.QgsProject.instance().mapLayers().values()
        for layer in layers:
            if type(layer) is not qgis.core.QgsVectorLayer: continue
            self.comboSelectLayer.addItem(layer.name())
            self.comboTargetLayer.addItem(layer.name())


    def changeSelect(self, string):
        if self.comboSelectLayer.currentText() == '': return
        self.selectLayer = qgis.core.QgsProject.instance().mapLayersByName(self.comboSelectLayer.currentText())[0]


    def changeTarget(self, string):
        if self.comboTargetLayer.currentText() == '': return
        self.targetLayer = qgis.core.QgsProject.instance().mapLayersByName(self.comboTargetLayer.currentText())[0]
        
        # このレイヤのフューチャーに交差するself.selectLayerのフューチャーを取得したいので、
        # self.targetLayerをアクティブにする（マウス選択できるように）
        self.iface.setActiveLayer(self.targetLayer)


    def pushExec(self):
        if self.comboSelectLayer.currentText() == self.comboTargetLayer.currentText():
            QMessageBox.about(None, '警告', '同じベクタレイヤを選択しないでください')
            return

        features = self.targetLayer.selectedFeatures()
        if len(features) == 0:
            QMessageBox.about(None, '警告', 'フューチャーを一つ選択してください')
            return

        self.selectLayer.removeSelection()
        areas = []
        inGeom = features[0].geometry()
        # 矩形で大まかに取得してから、インターセクトで細かく取得する
        cands = self.selectLayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterRect(inGeom.boundingBox())) # 「https://qgis.org/api/classQgsFeatureRequest.html」のexample
        for sf in cands:
            if inGeom.intersects(sf.geometry()):
                areas.append(sf.id())
        self.selectLayer.select(areas)

        res = qgis.core.QgsVectorFileWriter.writeAsVectorFormat(self.selectLayer, 'd:\\' + self.selectLayer.name() + '.shp', 'System', self.selectLayer.crs(), 'ESRI Shapefile', True)