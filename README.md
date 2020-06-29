# PyKeePassXC
A Python wrapper around the `keepassxc-cli` command.

## Usage
```python
import pykeepassxc

pykeepassxc.get_version()  # "2.5.4"
pykeepassxc.generate()  # "kMGLs2p7bt9dQ6uZ"

db = pykeepassxc.Database('/home/nepoh/secret.kdbx',
                          password='supersecretpassw0rd',
                          key_file='/mnt/usb-drive/keepass.key')

db.export_to('/home/nepoh/test.kdbx.xml', format='xml')
```

## Requirements
`KeePassXc >= 2.5.4`
(The command line interface changed somwhere between `2.3` and `2.5.4`,
so older versions may be supported as well)

## TODO
- Implement more commands
- Write some tests?
