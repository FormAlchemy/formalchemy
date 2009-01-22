# -*- coding: utf-8 -*-
from pylons import config
from adminapp import model
from formalchemy import FieldSet
from formalchemy.ext.fsblob import FileFieldRenderer

FileFieldRenderer.storage_path = config['app_conf']['storage_path']

Files = FieldSet(model.Files)
Files.configure(options=[Files.path.with_renderer(FileFieldRenderer)])


