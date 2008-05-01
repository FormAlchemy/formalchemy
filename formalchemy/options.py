# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

class Options(dict):
    """The `Options` dictionary class.

    This class is a dict style class, with extra API:

      * parse(self, model)
      * configure(self, **options)
      * reconfigure(self[, **options])
      * get_options(self)
      * new_options(self[, **options])

    """

    def parse(self, model):
        """Parse options set in the subclass `FormAlchemy` from the `model` if defined.

        This will reset any previously set options.

        """

        # Parse model's options.
        d = {}
        if hasattr(model, "FormAlchemy"):
            for k, v in model.FormAlchemy.__dict__.items():
                if not k.startswith('_'):
                    d.__setitem__(k, v)

        self.configure(**d)

    def configure(self, **options):
        """Configure FormAlchemy's default behaviour.

        This will update FormAlchemy's default behaviour with the given
        keyword options. Any other previously set options will be kept intact.

        """

        for option in options:
            if option in ["alias", "display"]:
                if not option in self:
                    self[option] = {}
                self[option].update(options[option])
            else:
                self.update({option:options[option]})

    def reconfigure(self, **options):
        """Reconfigure `Options` from scratch.

        This will clear any previously set option and update FormAlchemy's
        default behaviour with the given keyword options. If no keyword option
        is passed, this will just reset all option.

        """

        self.clear()
        self.configure(**options)

    def get_options(self):
        """Return the current configuration."""
        return self.copy()

    def new_options(self, **options):
        """Return a new Options holding class level options merged with `options`."""
        opts = Options(self.get_options())
        opts.configure(**options)
        return opts
