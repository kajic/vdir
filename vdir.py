import os
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

from vobj import VObj, VIOError
from vfile import VFile

class VDir(VObj, dict):
  def __init__(self, name="", parent=None):
    VObj.__init__(self, name, parent)
    dict.__init__(self)

    self.last_cur = self
    self.cur = self

    self[""] = self
    self["."] = self
    self[".."] = self.parent

  def is_file(self, path=None):
    if not path:
      return False

    try:
      vobj = self.open(path, create=False)
    except VIOError:
      return False
    else:
      return vobj.is_file()    

  def is_directory(self, path=None):
    if not path:
      return True

    try:
      vobj = self.open(path, create=False)
    except VIOError:
      return False
    else:
      return vobj.is_directory()

  def drill(self, path, create_intermediate=True, treat_basename_as_directory=False, overwrite=False):
    dirname = os.path.dirname(path)
    drill_path = dirname.split("/")

    if path.startswith("/"):
      cur = self.root()
    else:
      cur = self.cur

    if treat_basename_as_directory:
      basename = os.path.basename(path)
      if basename:
        drill_path.append(basename)

    for fragment in drill_path:
      if not fragment:
        continue

      if not cur.is_directory():
        if overwrite:
          dir = VDir(name=cur.name, parent=cur.parent)
          cur.parent[cur.name] = dir
          cur = dir
        else:
          raise VIOError("%s is not a directory" % cur.pwd())


      if not cur.has_key(fragment):
        if create_intermediate:
          cur[fragment] = VDir(name=fragment, parent=cur)
        else:
          raise VIOError("%s is not a directory" % os.path.join(cur.pwd(), fragment))
      elif overwrite and cur[fragment].is_file():
        cur[fragment] = VDir(name=fragment, parent=cur)

      cur = cur[fragment]
      
    return cur

  def open(self, path, create=True, mode="rw"):
    vobj = self.drill(path, create_intermediate=create)

    basename = os.path.basename(path)
    if basename:
      if vobj.is_directory():
        dir = vobj
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
      return vobj

  def mkdir(self, path, create_intermediate=False, overwrite=False):
    container_path = os.path.dirname(path)
    if not create_intermediate and not overwrite and not self.is_directory(container_path):
      raise VIOError("%s is not a directory" % container_path)
    else:
      # We can turn on creation of intermediate directories because we 
      # now know that only the last intermediate directory is missing
      create_intermediate = True
      
    cur = self.drill(path, create_intermediate=create_intermediate, treat_basename_as_directory=True, overwrite=overwrite)
    return cur

  def cd(self, path):
    last_cur = self.last_cur
    self.last_cur = self.cur

    if path == "-":
      self.cur = last_cur
    else:
      self.cur = self.drill(path, create_intermediate=False, treat_basename_as_directory=True)
    return self.cur

  def attach(self, vobj, path):
    destination = self.open(path)
    if destination.is_file() or vobj.is_file():
      # If the destination is a file we cannot attach anything to it,
      # therefore we may simply overwrite it. The same is true if vobj
      # is a file; it is safe to overwrite the destination with it.
      destination.parent[destination.name] = vobj
      vobj.name = destination.name
    else:
      destination.drill(vobj.name, treat_basename_as_directory=True)
      destination.cd(vobj.name)
      for base, dirnames, dirs, filenames, files in vobj.walk():
        if not destination.open(base).is_directory():
          destination.mkdir(base, overwrite=True)
        destination.cd(base)
        for cur in dirs+files:
          destination.cur[cur.name] = cur
        destination.cd("-")

  def cp(self, path_or_vobj, new_path=None, move=False):
    if isinstance(path_or_vobj, str):
      original = self.open(path_or_vobj)
      duplicate = deepcopy(original)
    else:
      duplicate = deepcopy(path_or_vobj)

    self.attach(duplicate, new_path)
    if move:
      original.unattach()

    return duplicate

  def mv(self, path_or_vobj, new_path):
    self.cp(path_or_vobj, new_path, move=True)

  def rm(self, path_or_vobj="."):
    if isinstance(path_or_vobj, str):
      vobj = self.open(path_or_vobj)
    else:
      vobj = path_or_vobj
    vobj.unattach()

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

  def compress(self, mode="w", compression=ZIP_DEFLATED, exclude_compress=[]):
    out = VFile("vdir.zip")
    zipfile = ZipFile(out, "w", compression)

    for base, dirnames, dirs, filenames, files in self.walk():
      for name, file in zip(filenames, files):
        path = os.path.join(base, name)
        data = file.getvalue()
        file_compression = ZIP_STORED if name in exclude_compress else compression
        zipfile.writestr(path, data, file_compression)

    out.seek(0)
    return out
