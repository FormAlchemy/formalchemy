import os
import cgi
import shutil
import tempfile
from StringIO import StringIO
from nose import with_setup

from formalchemy.tests import *
from formalchemy.tests.test_binary import *
from formalchemy.ext.fsblob import FileFieldRenderer as BaseFile
from formalchemy.ext.fsblob import ImageFieldRenderer as BaseImage
from formalchemy.ext.fsblob import file_extension

TEMPDIR = tempfile.mkdtemp()

class FileFieldRenderer(BaseFile):
    storage_path = TEMPDIR

class ImageFieldRenderer(BaseImage):
    storage_path = TEMPDIR

def setup_tempdir():
    if not os.path.isdir(TEMPDIR):
        os.makedirs(TEMPDIR)

def teardown_tempdir():
    if os.path.isdir(TEMPDIR):
        shutil.rmtree(TEMPDIR)

@with_setup(setup_tempdir, teardown_tempdir)
def test_file_storage():
    fs = FieldSet(Binaries)
    record = fs.model
    fs.configure(include=[fs.file.with_renderer(FileFieldRenderer)])

    assert 'test.js' not in fs.render()

    data = get_fields(TEST_DATA)
    fs.rebind(data=data)
    assert fs.validate() is True
    assert fs.file.value.endswith('/test.js')
    fs.sync()
    filepath = os.path.join(TEMPDIR, fs.file.value)
    assert os.path.isfile(filepath), filepath

    view = fs.file.render_readonly()
    value = '<a href="/%s">test.js (1 KB)</a>' % fs.file.value
    assert value in view, '%s != %s' % (value, view)

    assert value in fs.file.render(), fs.render()

@with_setup(setup_tempdir, teardown_tempdir)
def test_image_storage():
    fs = FieldSet(Binaries)
    record = fs.model
    fs.configure(include=[fs.file.with_renderer(ImageFieldRenderer)])

    assert 'test.js' not in fs.render()

    data = get_fields(TEST_DATA)
    fs.rebind(data=data)
    assert fs.validate() is True
    fs.sync()
    assert fs.file.value.endswith('/test.js')
    filepath = os.path.join(TEMPDIR, fs.file.value)
    assert os.path.isfile(filepath), filepath

    view = fs.file.render_readonly()
    v = fs.file.value
    value = '<a href="/%s"><img alt="test.js (1 KB)" src="/%s" /></a>' % (v, v)
    assert value in view, '%s != %s' % (value, view)

    assert value in fs.file.render(), fs.render()

@with_setup(setup_tempdir, teardown_tempdir)
def test_file_validation():
    fs = FieldSet(Binaries)
    record = fs.model
    fs.configure(include=[
        fs.file.with_renderer(
                    FileFieldRenderer
                ).validate(file_extension(['js']))])
    data = get_fields(TEST_DATA)
    fs.rebind(data=data)
    assert fs.validate() is True

    fs.configure(include=[
        fs.file.with_renderer(
                    FileFieldRenderer
                ).validate(file_extension(['txt']))])
    data = get_fields(TEST_DATA)
    fs.rebind(data=data)
    assert fs.validate() is False

