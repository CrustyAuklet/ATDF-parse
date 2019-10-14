import logging
from lxml import etree

LOGGER = logging.getLogger('atdf.modules')

### Heirachy of a atdf module
# Module
#     register-group
#         register
#             bitfield
#         register-group (different attributes)
#     value-group
#         value
#     interrupt-group
#         interrupt
#     parameters (only in CPU module?)
#         param

class BitField:
    def __init__(self, xmlNode):
        self.name = xmlNode.get('name')
        self.description = xmlNode.get('caption')
        self.mask = int(xmlNode.get('mask'), 16)
        self.valueType = xmlNode.get('values')

    def __repr__(self):
        return f'{self.name} field'

class Register:
    def __init__(self, xmlNode):
        assert xmlNode.tag == 'register'  # must be a register node!
        self.name = xmlNode.get('name')
        self.offset = int(xmlNode.get('offset'), 16)
        self.size = int(xmlNode.get('size'))
        self.description = xmlNode.get('caption')
        # create a list of fields in this register
        self.fields = [ self._processChild(c) for c in xmlNode.getchildren() ]

    def _processChild(self, xmlNode):
        assert xmlNode.tag == 'bitfield'
        return BitField(xmlNode)

    def __repr__(self):
        return f'{self.name} ({self.size} bytes)'


class GroupInstance:
    def __init__(self, xmlNode):
        # this should be a sub-group (reg group inside another reg-group) and should have no children
        assert xmlNode.tag == 'register-group' and xmlNode.getparent().tag == 'register-group'
        assert len(xmlNode.getchildren()) == 0
        self.name = xmlNode.get('name')
        self.offset = int(xmlNode.get('offset'), 16)
        self.description = xmlNode.get('caption')
        self.typename = xmlNode.get('name-in-module')

    def __repr__(self):
        return f'{self.name} instance'

class RegisterGroup:
    def __init__(self, xmlNode):
        assert xmlNode.tag == 'register-group'  # must be a register group node!
        self.name = xmlNode.get('name')

        # Some groups have no size... specifically the lock bits?!
        try:
            self.size = int(xmlNode.get('size'))
        except:
            LOGGER.warning(f"{self.name} has no size! setting to 1")
            self.size = 1

        self.description = xmlNode.get('caption')
        # Create a list of registers and sub-groups in this RegisterGroup
        self.registers = [ self._processChild(c) for c in xmlNode.getchildren() ]

    def _processChild(self, xmlNode):
        # only know how to handle registers and sub-groups within a reg-group
        assert xmlNode.tag == 'register' or xmlNode.tag == 'register-group'
        if xmlNode.tag == 'register':
            return Register(xmlNode)
        elif xmlNode.tag == 'register-group':
            return GroupInstance(xmlNode)

    def __repr__(self):
        return f'{self.name} : {len(self.registers)} registers'

class ValueGroup:
    def __init__(self, xmlNode):
        assert xmlNode.tag == 'value-group'
        self.name = xmlNode.get('name')
        self.description = xmlNode.get('caption')
        self.values = []
        for val in xmlNode.getchildren():
            self.values.append( { 'name':val.get('name'), 'value':int(val.get('value'), 16), 'description':val.get('caption') } )

    def __repr__(self):
        return f'{self.name} : {len(self.values)} Enums'

class InterruptGroup:
    def __init__(self, xmlNode):
        assert xmlNode.tag == 'interrupt-group'
        self.name = xmlNode.get('name')
        self.interrupts = []
        for val in xmlNode.getchildren():
            self.interrupts.append( { 'name':val.get('name'), 'index':int(val.get('index')), 'description':val.get('caption') } )

    def __repr__(self):
        return f'{self.name} : {len(self.interrupts)} Interrupts'

class Module:
    def __init__(self, xmlNode):
        assert xmlNode.tag == 'module' and xmlNode.getparent().tag == 'modules'
        self.name = xmlNode.get('name')
        self.id = xmlNode.get('id')
        self.version = xmlNode.get('version')
        self.description = xmlNode.get('caption')
        self.registerGroups = []
        self.valueGroups = []
        self.interruptGroups = []
        self.parameters = None

        for group in xmlNode.getchildren():
            if group.tag == 'register-group':
                self.registerGroups.append( RegisterGroup(group) )
            elif group.tag == 'value-group':
                self.valueGroups.append( ValueGroup(group) )
            elif group.tag == 'interrupt-group':
                self.interruptGroups.append( InterruptGroup(group) )
            elif group.tag == 'parameters':
                self.parameters = { c.get('name') : c.get('value') for c in group.getchildren() }
            else:
                LOGGER.error(f"Unknown Module group {group.tag}!")

    def __repr__(self):
        return f'{self.version}-{self.name}'
