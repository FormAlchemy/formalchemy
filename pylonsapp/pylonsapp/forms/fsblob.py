# -*- coding: utf-8 -*-
from pylons import config
from pylonsapp import model
from pylonsapp.forms import FieldSet
from formalchemy.ext.fsblob import FileFieldRenderer

# get the storage path from configuration
FileFieldRenderer.storage_path = config['app_conf']['storage_path']

Files = FieldSet(model.Files)
Files.configure(options=[Files.path.with_renderer(FileFieldRenderer)])


