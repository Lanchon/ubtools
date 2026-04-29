# ubtools

### Tiny little tools to interact with U-Boot via the serial console

Also included is a simple yet robust Python 3.11 library to talk to U-Boot.

### Usage

To install the tools:
```
pipx install ubtools
```

To run without installing:
```
cd src
python -m ubtools.cli.COMMAND ...
```

To build and test:
```
./build
./run-tests
pipx install -e .
```

### Configuration

Defaults are loaded from the `serial` section of `~/.config/ubtools/config.toml`, if present:
```toml
[serial]
port = "/dev/ttyUSB0"
baud = 115200
timeout = 0.1
mode = "exclusive"
```

Environment variables of the form `UBTOOLS_*` (`UBTOOLS_PORT`, etc.) can override those values.

### Commands

| Command | Description |
|---|---|
| **[ubint](#ubint)** | Interrupt U-Boot autoboot via the serial console |
| **[ubcmd](#ubcmd)** | Send a command to U-Boot via the serial console and print the output |
| **[ubread](#ubread)** | Read from U-Boot memory via the serial console |
| **[ubwrite](#ubwrite)** | Write to U-Boot memory via the serial console |

### ubint

Interrupt U-Boot autoboot via the serial console

```
usage: ubint [-s STR] [-p PORT] [-b BAUD] [--timeout SECONDS]
             [--mode {shared,exclusive,none}] [-h] [--version]

Interrupt U-Boot autoboot via the serial console

options:
  -s STR, --string STR  interrupt using custom string
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  serial port baud rate
  --timeout SECONDS     serial port receive timeout
  --mode {shared,exclusive,none}
                        serial port locking mode
  -h, --help            show help message and exit
  --version             show version number and exit
```

### ubcmd

Send a command to U-Boot via the serial console and print the output

```
usage: ubcmd [-n | -q] [-p PORT] [-b BAUD] [--timeout SECONDS]
             [--mode {shared,exclusive,none}] [-h] [--version]
             COMMAND ...

Send a command to U-Boot via the serial console and print the output

positional arguments:
  COMMAND               command to send
  ARGS                  arguments

options:
  -n, --no-reply        do not retrieve output nor exit code
  -q, --quiet           do not show non-zero exit code
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  serial port baud rate
  --timeout SECONDS     serial port receive timeout
  --mode {shared,exclusive,none}
                        serial port locking mode
  -h, --help            show help message and exit
  --version             show version number and exit
```

### ubread

Read from U-Boot memory via the serial console

```
usage: ubread [-q] [-w BITS] [-p PORT] [-b BAUD] [--timeout SECONDS]
              [--mode {shared,exclusive,none}] [-h] [--version]
              FILE ADDRESS LENGTH

Read from U-Boot memory via the serial console

positional arguments:
  FILE                  Output file (use '-' for stdout)
  ADDRESS               memory address (decimal or hex)
  LENGTH                number of bytes (decimal or hex)

options:
  -q, --quiet           do not show progress
  -w BITS, --word BITS  use reads of specified bit width
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  serial port baud rate
  --timeout SECONDS     serial port receive timeout
  --mode {shared,exclusive,none}
                        serial port locking mode
  -h, --help            show help message and exit
  --version             show version number and exit
```

### ubwrite

Write to U-Boot memory via the serial console

```
usage: ubwrite [-q] [-w BITS] [-p PORT] [-b BAUD] [--timeout SECONDS]
               [--mode {shared,exclusive,none}] [-h] [--version]
               FILE ADDRESS

Write to U-Boot memory via the serial console

positional arguments:
  FILE                  input file (use '-' for stdin)
  ADDRESS               memory address (decimal or hex)

options:
  -q, --quiet           do not show progress
  -w BITS, --word BITS  use writes of specified bit width
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  serial port baud rate
  --timeout SECONDS     serial port receive timeout
  --mode {shared,exclusive,none}
                        serial port locking mode
  -h, --help            show help message and exit
  --version             show version number and exit
```

