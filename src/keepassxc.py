from typing import List
from pykeepassxc import command


class GeneratePassword:
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

    def get_options(self) -> List[str]:
        options = []
        if self.length is not None:
            if not isinstance(self.length, int) or self.length < 1:
                raise ValueError('Invalid password length.')
            options.append('--length')
            options.append('{:d}'.format(self.length))

        if self.exclude_chars is not None:
            options.append('--exclude')
            options.append('"{}"'.format(''.join(self.exclude_chars)))

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


def get_version() -> str:
    """
    Shows the keepassxc version.
    :return: The version string.
    """
    return command.Command(['--version']).run()


def generate(password: GeneratePassword) -> str:
    """
    Generate a new random password.

    :return:
    """
    args = ['generate'] + password.get_options()
    return command.Command(args).run()


def generate_diceware(words: int = None) -> str:
    """
    Generate a new random diceware passphrase.
    :param words: Word count
    :return:
    """
    args = ['diceware']

    if words is not None:
        if not isinstance(words, int) or words < 1:
            raise ValueError('Invalid word count.')
        args.append('--words')
        args.append('{}'.format(words))

    return command.Command(args).run()
