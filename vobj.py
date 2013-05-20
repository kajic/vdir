class VIOError(IOError): pass

class VObj(object):
  def __init__(self, name, parent):
    self.name = name
    if not parent:
      parent = self
    self.parent = parent

  def __eq__(self, other):
    return not self<other and not other<self

  def __ne__(self, other):
    return self<other or other<self

  def __gt__(self, other):
    return other<self

  def __ge__(self, other):
    return not self<other

  def __le__(self, other):
    return not other<self

  def __lt__(self, other):
    return id(self)<id(other)

  def is_root(self):
    return self == self.parent

  def root(self):
    cur = self.cur
    while not cur.is_root():
      cur = cur.parent
    return cur

  def pwd(self):
    cur = self.cur
    path = [cur.name]

    while not cur.is_root():
      cur = cur.parent
      path.append(cur.name)

    path.reverse()
    return "/".join(path)

  def unattach(self):
    if not self.is_root():
      del self.parent[self.name]
      self.parent = self
