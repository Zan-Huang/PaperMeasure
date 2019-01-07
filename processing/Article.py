class Article:

    def __init__(self, page):
        self.articlePieces = []
        self.completed = False
        self.continuePage = 0
        self.originalPage = page
        self.title = ""

