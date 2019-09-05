

class ApiPlatform(object):

    def __init__(self, platform):
        self.platform = platform

    def api(self):
        if self.platform == 'EXX':
            from .exx.exxService import ExxService
            from .exx.exxMarket import MarketCondition

