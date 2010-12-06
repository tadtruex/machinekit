#!/usr/bin/env python
# vim: sts=4 sw=4 et

import os
import gtk, gobject

import emc
import gremlin
import rs274.glcanon

class HAL_Gremlin(gremlin.Gremlin):
    __gtype_name__ = "HAL_Gremlin"
    __gproperties__ = {
        'view' : ( gobject.TYPE_STRING, 'View type', 'Default view: x, y, z, p',
                    'z', gobject.PARAM_READWRITE | gobject.PARAM_CONSTRUCT),
        'enable_dro' : ( gobject.TYPE_BOOLEAN, 'Enable DRO', 'Draw DRO on plot or not',
                    True, gobject.PARAM_READWRITE | gobject.PARAM_CONSTRUCT),
    }
    __gproperties = __gproperties__
    def __init__(self, *a, **kw):
        inifile = os.environ.get('INI_FILE_NAME', '/dev/null')
        inifile = emc.ini(inifile)
        gremlin.Gremlin.__init__(self, inifile)

        self.show()

    def do_get_property(self, property):
        name = property.name.replace('-', '_')
        if name == 'view':
            return self.current_view
        elif name in self.__gproperties.keys():
            return getattr(self, name)
        else:
            raise AttributeError('unknown property %s' % property.name)

    def do_set_property(self, property, value):
        name = property.name.replace('-', '_')

        if name == 'view':
            view = value.lower()
            if view not in ['x', 'y', 'z', 'p']:
                return False
            self.current_view = view
            if self.initialised:
                self.set_current_view()

        elif name == 'enable_dro':
            self.enable_dro = value
        elif name in self.__gproperties.keys():
            setattr(self, name, value)
        else:
            raise AttributeError('unknown property %s' % property.name)

        self.queue_draw()
        return True

    def posstrs(self):
        l, h, p, d = gremlin.Gremlin.posstrs(self)
        if self.enable_dro:
            return l, h, p, d
        return l, h, [''], ['']

    def realize(self, widget):
        gremlin.Gremlin.realize(self, widget)
        gobject.timeout_add(1000, self.poll_file_change)

    def poll_file_change(self):
        s = self.stat
        s.poll()
        if s.file and self._current_file != s.file:
            self._load(s.file)
        return True

    @rs274.glcanon.with_context
    def _load(self, filename):
        return self.load(filename)
