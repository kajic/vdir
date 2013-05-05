import os 
import zipfile

from copy import copy
from StringIO import StringIO

class VDirError(Exception): pass

class ComparableMixin(object):
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

class VBase(ComparableMixin, object):
  def __init__(self, name, parent):
    self.name = name
    if not parent:
      parent = self
    self.parent = parent    

  def pwd(self):
    cur = self
    path = [self.name]
    while cur != cur.parent:
      path.append(cur.name)
      cur = cur.parent

    path.reverse()
    return "/".join(path)

class VFile(StringIO, VBase):
  def __init__(self, name, parent=None):
    VBase.__init__(name, parent)

  def read(self):
    self.seek(0)
    return super(VFile, self).read()

class VDir(dict, VBase):
  def __init__(self, name, parent=None):
    VBase.__init__(name, parent)

    self.cur = self

    self["."] = self
    self[".."] = self.parent

  def drill(self, path, create_intermediate=True, treat_basename_as_directory=False):
    dirname = os.path.dirname(path)

    cur = self.cur

    drill_path = dirname.split("/")

    if treat_basename_as_directory:
      basename = os.path.basename(path)
      if basename:
        drill_path.append(basename)

    for fragment in drill_path:
      if not fragment:
        continue

      if not cur.has_key(fragment):
        if not hasattr(cur, "has_key"):
          raise DirError("%s is not a directory" % cur.pwd())

        if create_intermediate:
          cur[fragment] = VDir(name=fragment, parent=cur)
        else:
          raise DirError("%s is not a directory" % os.path.join(cur.pwd(), fragment))

      cur = cur[fragment]
      
    return cur

  def open(self, path):
    dir = self.drill(path, create_intermediate=True)

    basename = os.path.basename(path)
    if basename:
      if hasattr(dir, "has_key"):
        if not dir.has_key(basename):
          dir[basename] = VFile(basename, dir)

        return dir[basename]
      else:
        raise DirError("%s is not a directory" % os.path.dirname(path))
    else:
      return dir

  def cd(self, path):
    self.cur = self.drill(path, create_intermediate=False, treat_basename_as_directory=True)
    return self.cur

  def pwd(self):
    pass

  def mkdir(self, path, create_intermediate=False):
    cur = self.drill(path, create_intermediate=create_intermediate, treat_basename_as_directory=True)
    return cur

  def cp(self, path, new_path=None):
    original = self.open(path)
    duplicate = self.copy(original)

    if new_path:
      name = os.path.basename(new_path)
      if not name:
        name = original.name

      destination = self.open(new_path)
      if hasattr(destination, "has_key"):
        destination[name] = duplicate
      else:
        destination.parent[name] = duplicate

    return duplicate

  def walk(self):
    candiates = [(self.cur, [])]

    for dir, path in candiates:
      dirnames = []
      filenames = []

      for fragment in dir:
        if fragment in [".", ".."]:
          continue

        if hasattr(dir[fragment], "walk"):
          dirnames.append(fragment)
        else:
          filenames.append(fragment)

      yield ("/".join(path), dirnames, filenames)

      # Add child directories to walk candiates
      candiates.extend([(dir[fragment], path+[fragment]) for fragment in dirnames])

  def zipfile(self, mode="w", compression=zipfile.ZIP_DEFLATED, exclude_compress=[]):
    zip_data = VFile()
    zip = zipfile.ZipFile(zip_data, "w", compression)

    for base, dirs, files in self.walk():
      for file in files:
        filename = os.path.join(base, file)
        data = self.open(filename).getvalue()
        file_compression = zipfile.ZIP_STORED if file in exclude_compress else compression
        zip.writestr(filename, data, file_compression)

    return zip_data

v = VDir()

v.open(".emacs").write("data0")
v.open("opt/git-create-branch").write("data1")
v.open("opt/trustme").write("data2")
v.open("opt/virtualenv/quail").write("data3")
v.open("opt/virtualenv")

v.open("opt/./virtualenv/../virtualenv/quail").write("data4")

v.mkdir("opt/virtualenv/readmill/", create_intermediate=True)

v.cp("opt/virtualenv/", "opt/virtualenv_copy")

print "quail value", v.open("opt/virtualenv/quail").read()

print "walk", list(v.walk())


v.open("opt/virtualenv/readmill/")

v.cd("opt")
print "pwd", v.pwd()
print "walk opt", list(v.walk())

v.cd("virtualenv")
print "pwd", v.pwd()
print "walk opt/virtualenv", list(v.walk())

v.cd("..")
print "pwd", v.pwd()
print "walk opt", list(v.walk())

v.cd(".")
print "pwd", v.pwd()
print "walk opt", list(v.walk())

print v.zipfile().getvalue()

try:
  v.open(".emacs/hej")
except DirError, e:
  print e

try:
  v.open("opt/trustme/.ssh")
except DirError, e:
  print e

