# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttributeEditorSample
        begin                : 2020-05-17
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
使い方例（『https://github.com/Chiakikun/PyQGIS/blob/master/ダイアログ無し雛形/nodialog_skelton.py』に組み込む場合）

プラグインのフォルダにこのファイルを置く

インポート
from .attributeeditorsample import AttributeEditorSample

__init__のcheckableをFalseにする
self.checkable = False

execSampleの以下の部分を書き換える
        else:
            pass
から
        else:
            self.ae = AttributeEditorSample(self.iface, self.canvas)
            self.ae.editAttribute(self.iface.activeLayer())
に書き換え

ベクタレイヤの地物を一つ選択した状態でプラグインを実行すると、編集ダイアログが表示されます。
"""
import qgis.core
from PyQt5.QtCore import QObject

class AttributeEditorSample(QObject):

    def editAttribute(self, layer):
        features = layer.selectedFeatures()
        if len(features) == 0:
            return

        self.layer = layer

        self.layer.startEditing() # レイヤを編集状態にする

        # 選択しているフューチャーの属性フォーム表示
        self.attdlg = self.iface.getFeatureForm(self.layer, features[0])
        self.attdlg.setMode(qgis.gui.QgsAttributeEditorContext.SingleEditMode)
        self.attdlg.finished.connect(self.commitEdit)
        self.attdlg.show()


    def commitEdit(self, result):
        if result == 1:
            self.layer.commitChanges()
        else:
            self.layer.rollBack()
        self.attdlg.finished.disconnect(self.commitEdit)


    def __init__(self, iface, canvas):

        self.canvas = canvas
        self.iface = iface
        QObject.__init__(self, self.canvas)

    def __del__(self):
        pass