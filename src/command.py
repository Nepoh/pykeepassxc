import logging
import os
import re
import shlex
import subprocess
from typing import List, Tuple, Optional, Set
import pexpect
from interface import ICommand, IDatabase


class GeneratePasswordConfig:
    def __init__(self, length: int = None, lowercase: bool = True, uppercase: bool = True,
                 numbers: bool = True, special: bool = False, extended: bool = False,
                 exclude_chars: List[chr] = None, exclude_similar: bool = False):
        """
        Generate a new random password.
        :param length: Length of the generated password
        :param lowercase: Use lowercase characters
        :param uppercase: Use uppercase characters
        :param numbers: Use numbers
        :param special: Use special characters
        :param extended: Use extended ASCII
        :param exclude_chars: Exclude character set
        :param exclude_similar: Exclude similar looking characters
        :return:
        """
        self.length = length
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.numbers = numbers
        self.special = special
        self.extended = extended
        self.exclude_chars = exclude_chars
        self.exclude_similar = exclude_similar

    def get_command_options(self) -> List[str]:
        options = []
        if self.length is not None:
            if not isinstance(self.length, int) or self.length < 1:
                raise ValueError('Invalid password length.')
            options.append('--length')
            options.append('{:d}'.format(self.length))

        if self.exclude_chars is not None:
            options.append('--exclude')
            options.append(''.join(self.exclude_chars))

        if self.lowercase:
            options.append('--lower')
        if self.uppercase:
            options.append('--upper')
        if self.numbers:
            options.append('--numeric')
        if self.special:
            options.append('--special')
        if self.extended:
            options.append('--extended')
        if self.exclude_similar:
            options.append('--exclude-similar')

        # --every-group  Include characters from every selected group

        return options


class Command(ICommand):
    def __init__(self, command: str = None, options: List[str] = None, args: List[str] = None):
        self._command = command
        self._options = options if options is not None else []
        self._args = args if args is not None else []
        self._encoding = 'utf-8'
        self._env = {'LC_ALL': 'en_US.UTF-8'}
        self.stdout = None
        self.stderr = None
        self.return_code = None

    def execute(self, check: bool = True) -> str:
        """
        Executes the command and returns content of STDOUT if the command's return code is zero.
        Populates `self.stdout`, `self.stderr` and `self.return_code`.

        :param check: Check the return code of the subprocess.
        :raise CalledProcessError: If the return code is checked and is non-zero.
        :return: Content of STDOUT (without leading/trailing line breaks) or empty string on non-zero return code.
        """
        command = self._build_command()
        logging.debug('Executing command `{}`'.format(' '.join(command)))

        self.return_code, self.stdout, self.stderr = self._run_subprocess(command)

        if len(self.stderr) > 0:
            logging.error(self.stderr)

        if self.return_code == 0:
            return self.stdout.strip("\r\n")
        else:
            logging.error('KeepPssXC returned non-zero exit status {}'.format(self.return_code))
            if check:
                raise subprocess.CalledProcessError(self.return_code, command, self.stdout, self.stderr)

    def _build_command(self) -> List[str]:
        executable = os.getenv('KEEPASSXC_CLI_EXE', 'keepassxc-cli')
        parts = [executable]

        if self._command is not None:
            parts.append(self._command)

        parts += self._options

        if len(self._args) > 0:
            parts.append('--')
            parts += self._args

        return [self.quote(part) for part in parts]

    def _run_subprocess(self, command: List[str]) -> Tuple[int, str, str]:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=self._encoding,
            env=self._env
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    @staticmethod
    def quote(string: str) -> str:
        return shlex.quote(string)


class GeneratePasswordCommand(Command):
    def __init__(self, config: GeneratePasswordConfig = None):
        options = None if config is None else config.get_command_options()
        super().__init__('generate', options=options)


class GenerateDicewareCommand(Command):
    def __init__(self, words: int = None):
        if words is None:
            options = None
        else:
            if not isinstance(words, int) or words < 1:
                raise ValueError('Invalid word count.')
            options = ['--words', '{:d}'.format(words)]

        super().__init__('diceware', options)


class EstimatePasswordCommand(Command):
    def __init__(self, password: str):
        super().__init__('estimate', args=[password])

    def execute(self, check: bool = True) -> dict:
        output = super().execute(check)
        line = output.splitlines()[0]
        pattern = re.compile('^(Length [0-9]+)\\s+(Entropy [0-9.]+)\\s+(Log10 [0-9.]+)$')
        match = re.match(pattern, line)
        if match is None:
            raise Exception('{} does not match {}'.format(line, pattern))
        else:
            return {k.lower(): self.convert(v) for (k, v) in [group.split(' ') for group in match.groups()]}

    @staticmethod
    def convert(string):
        try:
            return int(string)
        except ValueError:
            return float(string)


