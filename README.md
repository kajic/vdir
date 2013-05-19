vdir
====

virtual directories and files

Some examples of what you can do:

```python
from vdir import VDir

vd = VDir()

# Write to file
vd.open("path/to/some/file").write("your data")

# Create directory, go inside it, and write to some other file
vd.mkdir("foo")
vd.cd("foo")
vd.open("bar").write("something else") # writes to /foo/bar

# Read from file
vd.open("bar").read()

# Get the current path
vd.pwd()

# Copy directory and all its contents
vd.cp("/foo", "/foo_copy")

# Move the copied directory somewhere else
vd.mv("/foo_copy", "/foo_moved")

# Create a file, then remove it
vd.open("unnecessary").write("foo")
vd.rm("unnecessary")

# Walk over all directories and files in the virtual directory
for base, dirnames, dirs, filenames, files in self.walk():
  pass
  
# Create a zip from the virtual directory
zip = vd.compress()

# Get zip data
zip.read()
```
