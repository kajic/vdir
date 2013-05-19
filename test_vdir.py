import unittest

from vdir import VFile, VDir, VIOError

class TestVFile(unittest.TestCase):
  def test_read_write(self):
    data = "foo"

    file = VFile(".emacs")
    file.write(data)

    file.seek(0)

    self.assertEqual(data, file.read())
  

class TestVDir(unittest.TestCase):
  def setUp(self):
    self.vd = VDir()

  def assertIsFile(self, file):
    self.assertTrue(hasattr(file, "read"))
    self.assertTrue(hasattr(file, "write"))    

  def test_open(self):
    file = self.vd.open(".emacs")

    self.assertEqual(".emacs", file.name)
    self.assertIsFile(file)

  def test_open_nested_file(self):
    file = self.vd.open("opt/.git-create-branch")

    self.assertEqual(".git-create-branch", file.name)
    self.assertIsFile(file)

  def test_mkdir(self):
    self.vd.mkdir("foo")
    
    dir = self.vd.open("foo")
    self.assertTrue(hasattr(dir, "drill"))

  def test_mkdir_intermediate(self):
    self.vd.mkdir("foo/bar", create_intermediate=True)
    
    dir = self.vd.open("foo/bar")
    self.assertTrue(hasattr(dir, "drill"))
    
  def test_mkdir_no_intermediate(self):
    self.assertRaises(VIOError, self.vd.mkdir, "bar/foo")

  def test_cd(self):
    self.vd.mkdir("foo/bar/baz/qux", create_intermediate=True)

    self.vd.cd("foo")
    self.assertEqual("foo", self.vd.cur.name)

    self.vd.cd("bar/baz")
    self.assertEqual("baz", self.vd.cur.name)

    self.vd.cd("qux")
    self.assertEqual("qux", self.vd.cur.name)

    self.assertRaises(VIOError, self.vd.cd, "foo")

  def test_cd_parent(self):
    self.vd.mkdir("foo/bar/baz/qux", create_intermediate=True)

    self.vd.cd("foo/bar/baz/qux")

    self.vd.cd("..")
    self.assertEqual("baz", self.vd.cur.name)

    self.vd.cd("../../")
    self.assertEqual("foo", self.vd.cur.name)

    self.vd.cd("bar/baz/../baz")
    self.assertEqual("baz", self.vd.cur.name)

  def test_cd_nop(self):
    self.vd.mkdir("foo/bar/baz/qux", create_intermediate=True)

    self.vd.cd("foo/bar/baz")

    self.vd.cd("//")
    self.assertEqual("baz", self.vd.cur.name)

    self.vd.cd("./.")
    self.assertEqual("baz", self.vd.cur.name)

  def test_pwd(self):
    self.vd.mkdir("foo/bar/baz/qux", create_intermediate=True)
    
    self.assertEqual(".", self.vd.pwd())

    self.vd.cd("foo")
    self.assertEqual("./foo", self.vd.pwd())

    self.vd.cd("bar")
    self.assertEqual("./foo/bar", self.vd.pwd())
    
  def test_cp_dir(self):
    vd = VDir()

    vd.open("opt/virtualenv/quail").write("foo")
    vd.open("opt/virtualenv/egg").write("bar")
        
    vd.cp("opt/virtualenv", "opt/virtualenv_copy")

    # Assert the copied files contain the same data
    original = vd.open("opt/virtualenv/quail")
    duplicate = vd.open("opt/virtualenv_copy/quail")
    self.assertEqual(original.read(), duplicate.read())

    original = vd.open("opt/virtualenv/egg")
    duplicate = vd.open("opt/virtualenv_copy/egg")
    self.assertEqual(original.read(), duplicate.read())
    
    # Assert writing to the original file does not affect the copied file
    original.write("bar")
    original.seek(0)
    duplicate.seek(0)
    self.assertNotEqual(original.read(), duplicate.read())

  def test_cp_dir_trailing_slash(self):
    vd = VDir()

    vd.open("opt/virtualenv/quail").write("foo")
    vd.open("opt/virtualenv/egg").write("bar")
        
    vd.cp("opt/virtualenv/", "opt/virtualenv_copy")

    # Assert the copied files contain the same data
    original = vd.open("opt/virtualenv/quail")
    duplicate = vd.open("opt/virtualenv_copy/quail")
    self.assertEqual(original.read(), duplicate.read())

    original = vd.open("opt/virtualenv/egg")
    duplicate = vd.open("opt/virtualenv_copy/egg")
    self.assertEqual(original.read(), duplicate.read())

  def test_cp_dir_into_dir(self):
    vd = VDir()

    vd.open("opt/virtualenv/quail").write("foo")
    vd.open("opt/virtualenv/egg").write("bar")
        
    vd.cp("opt/virtualenv/", "opt/virtualenv_copy/")

    # Assert the copied files contain the same data
    original = vd.open("opt/virtualenv/quail")
    duplicate = vd.open("opt/virtualenv_copy/virtualenv/quail")
    self.assertEqual(original.read(), duplicate.read())

    original = vd.open("opt/virtualenv/egg")
    duplicate = vd.open("opt/virtualenv_copy/virtualenv/egg")
    self.assertEqual(original.read(), duplicate.read())
    
  def test_cp_dir_into_existing_dir(self):
    vd = VDir()

    vd.open("opt/virtualenv/quail").write("foo")
    vd.open("opt/virtualenv/egg").write("bar")

    vd.mkdir("opt/virtualenv_copy/virtualdir/", create_intermediate=True)
        
    vd.cp("opt/virtualenv/", "opt/virtualenv_copy/")

    # Assert the copied files contain the same data
    original = vd.open("opt/virtualenv/quail")
    duplicate = vd.open("opt/virtualenv_copy/virtualenv/quail")
    self.assertEqual(original.read(), duplicate.read())

    original = vd.open("opt/virtualenv/egg")
    duplicate = vd.open("opt/virtualenv_copy/virtualenv/egg")
    self.assertEqual(original.read(), duplicate.read())

  def test_cp_dir_into_existing_dir_with_content(self):
    vd = VDir()

    vd.open("opt/virtualenv_copy/virtualenv/wing").write("baz")
        
    vd.cp("opt/virtualenv/", "opt/virtualenv_copy/")

    # Assert that the wing file has not been overwritten
    wing = vd.open("opt/virtualenv_copy/virtualenv/wing")
    self.assertEqual("baz", wing.read())

  def test_cp_dir_into_existing_dir_with_same_content(self):
    vd = VDir()

    vd.open("opt/virtualenv/wing").write("flyes")
    vd.open("opt/virtualenv_copy/virtualenv/wing").write("baz")
        
    vd.cp("opt/virtualenv/", "opt/virtualenv_copy/")

    # Assert that the file has been overwritten
    wing = vd.open("opt/virtualenv_copy/virtualenv/wing")
    self.assertEqual("flyes", wing.read())
