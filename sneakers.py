
class sneaker:
    snkr_name = str()
    release_date = str()
    snkr_prize = str()
    _color = str()
    color_ID = str()

    def __str__(self):
        return "\nSneaker Name:{}\nRelease Date:{}\nPrize:{}\nColor:{}\nID:{}\n".format(self.snkr_name,
                                                                                       self.release_date,
                                                                                       self.snkr_prize,
                                                                                       self._color,
                                                                                       self.color_ID)

    def name(self, val):
        self.snkr_name = val

    def release(self, val):
        self.release_date = val

    def prize(self, val):
        self.snkr_prize = val

    def id(self, val):
        self.color_ID = val

    def color(self, val):
        self._color = val
