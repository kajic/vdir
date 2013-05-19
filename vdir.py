import os 
import zipfile

from copy import deepcopy
from StringIO import StringIO

class VIOError(IOError): pass

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

  def __str__(self):
    return "<%s>: %s" % (self.name,  super(VDir, self).__str__())

  def __lt__(self, other):
    return id(self)<id(other)

  def is_root(self):
    return self == self.parent 

  def pwd(self):
    cur = self.cur
    path = [cur.name]

    while not cur.is_root():
      cur = cur.parent
      path.append(cur.name)

    path.reverse()
    return "/".join(path)

class VFile(VBase, StringIO):
  def __init__(self, name, parent=None, mode="rw"):
    VBase.__init__(self, name, parent)
    StringIO.__init__(self)

    self.set_mode(mode)

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

class VDir(VBase, dict):
  def __init__(self, name=".", parent=None):
    VBase.__init__(self, name, parent)
    dict.__init__(self)

    self.last_cur = self
    self.cur = self

    self[""] = self
    self["."] = self
    self[".."] = self.parent

  def is_directory(self, path=None):
    if not path:
      return True

    try:
      vobj = self.open(path, create=False)
    except VIOError:
      return False
    else:
      return vobj.is_directory()

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

      if not hasattr(cur, "has_key"):
        raise VIOError("%s is not a directory" % cur.pwd())

      if not cur.has_key(fragment):
        if create_intermediate:
          cur[fragment] = VDir(name=fragment, parent=cur)
        else:
          raise VIOError("%s is not a directory" % os.path.join(cur.pwd(), fragment))

      cur = cur[fragment]
      
    return cur

  def open(self, path, create=True, mode="rw"):
    vobj = self.drill(path, create_intermediate=create)

    basename = os.path.basename(path)
    if basename:
      if hasattr(dir, "has_key"):
        if not dir.has_key(basename):
          if create:
            dir[basename] = VFile(basename, dir, mode)
          else:
            raise VIOError("%s does not exist", path)
        elif hasattr(dir[basename], "set_mode"):
          dir[basename].set_mode(mode)

        return dir[basename]
      else:
        raise VIOError("%s is not a directory" % os.path.dirname(path))
    else:
      return dir

  def mkdir(self, path, create_intermediate=False):
    container_path = os.path.dirname(path)
    if not create_intermediate and not self.is_directory(container_path):
      raise VIOError("%s is not a directory" % container_path)
    else:
      # We can turn on creation of intermediate directories because we 
      # now know that only the last intermediate directory is missing
      create_intermediate = True
      
    cur = self.drill(path, create_intermediate=create_intermediate, treat_basename_as_directory=True)
    return cur

  def cd(self, path):
    last_cur = self.last_cur
    self.last_cur = self.cur
    if path == "-":
      self.cur = last_cur
    else:      
      self.cur = self.drill(path, create_intermediate=False, treat_basename_as_directory=True)
    return self.cur

  def cp(self, path, new_path=None):
    original = self.open(path)

    duplicate = deepcopy(original)

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
      dirs = []
      filenames = []
      files = []

      for name, vobj in dir.items():
        if name in ["", ".", ".."]:
          continue

        if vobj.is_directory():
          dirnames.append(name)
          dirs.append(vobj)
        else:
          filenames.append(name)
          files.append(vobj)

      yield ("/".join(path), dirnames, dirs, filenames, files)

      # Add child directories to walk candiates
      candiates.extend([(dir[name], path+[name]) for name in dirnames])

  def zipfile(self, mode="w", compression=zipfile.ZIP_DEFLATED, exclude_compress=[]):
    zip_data = VFile("file.zip")
    zip = zipfile.ZipFile(zip_data, "w", compression)

    for base, dirs, files in self.walk():
      for file in files:
        filename = os.path.join(base, file)
        data = self.open(filename).getvalue()
        file_compression = zipfile.ZIP_STORED if file in exclude_compress else compression
        zip.writestr(filename, data, file_compression)

    return zip_data
