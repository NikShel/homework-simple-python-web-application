class Link:
    def __init__(self, short, long, flag):
        self.short = short
        self.long = long
        self.flag = flag
        self.count = 0

    def __str__(self):
        return '{} --> {}'.format(self.short, self.long)


class User:
    def __init__(self, name, password, links):
        self.name = name
        self.password = password
        self.links = links

    def __str__(self):
        return '{}: {} {}'.format(self.name, self.password, self.links)