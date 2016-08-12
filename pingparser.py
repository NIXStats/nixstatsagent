#!/usr/bin/env python
# coding: utf-8
"""
Parses the output of the system ping command.
"""
__version__ = '0.3'

from optparse import OptionGroup,OptionParser

import re
import sys

def _get_match_groups(ping_output, regex):
    match = regex.search(ping_output)
    if not match:
        raise Exception('Invalid PING output:\n' + ping_output)
    return match.groups()

def parse(ping_output):
    """
    Parses the `ping_output` string into a dictionary containing the following
    fields:

        `host`: *string*; the target hostname that was pinged
        `sent`: *int*; the number of ping request packets sent
        `received`: *int*; the number of ping reply packets received
        `packet_loss`: *int*; the percentage of  packet loss
        `minping`: *float*; the minimum (fastest) round trip ping request/reply
                    time in milliseconds
        `avgping`: *float*; the average round trip ping time in milliseconds
        `maxping`: *float*; the maximum (slowest) round trip ping time in
                    milliseconds
        `jitter`: *float*; the standard deviation between round trip ping times
                    in milliseconds
    """
    matcher = re.compile(r'PING ([a-zA-Z0-9.\-]+) \(')
    host = _get_match_groups(ping_output, matcher)[0]

    matcher = re.compile(r'(\d+) packets transmitted, (\d+) received, (\d+)% packet loss')
    sent, received, packet_loss = _get_match_groups(ping_output, matcher)

    try:
        matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
        minping, avgping, maxping, jitter = _get_match_groups(ping_output,
                                                              matcher)
    except:
        minping, avgping, maxping, jitter = ['NaN']*4

    return {'host': host, 'sent': sent, 'received': received, 'packet_loss': packet_loss,
            'minping': minping, 'avgping': avgping, 'maxping': maxping,
            'jitter': jitter}


def main(argv=sys.argv):
    # detects whether input is piped in
    ping_output = None
    if not sys.stdin.isatty():
        ping_output = sys.stdin.read()

    usage = 'Usage: %prog [OPTIONS] [+FORMAT]\n\n'\
            'Parses output from the system ping command piped in via stdin.'
    parser = OptionParser(usage=usage, version="%prog " + __version__)

    format_group = OptionGroup(parser,
    """FORMAT controls the output. Interpreted sequences are:
    \t%h    host name or IP address
    \t%s    packets sent
    \t%r    packets received
    \t%p    packet_loss
    \t%m    minimum ping in milliseconds
    \t%a    average ping in milliseconds
    \t%M    maximum ping in milliseconds
    \t%j    jitter in milliseconds

    Default FORMAT is %h,%s,%r,%p,%m,%a,%M,%j""")
    parser.add_option_group(format_group)

    (options, args) = parser.parse_args()

    if ping_output is None:
        parser.print_help()
        sys.exit(1)

    ping_result = parse(ping_output)

    format_replacements = [('%h', 'host'),
                           ('%s', 'sent'),
                           ('%r', 'received'),
                           ('%p', 'packet_loss'),
                           ('%m', 'minping'),
                           ('%a', 'avgping'),
                           ('%M', 'maxping'),
                           ('%j', 'jitter')]
    format_replacements = [(fmt, ping_result[field]) for fmt, field in
                           format_replacements]

    if len(args) == 0:
        output = ','.join(fmt for (fmt, rep) in format_replacements)
    elif args[0].startswith('+'):
        args[0] = args[0].lstrip('+')
        output = ' '.join(args[0:])
    else:
        parser.print_help()

    for (fmt, rep) in format_replacements:
        output = output.replace(fmt, rep)

    sys.stdout.write(output)

    sys.exit(0)

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass