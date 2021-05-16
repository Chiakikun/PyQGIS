# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .attributeeditor_sample import AttributeEditorSample
    return AttributeEditorSample(iface)
