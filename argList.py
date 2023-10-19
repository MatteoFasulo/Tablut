class argList(list):
    def __contains__(self, other):
        "Check if <other> is a substring of exactly one element of <self>"
        num = 0
        for item in self:
            if other.lower() in item:
                num += 1
            if num > 1:
                return False
        return num==1
    def find(self, other):
        "Return the first element of <self> in which <other> can be found"
        for item in self:
            if other.lower() in item:
                return item