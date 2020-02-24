﻿# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ScreenShotSample2Dialog
                                 A QGIS plugin
 ベクタレイヤをフューチャー毎にスクリーンショットで保存するサンプルの改良版。
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-29
        git sha              : $Format:%H$
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

 注意! スタイル設定されているレイヤを選択して実行するとpushExecでエラーになります。

"""
from qgis.PyQt import QtCore
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtGui import QColor

import os
import qgis.core


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'screenShot_Sample2_dialog_base.ui'))


class ScreenShotSample2Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(ScreenShotSample2Dialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = qgis.utils.iface
        self.canvas = self.iface.mapCanvas()

        # 縮尺リスト
        self.scaleList.addItem('2500')
        self.scaleList.addItem('10000')
        self.scaleList.addItem('50000')
        self.scaleList.addItem('100000')
        self.scaleList.addItem('250000')


    def closeEvent(self, e):
        try:
            self.layer.setRenderer(self.prerenderer)
            self.layer.triggerRepaint()
        except: # pushExecを通らずに終了した時のため
            pass


    def pushSelectDir(self):
        path = QFileDialog.getExistingDirectory(None, "", "")
        self.saveDirPath.setText(path)


    def pushClose(self):
        self.close()


    def exportMap(self):
        self.canvas.saveAsImage(self.saveDirPath.text() + "\{}.png".format(self.ids.pop()) )

        if self.ids:
            self.setNextFeatureExtent()
        else:
            self.canvas.mapCanvasRefreshed.disconnect( self.exportMap )
            self.show()


    def setNextFeatureExtent(self):
        # スクリーンショット撮るフューチャー
        rule = self.root_rule.children()[0].clone()
        rule.setFilterExpression('$id = ' + str(self.ids[-1]))
        self.root_rule.insertChild(1,rule) # この時点でルールは「赤(対象idは前のid)、赤(対象idはids[-1])、そのまま」
        self.root_rule.removeChildAt(0)    # この時点でルールは「赤(対象idはids[-1])、そのまま」
        self.layer.setRenderer(self.renderer)
        self.layer.triggerRepaint()

        self.canvas.zoomToFeatureIds( self.layer, [self.ids[-1]] )
        self.canvas.zoomScale(int(self.scaleList.currentText()))


    def pushExec(self):

        if not (os.path.exists(self.saveDirPath.text()) and (os.path.isdir(self.saveDirPath.text()))):
            QtWidgets.QMessageBox.information(None, "エラー", "指定したフォルダが見つかりませんでした。:"+ self.saveDirPath.text() , QMessageBox.Ok)
            return

        self.layer = self.iface.activeLayer()
        if type(self.layer) is not qgis.core.QgsVectorLayer:
            QtWidgets.QMessageBox.information(None, "エラー", "ベクタレイヤが選択されていません。" , QMessageBox.Ok)
            return
        self.ids = self.layer.allFeatureIds()


        # スタイル設定 画像にするフューチャーを赤くしたいので... 「https://gis.stackovernet.com/ja/q/54438」を参考にしました
        self.prerenderer = self.layer.renderer().clone()
        symbol = qgis.core.QgsSymbol.defaultSymbol(self.layer.geometryType())
        self.renderer = qgis.core.QgsRuleBasedRenderer(symbol)
        style_rules = (
            ('Target', '$id = 0', '#ff0000'), # $idが0なら赤
            ('Other', 'ELSE', self.prerenderer.symbol().color().name()), # それ以外はそのまま      
        )
        self.root_rule = self.renderer.rootRule()
        for label, expression, color_name in style_rules:
            rule = self.root_rule.children()[0].clone() # ラベル、フィルタ、色以外はデフォルトを使いたいのでcloneしています
            rule.setLabel(label)
            rule.setFilterExpression(expression)
            rule.symbol().setColor(QColor(color_name))
            self.root_rule.appendChild(rule) # この時点でルールは「デフォルト、赤、そのまま」
        self.root_rule.removeChildAt(0)      # この時点でルールは「赤、そのまま」
        self.layer.setRenderer(self.renderer)
        self.layer.triggerRepaint()

        # スクリーンショット開始
        self.hide()
        self.canvas.mapCanvasRefreshed.connect( self.exportMap )
        self.setNextFeatureExtent() # setNextFeatureExtent -> exportMap -> ... のループ
