# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .layertreeview_sample import LayerTreeViewSample
    return LayerTreeViewSample(iface)
