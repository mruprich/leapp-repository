from collections import namedtuple

import pytest

from leapp.exceptions import StopActorExecutionError
from leapp.libraries.actor import library
from leapp.libraries.common.config import architecture
from leapp.libraries.stdlib import api
from leapp.models import BootContent


class run_mocked(object):
    def __init__(self):
        self.args = []

    def __call__(self, args, split=False):
        self.args.append(args)


class write_to_file_mocked(object):
    def __init__(self):
        self.content = None

    def __call__(self, filename, content):
        self.content = content


class CurrentActorMocked(object):
    def __init__(self, arch):
        self.configuration = namedtuple('configuration', ['architecture'])(arch)

    def __call__(self):
        return self


def test_add_boot_entry_non_s390x(monkeypatch):
    def get_boot_file_paths_mocked():
        return '/abc', '/def'
    monkeypatch.setattr(library, 'get_boot_file_paths', get_boot_file_paths_mocked)
    monkeypatch.setenv('LEAPP_DEBUG', '1')
    monkeypatch.setattr(library, 'run', run_mocked())
    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(architecture.ARCH_X86_64))

    library.add_boot_entry()

    assert len(library.run.args) == 2
    assert library.run.args[0] == ['/usr/sbin/grubby',
                                   '--remove-kernel', '/abc']
    assert library.run.args[1] == ['/usr/sbin/grubby',
                                   '--add-kernel', '/abc',
                                   '--initrd', '/def',
                                   '--title', 'RHEL-Upgrade-Initramfs',
                                   '--copy-default',
                                   '--make-default',
                                   '--args',
                                   'debug enforcing=0 rd.plymouth=0 plymouth.enable=0']


def test_add_boot_entry_s390x(monkeypatch):
    def get_boot_file_paths_mocked():
        return '/abc', '/def'
    monkeypatch.setattr(library, 'get_boot_file_paths', get_boot_file_paths_mocked)
    monkeypatch.setenv('LEAPP_DEBUG', '1')
    monkeypatch.setattr(library, 'run', run_mocked())
    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(architecture.ARCH_S390X))

    library.add_boot_entry()

    assert len(library.run.args) == 3
    assert library.run.args[0] == ['/usr/sbin/grubby',
                                   '--remove-kernel', '/abc']
    assert library.run.args[1] == ['/usr/sbin/grubby',
                                   '--add-kernel', '/abc',
                                   '--initrd', '/def',
                                   '--title', 'RHEL-Upgrade-Initramfs',
                                   '--copy-default',
                                   '--make-default',
                                   '--args',
                                   'debug enforcing=0 rd.plymouth=0 plymouth.enable=0']
    assert library.run.args[2] == ['/usr/sbin/zipl']


def test_get_boot_file_paths(monkeypatch):
    # BootContent message available
    def consume_message_mocked(*models):
        yield BootContent(kernel_path='/ghi', initram_path='/jkl')
    monkeypatch.setattr('leapp.libraries.stdlib.api.consume', consume_message_mocked)

    kernel_path, initram_path = library.get_boot_file_paths()

    assert kernel_path == '/ghi' and initram_path == '/jkl'

    # No BootContent message available
    def consume_no_message_mocked(*models):
        yield None
    monkeypatch.setattr('leapp.libraries.stdlib.api.consume', consume_no_message_mocked)

    with pytest.raises(StopActorExecutionError):
        library.get_boot_file_paths()


def test_fix_grub_config_error(monkeypatch):
    monkeypatch.setattr(library, 'write_to_file', write_to_file_mocked())
    library.fix_grub_config_error('files/grub_test.wrong')

    with open('files/grub_test.fixed') as f:
        assert library.write_to_file.content == f.read()
