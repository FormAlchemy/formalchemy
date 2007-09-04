# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

__all__ = ["FormAlchemyError", "RenderError", "UnboundModelError",
    "InvalidColumnError", "InvalidCollectionError"]
__doc__ = """FormAlchemy Exceptions

This module holds all FormAlchemy's exceptions.

"""

class FormAlchemyError(Exception):
    """Base FormAlchemy error class."""

class RenderError(FormAlchemyError):
    """Raised when an error occurs during rendering."""

class UnboundModelError(RenderError):
    """Raised when rendering is called but no model has been bound to it."""

    def __str__(self):
        return "No SQLAlchemy mapped class was bound to this class yet. Use the .bind() method."

class InvalidColumnError(RenderError):
    """Raised when column level rendering classes don't have a valid column set."""

class InvalidCollectionError(RenderError):
    """Raised when collection level rendering classes don't have a valid collection set."""
