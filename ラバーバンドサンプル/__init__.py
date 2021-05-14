# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .rubberband_sample import RubberbandSample
    return RubberbandSample(iface)
