# PyKeePassXC
A Python wrapper around the `keepassxc-cli` command.

## Usage
```python
import pykeepassxc

# get the installed version of KeePassXc
pykeepassxc.get_version()        # "2.5.4"

# generate a password and diceware
pykeepassxc.generate_password()  # "kMGLs2p7bt9dQ6uZ"
pykeepassxc.generate_diceware()  # "amnesty mobilize broken excuse elixir jackpot cannot"

# create a new database and add an entry
db = pykeepassxc.create_database(
    '/home/nepoh/secret.kdbx',
    password='supersecretpassw0rd',
    key_file='/mnt/usb-drive/keepass.key'
)
grp = db.create_entry(path='websites', password='monday123', username='garfield', url='wikipedia.org')

# export the database to XML
db.export_to('/home/nepoh/test.kdbx.xml', format='xml')
```

## Requirements
`KeePassXc >= 2.5.4`
(The command line interface changed somwhere between `2.3` and `2.5.4`,
so older versions may be supported as well)

## Development
```shell
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## TODO
- Implement more commands

## See
- https://keepassxc.org/
- https://www.mankier.com/1/keepassxc-cli
