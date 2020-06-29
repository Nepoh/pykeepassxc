from pykeepassxc import command


def get_version() -> str:
    """
    Shows the keepassxc version.
    :return: The version string.
    """
    return command.Command(['--version']).run()


def generate(length: int = None, lowercase: bool = True, uppercase: bool = True, numbers: bool = True,
             special: bool = False, extended: bool = False) -> str:
    """
    Generate a new random password.
    :param length: Password length
    :param lowercase:
    :param uppercase:
    :param numbers:
    :param special:
    :param extended:
    :return:
    """
    args = ['generate']

    if length is not None:
        if not isinstance(length, int) or length < 1:
            raise ValueError('Invalid password length.')
        args.append('--length')
        args.append('{}'.format(length))
    if lowercase:
        args.append('-l')
    if uppercase:
        args.append('-U')
    if numbers:
        args.append('-n')
    if special:
        args.append('-s')
    if extended:
        args.append('-e')

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
