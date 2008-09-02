import cgi
from StringIO import StringIO

from fields import FileFieldRenderer
from regression import *

BOUNDARY='testdata'
ENVIRON = {
        'REQUEST_METHOD':'POST',
        'CONTENT_TYPE': 'multipart/form-data;boundary="%s"' % BOUNDARY
        }
TEST_DATA = '''--%s
Content-Disposition: form-data; name="Binaries--file"; filename="test.js"
Content-Type: application/x-javascript

var test = null;

--%s--
''' % (BOUNDARY, BOUNDARY)
EMPTY_DATA = '''--%s
Content-Disposition: form-data; name="Binaries--file"; filename=""
Content-Type: application/x-javascript

--%s--
''' % (BOUNDARY, BOUNDARY)
REMOVE_DATA = '''--%s
Content-Disposition: form-data; name="Binaries--file--remove"
1
--%s
Content-Disposition: form-data; name="Binaries--file"; filename=""
Content-Type: application/x-javascript

--%s--
''' % (BOUNDARY, BOUNDARY, BOUNDARY)


def get_fields(data):
    return cgi.FieldStorage(fp=StringIO(data), environ=ENVIRON)

__doc__ = r"""

Notice that those tests assume that the FileFieldRenderer work with Binary type
*and* String type if you only want to store file path in your DB.

Configure a fieldset with a file field

    >>> record = Three()
    >>> fs = FieldSet(record)
    >>> fs.configure(include=[fs.bar.with_renderer(FileFieldRenderer)])
    >>> isinstance(fs.bar.renderer, FileFieldRenderer)
    True

At creation time only the input field is rendered

    >>> print fs.render()
    <div>
     <label class="field_opt" for="Three--bar">
      Bar
     </label>
     <input id="Three--bar" name="Three--bar" type="file" />
    </div>
    <script type="text/javascript">
     //<![CDATA[
    document.getElementById("Three--bar").focus();
    //]]>
    </script>

If the field has a value then we add a check box to remove it

    >>> record.bar = '/path/to/file'
    >>> print fs.render()
    <div>
     <label class="field_opt" for="Three--bar">
      Bar
     </label>
     <input id="Three--bar" name="Three--bar" type="file" />
     <input id="Three--bar--remove" name="Three--bar--remove" type="checkbox" value="1" />
     <label for="Three--bar--remove">
      Remove
     </label>
    </div>
    <script type="text/javascript">
     //<![CDATA[
    document.getElementById("Three--bar").focus();
    //]]>
    </script>

Now submit form with empty value

    >>> fs.rebind(data={'Three--bar':''})
    >>> fs.validate()
    True
    >>> fs.sync()

The field value does not change

    >>> print record.bar
    /path/to/file

Try to remove it by checking the checkbox

    >>> fs.rebind(data={'Three--bar':'', 'Three--bar--remove':'1'})
    >>> fs.validate()
    True
    >>> fs.sync()

The field value is removed

    >>> print record.bar
    <BLANKLINE>

Also check that this work with cgi.FieldStorage

    >>> record = Binaries()
    >>> fs = FieldSet(record)

We need test data

    >>> data = get_fields(TEST_DATA)
    >>> print data.getfirst('Binaries--file')
    var test = null;
    <BLANKLINE>

    >>> fs.rebind(data=data)
    >>> if fs.validate(): fs.sync()

We get the file, yeah.

    >>> print record.file
    var test = null;
    <BLANKLINE>

Now submit form with empty value

    >>> data = get_fields(EMPTY_DATA)
    >>> fs.rebind(data=data)
    >>> if fs.validate(): fs.sync()

The field value dos not change

    >>> print record.file
    var test = null;
    <BLANKLINE>

Remove file

    >>> data = get_fields(REMOVE_DATA)
    >>> fs.rebind(data=data)
    >>> if fs.validate(): fs.sync()

The field value dos not change

    >>> print record.file
    <BLANKLINE>

"""
