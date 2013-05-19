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
cd.open("bar").write("something else") # writes to /foo/bar

```
