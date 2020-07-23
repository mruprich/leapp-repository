from leapp import reporting
from leapp.actors import Actor
from leapp.models import QuaggaToFrrFacts, Report
from leapp.reporting import create_report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

COMMON_REPORT_TAGS = [
    reporting.Tags.NETWORK,
    reporting.Tags.SERVICES
]


class QuaggaReport(Actor):
    """
    Checking for babeld on RHEL-7.

    This actor is supposed to report that babeld was used on RHEL-7
    and it is no longer available in RHEL-8.
    """

    name = 'quagga_report'
    consumes = (QuaggaToFrrFacts, )
    produces = (Report, )
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    def process(self):
        quagga_facts = next(self.consume(QuaggaToFrrFacts))
        if quagga_facts:
            if 'babeld' in quagga_facts.active_daemons or 'babeld' in quagga_facts.enabled_daemons:
                create_report([
                    reporting.Title('Babeld is not available in FRR'),
                    reporting.Summary(
                        'babeld daemon which was a part of quagga implementation in RHEL7 '
                        'is not available in RHEL8 in FRR due to licensing issues.'
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags(COMMON_REPORT_TAGS),
                    reporting.Flags([reporting.Flags.INHIBITOR]),
                    reporting.Remediation(hint='Please use RIP, OSPF or EIGRP instead of Babel')
                ])
        else:
            self.log.debug('babeld not used, moving on.')
