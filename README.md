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

# walk over all directories and files in the virtual directory
for base, dirnames, dirs, filenames, files in self.walk():
  pass
  
# create zipfile from the virtual directory
zipfile = vd.zipfile()

```
