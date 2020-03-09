from leapp.models import Model, fields
from leapp.topics import SystemInfoTopic


class QuaggaToFrrFacts(Model):
    '''
    A list of configuration files used by quagga. This list is used to add yes/no to 
    /etc/frr/daemons file. It indicates which daemons from frr should be run.
    '''
    topic = SystemInfoTopic

    active_daemons = fields.List(fields.String())
    enabled_daemons = fields.List(fields.String())
