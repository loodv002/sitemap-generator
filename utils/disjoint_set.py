class DisjointSet:
    def __init__(self, n):
        self.group = [-1] * n
        self.nGroup = n # number of groups
    def find(self, i): # find root of group
        path = []
        while self.group[i] >= 0:
            path.append(i)
            i = self.group[i]
        for p in path: self.group[p] = i
        return i
    def same(self, a, b): # two elements in same group
        return self.find(a) == self.find(b)
    def size(self, a): # size of group of a element
        return -self.group[self.find(a)]
    def union(self, a, b):
        if self.same(a, b): return
        if self.size(a) < self.size(b): a, b = b, a
        self.nGroup -= 1
        pa = self.find(a)
        pb = self.find(b)
        self.group[pa] += self.group[pb]
        self.group[pb] = pa
    def __len__(self): return self.nGroup