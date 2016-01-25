# python
# This file is generated by a program (mib2py). Any edits will be lost.

from pycopia.aid import Enum
import pycopia.SMI.Basetypes
Range = pycopia.SMI.Basetypes.Range
Ranges = pycopia.SMI.Basetypes.Ranges

from pycopia.SMI.Objects import ColumnObject, MacroObject, NotificationObject, RowObject, ScalarObject, NodeObject, ModuleObject, GroupObject

# imports 
from SNMPv2_SMI import ObjectName, NotificationName, ObjectSyntax

class SNMPv2_CONF(ModuleObject):
	path = '/usr/share/mibs/ietf/SNMPv2-CONF'
	conformance = 2
	name = 'SNMPv2-CONF'
	language = 2

# nodes

# macros
class OBJECT_GROUP(MacroObject):
	name = 'OBJECT-GROUP'


class NOTIFICATION_GROUP(MacroObject):
	name = 'NOTIFICATION-GROUP'


class MODULE_COMPLIANCE(MacroObject):
	name = 'MODULE-COMPLIANCE'


class AGENT_CAPABILITIES(MacroObject):
	name = 'AGENT-CAPABILITIES'


# types 
# scalars 
# columns
# rows 
# notifications (traps) 
# groups 
# capabilities 

# special additions

# Add to master OIDMAP.
from pycopia import SMI
SMI.update_oidmap(__name__)