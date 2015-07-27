# FAIDDS

**Forensic Acquisition Information and Drive Data Script**

This script provides a simple way to gather drive information and acquire a drive from a specified device file to the
local directory. For this script to work you must run it as Administrator.

Use the -d argument to specify the device or file path. Using -lh you can get the list of hashes available.
These two options are mutually exclusive.

You can get sample reports in the *Sample* directory.

### Usage

**See all the available options**

    python faids.py --help

    usage: faidds.py [-h] [-d DRIVE] [-D] [-c CHUNK] [-s SERIAL] [-m HASHES] [-lh]
                 [-dcfldd]

    Forensic Acquisition Information and Drive Data Script. This script provides a
    simple way to gather drive information and acquire a drive from a specified
    device file to the local directory. For this script to work you must run it as
    Administrator. Use the -d argument to specify the device or file path. Using
    -lh you can get the list of hashes available. These two options are mutually
    exclusive.

    optional arguments:
      -h, --help            show this help message and exit
      -d DRIVE, --drive DRIVE
                            Device file to acquire. Example: /dev/sda
      -D, --DEBUG           Debug mode will be activated. All the system calls are
                            printed
      -c CHUNK, --chunk CHUNK
                            Size to split file in GB (1024*1024*1024)
      -s SERIAL, --serial SERIAL
                            User specified serial number. Default is to find
                            serial number in drive info.
      -m HASHES, --hashes HASHES
                            List of hash algorithms to use. Comma separated with
                            no spaces. (default: md5)
      -lh, --list_hashes    List all the Hashes
      -dcfldd, --dcfldd     Use dcfldd to acquire image. (default: dc3dd)

#### Example Usage

**Acquire a drive image and gather information**

    python faids.py -d /dev/sdb1

**Acquire a drive image and get multiple hash results**

Write the hashes as Comma separated value.

    python faids.py -d /dev/sdb1 -m md5,sha256,sha512

**Get list of all available hashes**

    python faids.py -lh

*Available hashes*: md5, sha1, sha256, sha384 and sha512

### Note

This script was adopted from [here](https://github.com/cutaway/faidds). I have refactored it and made it more readable
with a better documentation and I plan to add some more new features later.
