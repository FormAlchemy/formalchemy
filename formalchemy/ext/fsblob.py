# -*- coding: utf-8 -*-
import os
import stat
import cgi
import string
import random
import shutil
import formalchemy.helpers as h
from formalchemy.fields import FileFieldRenderer as Base
from formalchemy.fields import FieldRenderer
from formalchemy.validators import regex
from formalchemy.i18n import _

try:
    from pylons import config
except ImportError:
    config = {}

__all__ = ['file_extension', 'image_extension',
           'FileFieldRenderer', 'ImageFieldRenderer']

def file_extension(extensions=[], errormsg=None):
    """Validate a file extension.
    """
    if errormsg is None:
        errormsg = _('Invalid file extension. Must be %s'%', '.join(extensions))
    return regex(r'^.+\.(%s)$' % '|'.join(extensions), errormsg=errormsg)

def image_extension(extensions=['jpeg', 'jpg', 'gif', 'png']):
    """Validate an image extension. default valid extensions are jpeg, jpg,
    gif, png.
    """
    errormsg = _('Invalid image file. Must be %s'%', '.join(extensions))
    return file_extension(extensions, errormsg=errormsg)

def normalized_basename(path):
    """
    >>> print normalized_basename(u'c:\\Prog files\My fil\xe9.jpg')
    My_fil.jpg

    >>> print normalized_basename('c:\\Prog files\My fil\xc3\xa9.jpg')
    My_fil.jpg

    """
    if isinstance(path, str):
        path = path.decode('utf-8', 'ignore').encode('ascii', 'ignore')
    if isinstance(path, unicode):
        path = path.encode('ascii', 'ignore')
    filename = path.split('/')[-1]
    filename = filename.split('\\')[-1]
    return filename.replace(' ', '_')


class FileFieldRenderer(Base):
    """render a file input field stored on file system
    """

    url_prefix = '/'

    @property
    def storage_path(self):
        if 'app_conf' in config:
            config['app_conf'].get('storage_path', '')

    def __init__(self, *args, **kwargs):
        if not self.storage_path or not os.path.isdir(self.storage_path):
            raise ValueError(
                    'storage_path must be set to a valid path. Got %r' % self.storage_path)
        Base.__init__(self, *args, **kwargs)
        self._path = None

    def relative_path(self, filename):
        """return the file path relative to root
        """
        rdir = lambda: ''.join(random.sample(string.ascii_lowercase, 3))
        path = '/'.join([rdir(), rdir(), rdir(), filename])
        return path

    def get_url(self, relative_path):
        """return the file url. by default return the relative path stored in
        the DB
        """
        return self.url_prefix + relative_path

    def get_size(self):
        relative_path = self.field.value
        if relative_path:
            filepath = os.path.join(self.storage_path,
                                    relative_path.replace('/', os.sep))
            if os.path.isfile(filepath):
                return os.stat(filepath)[stat.ST_SIZE]
        return 0

    def render(self, **kwargs):
        """render a file field and the file preview
        """
        html = Base.render(self, **kwargs)
        value = self.field.value
        if value:
            html += self.render_readonly()

            # add the old value for objects not yet stored
            old_value = '%s--old' % self.name
            html += h.hidden_field(old_value, value=value)
        return html


    def render_readonly(self, **kwargs):
        """render the filename and the binary size in a human readable with a
        link to the file itself.
        """
        value = self.field.value
        if value:
            content = '%s (%s)' % (normalized_basename(value),
                                 self.readable_size())
            return h.content_tag('a', content,
                                 href=self.get_url(value), **kwargs)
        return ''

    def _serialized_value(self):
        name = self.name
        if '%s--remove' % self.name in self.params:
            self._path = None
            return None
        elif name in self.params:
            return self.params.getone(self.name)
        old_value = '%s--old' % self.name
        if old_value in self.params:
            self._path = self.params.getone(old_value)
            return self._path
        raise RuntimeError('This should never occurs')

    def deserialize(self):
        if self._path:
            return self._path
        data = FieldRenderer.deserialize(self)
        if isinstance(data, cgi.FieldStorage):
            filename = normalized_basename(data.filename)
            self._path = self.relative_path(filename)
            filepath = os.path.join(self.storage_path,
                                    self._path.replace('/', os.sep))
            dirname = os.path.dirname(filepath)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            fd = open(filepath, 'wb')
            shutil.copyfileobj(data.file, fd)
            fd.close()
            return self._path
        checkbox_name = '%s--remove' % self.name
        if not data and not self.params.has_key(checkbox_name):
            data = getattr(self.field.model, self.field.name)

        # get value from old_value if needed
        old_value = '%s--old' % self.name
        checkbox_name = '%s--remove' % self.name
        if not data and not self.params.has_key(checkbox_name) \
                    and self.params.has_key(old_value):
            return self.params[old_value]
        return data is not None and data or ''

    @classmethod
    def new(cls, storage_path, url_prefix='/'):
        """Return a new class::

            >>> FileFieldRenderer.new(storage_path='/') # doctest: +ELLIPSIS
            <class 'formalchemy.ext.fsblob.ConfiguredFileFieldRenderer_...'>
            >>> ImageFieldRenderer.new(storage_path='/') # doctest: +ELLIPSIS
            <class 'formalchemy.ext.fsblob.ConfiguredImageFieldRenderer_...'>
        """
        if url_prefix[-1] != '/':
            url_prefix += '/'
        name = 'Configured%s_%s' % (cls.__name__, str(random.random())[2:])
        return type(name, (cls,),
                    dict(storage_path=storage_path,
                    url_prefix=url_prefix))


class ImageFieldRenderer(FileFieldRenderer):

    def render_readonly(self, **kwargs):
        """render the image tag with a link to the image itself.
        """
        value = self.field.value
        if value:
            url = self.get_url(value)
            content = '%s (%s)' % (normalized_basename(value),
                                 self.readable_size())
            tag = h.tag('img', src=url, alt=content)
            return h.content_tag('a', tag, href=url, **kwargs)
        return ''

