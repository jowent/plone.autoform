from z3c.form import field

from plone.z3cform.fieldsets.group import GroupFactory

from plone.autoform.utils import process_field_moves, process_fields

_marker = object()

class AutoFields(object):
    """Mixin class for the WidgetsView and AutoExtensibleForm classes.
    Takes care of actually processing field updates
    """

    schema = None
    additional_schemata = ()
    
    fields = field.Fields()
    groups = []
    
    ignorePrefix = False
    autoGroups = False
    
    def updateFieldsFromSchemata(self):
        
        # Turn fields into an instance variable, since we will be modifying it
        self.fields = field.Fields(self.fields)
        
        # Copy groups to an instance variable and ensure that we have
        # the more mutable factories, rather than 'Group' subclasses

        self.groups = []

        for g in self.groups:
            group_name = getattr(g, '__name__', g.label)
            fieldset_group = GroupFactory(group_name,
                                          field.Fields(g.fields),
                                          g.label,
                                          getattr(g, 'description', None))
            self.groups.append(fieldset_group)
        
        prefixes = {}
        
        # Set up all widgets, modes, omitted fields and fieldsets
        if self.schema is not None:
            process_fields(self, self.schema)
            for schema in self.additional_schemata:
                
                # Find the prefix to use for this form and cache for next round
                prefix = self.getPrefix(schema)
                if prefix and prefix in prefixes:
                    prefix = schema.__identifier__
                prefixes[schema] = prefix
                
                # By default, there's no default group, i.e. fields go 
                # straight into the default fieldset
                
                default_group = None
                
                # Create groups from schemata if requested and set default 
                # group

                if self.autoGroups:
                    group_name = schema.__name__
                    
                    # Look for group - note that previous process_fields
                    # may have changed the groups list, so we can't easily
                    # store this in a dict.
                    found = False
                    for g in self.groups:
                        if group_name == getattr(g, '__name__', g.label):
                            found = True
                            break
                    
                    if not found:
                        fieldset_group = GroupFactory(group_name,
                                                      field.Fields(),
                                                      group_name,
                                                      schema.__doc__)
                        self.groups.append(fieldset_group)

                    default_group = group_name
                    
                process_fields(self, schema, prefix=prefix, default_group=default_group)
        
        # Then process relative field movements. The base schema is processed
        # last to allow it to override any movements made in additional 
        # schemata.
        if self.schema is not None:
            for schema in self.additional_schemata:
                process_field_moves(self, schema, prefix=prefixes[schema])
            process_field_moves(self, self.schema)
            
    def getPrefix(self, schema):
        """Get the preferred prefix for the given schema
        """
        if self.ignorePrefix:
            return ''
        return schema.__name__