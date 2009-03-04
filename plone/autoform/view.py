from zope.interface import implements

from z3c.form.form import DisplayForm
from z3c.form.interfaces import IFormLayer

from Acquisition import Explicit
from plone.z3cform import z2

from plone.autoform.interfaces import IWidgetsView
from plone.autoform.base import AutoFields

class WidgetsView(AutoFields, DisplayForm, Explicit):
    """Mix-in to allow widgets (in view mode) to be accesed from browser
    views.
    """
    
    implements(IWidgetsView)
    
    # You should set one or more of these, or the 'fields' variable
    
    schema = None
    additional_schemata = ()
    
    request_layer = IFormLayer

    def update(self):
        pass

    def render(self):
        if getattr(self, 'index', None) is not None:
            return self.index()
        raise NotImplemented("You must implement the 'render' method")
    
    # Helper methods
    
    def __call__(self):
        z2.switch_on(self)
        self._update()
        self.update()
        return self.render()
    
    def _update(self):
        self.updateFieldsFromSchemata()
        self.updateWidgets()
        
        # shortcut 'widget' dictionary for all fieldsets
        self.w = {}
        for k, v in self.widgets.items():
            self.w[k] = v
        
        groups = []
        self.fieldsets = {}
        
        for idx, groupFactory in enumerate(self.groups):
            group = groupFactory(self.context, self.request, self)
            group.update()
            
            for k, v in group.widgets.items():
                self.w[k] = v
            
            groups.append(group)
            
            group_name = getattr(group, '__name__', str(idx))
            self.fieldsets[group_name] = group
    
        self.groups = tuple(groups)