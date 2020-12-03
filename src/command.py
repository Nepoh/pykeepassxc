import os
import subprocess
from typing import List
import pexpect
from pykeepassxc.database import Database


class Command:
    def __init__(self, args: List[str]):
        self._args = ['keepassxc-cli'] + args
        self._encoding = 'utf-8'
        self._env = {'LANGUAGE': 'en_US'}
        self.stdout = None
        self.stderr = None
        self.return_code = None

    def run(self, check: bool = True) -> str:
        """
        Executes the command and returns content of STDOUT if the command's return code is zero.
        Populates `self.stdout`, `self.stderr` and `self.return_code`.

        :param check: Check the return code of the subprocess.
        :raise CalledProcessError: If the return code is checked and is non-zero.
        :return: Content of STDOUT (without leading/trailing line breaks) or empty string on non-zero return code.
        """
        p = subprocess.Popen(self._args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=self._encoding, env=self._env)
        self.stdout, self.stderr = p.communicate()
        self.return_code = p.returncode

        if self.return_code == 0:
            return self.stdout.strip("\r\n")
        elif check:
            raise subprocess.CalledProcessError(self.return_code, self._args, self.stdout, self.stderr)


class DatabaseCommand(Command):
    def __init__(self, database: Database, args: List[str]):
        super().__init__(args)
        self._database = database

    def run(self, check: bool = True) -> str:
        args = self._args.copy()

        if self._database.has_key_file():
            args.append('--key-file')
            args.append('"{}"'.format(self._database.get_key_file()))
        if self._database.has_yubikey_slot():
            args.append('--yubikey')
            args.append('"{}"'.format(self._database.get_yubikey_slot()))

        args.append('--')
        args.append('"{}"'.format(self._database.get_path()))

        child = pexpect.spawn(' '.join(args), env=self._env, encoding=self._encoding)
        child.delaybeforesend = 0.05  # use 50 ms delay between expect and send
        child.expect('Enter password to unlock .*: ')
        child.sendline(self._database.get_password())
        child.expect(pexpect.EOF)

        # Note that lines are terminated by CR/LF (rn) combination even on UNIX-like systems
        # because this is the standard for pseudottys.
        self.stdout = child.before.replace("\r\n", os.linesep)
        self.stderr = ''
        child.close()

        # If the child exited normally then exitstatus will store the exit return code and signalstatus will be None.
        # If the child was terminated abnormally with a signal then signalstatus will store the signal value and exitstatus will be None:
        self.return_code = child.exitstatus if child.signalstatus is None else child.signalstatus

        if self.return_code == 0:
            return self.stdout.strip("\r\n")
        else:
            self.stderr = self.stdout
            self.stdout = ''
            if check:
                raise subprocess.CalledProcessError(self.return_code, ' '.join(self._args), self.stdout, self.stderr)
