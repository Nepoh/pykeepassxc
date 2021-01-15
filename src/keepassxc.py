import command
from entity import IDatabase, Database


def get_version() -> str:
    """
    Shows the KeePassXC version.
    :return: The version string.
    """
    return command.Command(options=['--version']).execute()


def generate_password(config: command.GeneratePasswordConfig = None) -> str:
    """
    Generate a new random password.
    :param config: Password generation options
    :return:
    """
    return command.GeneratePasswordCommand(config).execute()


def generate_diceware(words: int = None) -> str:
    """
    Generate a new random diceware passphrase.
    :param words: Word count
    :return:
    """
    return command.GenerateDicewareCommand(words).execute()


def estimate_password(password: str) -> dict:
    """
    Estimate the strength of a password.

    >>> estimate_password('1234')
    {'length': 4, 'entropy': 2.0, 'log10': 0.602}

    :param password: The password to estimate
    :return:
    """
    return command.EstimatePasswordCommand(password).execute()


def create_database(path: str, password: str = None, key_file: str = None, yubikey_slot: str = None,
                    decryption_time: int = None) -> IDatabase:
    """
    A wrapper around :py:meth:`~entity.Database.create`.

    :return: The newly created database
    :raise IOError: If the database file already exists and `decryption_time` has been specified.
    """
    database = Database(path, password, key_file, yubikey_slot)
    if not database.exists():
        database.create(decryption_time)
    elif decryption_time is not None:
        raise IOError('Decryption time cannot be assured for existing database at "{}"'.format(path))
    return database
