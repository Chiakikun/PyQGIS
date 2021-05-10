# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .intersectselect_sample import IntersectSelectSample
    return IntersectSelectSample(iface)
