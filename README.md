# ubtools

### Tiny little tools to interact with U-Boot via the serial console

Also included is a simple yet robust Python 3.11 library to talk to U-Boot.

| Command | Description |
|---|---|
| **[ubint](#ubint)** | Interrupt U-Boot autoboot via the serial console |
| **[ubcmd](#ubcmd)** | Send a command to U-Boot via the serial console and print the output |
| **[ubread](#ubread)** | Read from U-Boot memory via the serial console |
| **[ubwrite](#ubwrite)** | Write to U-Boot memory via the serial console |

### ubint

Interrupt U-Boot autoboot via the serial console

```
usage: ubint [-h] [-s XXX] [-p PORT] [-b BAUD] [--timeout SECONDS] [--shared]

Interrupt U-Boot autoboot via the serial console

options:
  -h, --help            show this help message and exit
  -s XXX, --string XXX  interrupt using custom string
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  baud rate
  --timeout SECONDS     timeout for read operations
  --shared              open serial port in shared mode
```

### ubcmd

Send a command to U-Boot via the serial console and print the output

```
usage: ubcmd [-h] [-q] [-p PORT] [-b BAUD] [--timeout SECONDS] [--shared]
             COMMAND ...

Send a command to U-Boot via the serial console and print the output

positional arguments:
  COMMAND               command to send
  ARGS                  arguments

options:
  -h, --help            show this help message and exit
  -q, --quiet           do not show exit code
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  baud rate
  --timeout SECONDS     timeout for read operations
  --shared              open serial port in shared mode
```

### ubread

Read from U-Boot memory via the serial console

```
usage: ubread [-h] [-q] [-w BITS] [-p PORT] [-b BAUD] [--timeout SECONDS]
              [--shared]
              FILE ADDRESS LENGTH

Read from U-Boot memory via the serial console

positional arguments:
  FILE                  Output file (use '-' for stdout)
  ADDRESS               memory address (decimal or hex)
  LENGTH                number of bytes (decimal or hex)

options:
  -h, --help            show this help message and exit
  -q, --quiet           do not show progress
  -w BITS, --word BITS  use reads of specified bit width
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  baud rate
  --timeout SECONDS     timeout for read operations
  --shared              open serial port in shared mode
```

### ubwrite

Write to U-Boot memory via the serial console

```
usage: ubwrite [-h] [-q] [-w BITS] [-p PORT] [-b BAUD] [--timeout SECONDS]
               [--shared]
               FILE ADDRESS

Write to U-Boot memory via the serial console

positional arguments:
  FILE                  input file (use '-' for stdin)
  ADDRESS               memory address (decimal or hex)

options:
  -h, --help            show this help message and exit
  -q, --quiet           do not show progress
  -w BITS, --word BITS  use writes of specified bit width
  -p PORT, --port PORT  serial port device
  -b BAUD, --baud BAUD  baud rate
  --timeout SECONDS     timeout for read operations
  --shared              open serial port in shared mode
```

