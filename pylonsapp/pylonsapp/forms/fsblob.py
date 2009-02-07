# -*- coding: utf-8 -*-
from pylonsapp import model
from pylonsapp.forms import FieldSet
from formalchemy.ext.fsblob import FileFieldRenderer

Files = FieldSet(model.Files)
Files.configure(options=[Files.path.with_renderer(FileFieldRenderer)])


