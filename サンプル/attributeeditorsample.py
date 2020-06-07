# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttributeEditorSample
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

①プラグインのフォルダにこのファイルを置く

②インポート部分に以下を追加する
from .attributeeditorsample import AttributeEditorSample

③__init__のcheckableをFalseにする
self.checkable = False

④startを以下で置き換える
    def start(self):
        self.ae = AttributeEditorSample(self.iface)
        self.ae.editAttribute(self.iface.activeLayer())

⑤ベクタレイヤの地物を一つ選択した状態でプラグインを実行する
"""
import qgis
from qgis.gui  import *

class AttributeEditorSample:

    def editAttribute(self, layer):
        features = layer.selectedFeatures()
        if len(features) == 0:
            return

        self.layer = layer

        self.layer.startEditing() # レイヤを編集状態にする

        # 選択しているフューチャーの属性フォーム表示
        self.attdlg = self.iface.getFeatureForm(self.layer, features[0])
        self.attdlg.setMode(QgsAttributeEditorContext.SingleEditMode)
        self.attdlg.finished.connect(self.commitEdit)
        self.attdlg.show()


    def commitEdit(self, result):
        if result == 1:
            self.layer.commitChanges()
        else:
            self.layer.rollBack()
        self.attdlg.finished.disconnect(self.commitEdit)


    def __init__(self, iface):
        self.iface = iface