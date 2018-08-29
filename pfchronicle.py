import argparse
import os
import lxml

from subprocess import call

deductions =  \
    { 'safe': [62, 120, 178],
      'cottage': [48, 152, 256],
      'ilchok': [100, 302, 504],
      'timinic_dies': [56, 139, 222, 'boxA'],
      'cladara': [153, 371, 590],
      'pemak3': [0, 0, 0, 'boxC'],
      'timinic_stays': [0, 0, 0, 'boxB', 'Boon2'],
      'pemak5': [0, 0, 0, 'Boon1'],
     }
totals = [520, 1218, 1915]


def calculate(details):
    gold = totals
    conditions = []
    for key in deductions:
        if key in details:
            gold = [gold[x] - deductions[key][x] for x in range(len(totals))]
            conditions.extend(deductions[key][3:])

    print(gold)
    print(conditions)
    return (gold, conditions)

def render(scenario, gold, conditions, prestige, args):
    svgfile = '{}chron_plain.svg'.format(scenario)
    assert os.path.exists(svgfile)
    with open(svgfile) as f:
        chron = f.read()
        chron = chron.replace('GPGAIN', str(gold))
        for condition in conditions:
            # TODO: Find some xpath library that works with SVGs
        
            cross_node = 'id="' + condition + 'Cross'
            if cross_node in chron:
                print('Uncrossing{}'.format(condition))
                # It's crossed out, we need to uncross it.
                # node_location = chron.index(cross_node)
                # node_length = chron[node_location:].index('/>')
                chron = chron.replace(cross_node, cross_node + '"\n     opacity="0')
        chron = chron.replace('PRESTIGE', str(prestige))
        chron = _replace_fields(chron, args)

    with open(os.path.join('/tmp', svgfile), 'wt') as f:
        f.write(chron)

    if args.output:
        call(["inkscape", '--file=/tmp/{}'.format(svgfile), '--without-gui', '--export-pdf={}'.format(args.output)])
    else:
        call(["inkscape", '--file=/tmp/{}'.format(svgfile), '--without-gui', '--export-pdf={}chron.pdf'.format(scenario)])


def _replace_field(svgdata, fieldname, replacement):
    if replacement is None:
        replacement = ''
    return svgdata.replace(fieldname, replacement)

def _replace_fields(svgdata, args):
    svgdata = _replace_field(svgdata, 'EVENTNAME', args.eventname)
    svgdata = _replace_field(svgdata, 'EVENTCODE', args.eventcode)
    svgdata = _replace_field(svgdata, 'DATEFIELD', args.date)
    svgdata = _replace_field(svgdata, 'GMNUMBER', args.gm)
    svgdata = _replace_field(svgdata, 'DAYJOB', args.dayjob)
    return svgdata

def parse_args():
    parser = argparse.ArgumentParser(description="Generate chronicle sheets")
    parser.add_argument('-s', help='scenario', default='1001')
    parser.add_argument('-d', help='details')
    parser.add_argument('--tier', '-t', help='tier', type=int, default=0)
    parser.add_argument('--prestige', '-p', help='prestige gained')
    parser.add_argument('--eventname', help='event name')
    parser.add_argument('--eventcode', help='event code')
    parser.add_argument('--date', help='date')
    parser.add_argument('--gm', help='gm number')
    parser.add_argument('--dayjob', help='dayjob')
    parser.add_argument('--output', '-o')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.d is None:
        print(deductions.keys())
    else:
        gold, conditions = calculate(args.d)

        render(args.s, gold[args.tier], conditions, args.prestige, args)

