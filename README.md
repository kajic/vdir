vdir
====

virtual directories and files

Some examples of what you can do:

```python
from vdir import VDir

vd = VDir()

# write to file
vd.open("path/to/some/file").write("your data")

# create directory, go inside it, and write to some other file
vd.mkdir("foo")
vd.cd("foo")
vd.open("bar").write("something else") # writes to /foo/bar

# see the current path
vd.pwd()

# copy a directory and all its contents
vd.cp("/foo", "/foo_copy")

# move the copy somewhere else
vd.mv("/foo_copy", "/foo_moved")

# create a file, then remove it
vd.open("unnecessary").write("foo")
vd.rm("unnecessary")

# walk over all directories and files in the virtual directory
for base, dirnames, dirs, filenames, files in self.walk():
  pass
  
# create zip from the virtual directory
zip = vd.compress()

# show raw zipfile data
zip.read()
```
