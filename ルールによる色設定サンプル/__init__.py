# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .rulebase_sample import RulebaseSample
    return RulebaseSample(iface)
