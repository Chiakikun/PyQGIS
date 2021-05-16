# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .temporarylayer_sample import TemporaryLayerSample
    return TemporaryLayerSample(iface)
