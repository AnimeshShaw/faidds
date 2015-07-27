#!/usr/bin/env python3

import sys
import argparse
import subprocess
import time
import re


class Faidds():
    def __init__(self, debug=False, drive_path="", serial_num="", size="", def_hash="md5", dc3=True):
        """
        Initialize the default variables used throughout the Script.
        """

        self.debug = debug
        self.ftformat = "%B %d %Y %H:%M:%S"
        self.timezone = "%Z"
        self.drive_path = drive_path
        self.serial_num = serial_num
        self.size = size
        self.def_hash = def_hash
        self.dc3 = dc3

        # Set drive to acquire
        self.serial = "Serial Number"
        self.sn = re.compile(self.serial)

        # Command locations
        self.sdparm = "/usr/bin/sdparm"
        self.hdparm = "/sbin/hdparm"
        self.parted = "/sbin/parted"
        self.dcfldd = "/usr/bin/dcfldd"
        self.dc3dd = "/usr/bin/dc3dd"

    @staticmethod
    def get_time(tformat="%Y%m%d%H%M%S"):
        """
        Times are returned as UTC.

        :param tformat: Return time as a particular format.
        Default format: %Y%m%d%H%M%S
        """
        return time.strftime(tformat, time.gmtime())

    def start_process(self):
        """
        Start the main process drive information gathering.

        :rtype : None
        """

        if self.debug:
            print("Debug Enabled. All System calls will be printed.")

        #############################
        # Capture drive information #
        #############################

        # Parted Options
        parted_options = "print"
        parted_cmd = [self.parted, self.drive_path, parted_options]

        # sdparm Options
        sdparm_options = "--inquiry"
        sdparm_cmd = [self.sdparm, sdparm_options, self.drive_path]

        # hdparm Options
        hdparm_options = "-I"
        hdparm_cmd = [self.hdparm, hdparm_options, self.drive_path]

        data_cmds = [parted_cmd, hdparm_cmd, sdparm_cmd]
        info = []

        # Get drive data
        for cmd in data_cmds:
            if self.debug:
                print("System Call - " + " ".join(cmd))

            info.append("System Call - " + " ".join(cmd))
            p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            info.append(p.communicate()[0])

        # Search for Serial Number and grab.
        if not self.serial_num:
            for e in info:
                if self.serial_num:
                    break
                if self.sn.search(e):
                    for l in e.split("\n"):
                        if self.sn.search(l):
                            if self.debug:
                                print("Serial Number: " + l.split(':')[1].strip())
                            self.serial_num = l.split(':')[1].strip()
                            break

        if not self.serial_num:
            self.serial_num = 'serial_unknown'

        ####################################################
        # Acquire drive                                    #
        # dcfldd: http://www.forensicswiki.org/wiki/Dcfldd #
        ####################################################

        ctime = self.get_time()
        infile = 'if=' + self.drive_path
        outfile = 'of=./' + self.serial_num + '_' + ctime + '.dd'

        if self.dc3:
            hash_file = 'log=./' + self.serial_num + '_' + ctime + '_hash.txt'
            err = 'rec=on'
            dd = self.dc3dd

            # dc3dd hashes are provided one at a time
            if self.def_hash != 'md5':
                thash = []
                for e in self.def_hash.split(','):
                    thash.append('hash=' + e)
            else:
                thash = ['hash=' + self.def_hash]

            cmd = [dd, hash_file, err, infile]
            cmd.extend(thash)

            if self.size:
                outfile = 'ofs=./' + self.serial_num + '_' + ctime + '.dd.0000'
                cmd.append('ofsz=' + self.size + 'G')
            cmd.append(outfile)
        else:
            # dcfldd hashes are provided as a comma separated list
            thash = 'hash=' + self.def_hash
            hash_file = 'hashlog=./' + self.serial_num + '_' + ctime + '_hash.txt'
            err = 'conv=noerror,sync'
            dd = self.dcfldd
            cmd = [dd, thash, hash_file, err, infile]
            if self.size:
                cmd.extend(['split=' + self.size + 'G', 'splitformat=0000'])
            # Split and split format MUST come before the filename
            cmd.append(outfile)

        print('System Time Zone Is: ' + time.tzname[time.daylight])
        info.append('System Time Zone Is:' + time.tzname[time.daylight] + '\n')

        print('Start Time:' + self.get_time(self.ftformat) + ' UTC')
        info.append('Start Time: ' + self.get_time(self.ftformat) + ' UTC')

        print('Acquisition command:' + ' '.join(cmd))
        info.append('Acquisition command: ' + ' '.join(cmd))

        # Run dcfldd - do not use stderr and stdout to prevent blocking due to
        # large stderr output
        subprocess.Popen(cmd).wait()

        print('Stop Time: ' + self.get_time(self.ftformat) + ' UTC')
        info.append('Stop Time: ' + self.get_time(self.ftformat) + ' UTC')

        # Output file
        onf = 'drive_data_' + self.drive_path.replace("/", "_") + '_' + self.serial_num + '_' + self.get_time() + '.txt'

        with open(onf, 'w') as f:
            for e in info:
                f.write(e + '\n')


def acquire_conf():
    """
    Get user permission to acquire drive image.

    :rtype : bool
    :return: Permission to acquire drive image.
    """
    if sys.hexversion > 0x30000000:
        return input("Enter YES/Y to acquire drive image: ").lower() == "y" or "yes"
    else:
        return raw_input("Enter YES/Y to acquire drive image: ").lower() == "y" or "yes"


def main():
    desc = """
        Forensic Acquisition Information and Drive Data Script.
        This script provides a simple way to gather drive information
        and acquire a drive from a specified device file to the
        local directory.

        For this script to work you must run it as Administrator.

        Use the -d argument to specify the device or file path. Using -lh
        you can get the list of hashes available. These two options are mutually
        exclusive.
    """

    parser = argparse.ArgumentParser(description=desc, prog="faidds.py")
    parser.add_argument('-d', '--drive', type=str, help="Device file to acquire. Example: /dev/sda")
    parser.add_argument('-D', '--DEBUG', action='store_true', help="Debug mode will be activated. All the "
                                                                   "system calls are printed")
    parser.add_argument('-c', '--chunk', type=str, help="Size to split file in GB (1024*1024*1024)")
    parser.add_argument('-s', '--serial', type=str, help="User specified serial number. Default is to "
                                                         "find serial number in drive info.")
    parser.add_argument('-m', '--hashes', type=str, help="List of hash algorithms to use. Comma separated "
                                                         "with no spaces. (default: md5)")
    parser.add_argument('-lh', '--list_hashes', action="store_true", help="List all the Hashes")
    parser.add_argument('-dcfldd', '--dcfldd', action="store_true", help="Use dcfldd to acquire image. (default: dc3dd)")

    args = parser.parse_args()

    hash_list = ["md5", "sha1", "sha256", "sha384", "sha512"]

    if args.drive:
        if acquire_conf():
            Faidds(drive_path=args.drive, debug=args.DEBUG, serial_num=args.serial, size=args.chunk,
                  def_hash=args.hashes, dc3=args.dcfldd).start_process()
        else:
            print("Exiting....")
    elif args.list_hashes and not (args.DEBUG or args.hashes or args.chunk
                                 or args.serial or args.dcfldd):
        print("All Hashes List:")
        for i in hash_list:
            print("\t" + i)
    else:
        print("Invalid arguments passed. Retry!")
        parser.parse_args(["--help"])


if __name__ == "__main__":
    main()