class DatabaseCommand(Command):
    def __init__(self, database: IDatabase, command: str, options: List[str] = None, args: List[str] = None, pre_args: List[str] = None):
        self._database = database

        full_args = []
        if pre_args is not None:
            full_args += pre_args

        full_args.append(self._database.get_path())

        if args is not None:
            full_args += args

        if options is None:
            options = []

        if not self._database.has_password():
            options.append('--no-password')

        if self._database.has_key_file():
            options.append('--key-file')
            options.append(self._database.get_key_file())

        super().__init__(command, options, full_args)

    def _run_subprocess(self, command: List[str]) -> Tuple[int, str, str]:

        child = pexpect.spawn(' '.join(command), env=self._env, encoding=self._encoding)
        child.delaybeforesend = 0.05  # use 50 ms delay between expect and send
        stdout = self._run_expect(child)
        stderr = ''
        child.wait()

        # Note that lines are terminated by CR/LF (rn) combination even on UNIX-like systems
        # because this is the standard for pseudottys.
        stdout = '' if stdout is None else stdout.replace("\r\n", os.linesep)

        # If the child exited normally then exitstatus will store the exit return code and signalstatus will be None.
        # If the child was terminated abnormally with a signal then signalstatus will store the signal value and exitstatus will be None:
        return_code = child.exitstatus if child.signalstatus is None else child.signalstatus

        if not return_code == 0:
            stderr = stdout
            stdout = ''

        return return_code, stdout.strip(), stderr.strip()

    def _run_expect(self, child: pexpect.spawn) -> Optional[str]:
        if self._database.has_password():
            child.expect('Enter password to unlock {}: '.format(self._database.get_path()))
            child.sendline(self._database.get_password())
        child.expect(pexpect.EOF)
        return child.before


class DatabaseInfoCommand(DatabaseCommand):
    def __init__(self, database: IDatabase):
        super().__init__(database, 'db-info')

    def execute(self, check: bool = True) -> dict:
        output = super().execute()
        assert len(output) > 0
        return self._parse_output(output)

    @staticmethod
    def _parse_output(output: str) -> dict:
        """
        UUID: {deaedbd6-2d29-49f4-9357-3d16ca00e716}
        Name: Passwörter
        Description:
        Cipher: AES 256-bit
        KDF: Argon2 (20 rounds, 65536 KB)
        Recycle bin is enabled.
        """
        info = {}
        pattern = re.compile('^([A-Za-z]+):\s+(.*)$')
        for line in output.splitlines():
            m = pattern.match(line)
            if m:
                k, v = m.groups()
                info[k.lower()] = v
        return info


class AnalyzeDatabaseCommand(DatabaseCommand):
    def __init__(self, database: IDatabase, hibp_path: str = None):
        if hibp_path is None:
            options = None
        else:
            options = ['--hibp', hibp_path]

        super().__init__(database, 'analyze', options=options)


class ExportDatabaseCommand(DatabaseCommand):
    def __init__(self, database: IDatabase, format: str = None):
        if format is None:
            options = None
        else:
            assert format in ['xml', 'csv']
            options = ['--format', format]

        # in earlier versions "export" was called "extract"
        super().__init__(database, 'export', options=options)


class CompareDatabaseCommand(DatabaseCommand):
    def __init__(self, database: IDatabase, database_from: IDatabase):
        self._database_from = database_from

        args = []
        args.append(self._database_from.get_path())

        options = ['--dry-run']
        if not self._database_from.has_password():
            options.append('--no-password-from')
        if self._database_from.has_key_file():
            options.append('--key-file-from')
            options.append(self._database_from.get_key_file())

        super().__init__(database, 'merge', options=options, args=args)

    def execute(self, check: bool = True) -> Set[str]:
        output = super().execute(check)
        return {l.strip() for l in output.splitlines(keepends=False)}

    def _run_expect(self, child: pexpect.spawn) -> Optional[str]:
        if self._database.has_password():
            child.expect('Enter password to unlock {}: '.format(self._database.get_path()))
            child.sendline(self._database.get_password())
        if self._database_from.has_password():
            child.expect('Enter password to unlock {}: '.format(self._database_from.get_path()))
            child.sendline(self._database_from.get_password())
        child.expect('Database was not modified by merge operation.')
        return child.before
