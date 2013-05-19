from StringIO import StringIO

from vobj import VObj, VIOError

class VFile(VObj, StringIO):
  def __init__(self, name, parent=None, mode="rw"):
    VObj.__init__(self, name, parent)
    StringIO.__init__(self)

    self.set_mode(mode)

  def is_file(self):
    return True

  def is_directory(self):
    return False

  def set_mode(self, mode):
    self.mode = set(mode)

    if set("rw") & self.mode:
      self.seek(0)
    elif "a" in self.mode:
      self.seek(self.len)

  def write(self, *args, **kwargs):
    if not set("wa") & self.mode:
      raise VIOError("File not open for writing")
    return super(VFile, self).write(*args, **kwargs)

  def read(self, *args, **kwargs):
    if not "r" in self.mode:
      raise VIOError("File not open for reading")
    return super(VFile, self).read(*args, **kwargs)