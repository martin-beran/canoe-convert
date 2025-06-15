import argparse
import csv
import os.path
import sys
import xml.etree.ElementTree as ET

def eskymo2canoe(classid, csv_data):
    '''Convert from Eskymo CSV export to Canoe123 XML'''
    it = iter(csv_data)
    try:
        while True:
            row = next(it)
            if (
                    row[0:8] == ['id', 'stč', 'rgc', 'jméno', 'nar.', 'vk', 'vt', 'oddíl'] or
                    row[0:8] == ['id', 'Bib', 'Id',  'Name',  'Age',  '',   '',   'Team']):
                break
    except StopIteration:
        raise RuntimeError('Expected header line missing in input CSV')
    root = ET.Element('root')
    root.text = '\n' + (' ' * 4)
    xml_data = ET.ElementTree(element=root)
    i_line = 0
    try:
        while True:
            i_line += 1
            row = next(it)
            row = [e.strip() for e in row]
            if row[1] == '':
                break
            if row[4] == '' and row[5] == '':
                continue

            p = ET.SubElement(root, 'Participants')
            id = '.'.join(row[2].split())
            ET.SubElement(p, 'Id').text = f'{id}.{classid}.{row[5]}'
            ET.SubElement(p, 'ClassId').text = classid
            icfids = row[2].split()
            ET.SubElement(p, 'EventBib').text = row[1]
            ET.SubElement(p, 'ICFId').text = icfids[0]
            names = row[3].split('\n')
            family_name, given_name = names[0].strip().split(None, 1)
            ET.SubElement(p, 'FamilyName').text = family_name
            ET.SubElement(p, 'GivenName').text = given_name
            if len(names) > 1:
                family_name, given_name = names[1].strip().split(None, 1)
                ET.SubElement(p, 'FamilyName2').text = family_name
                ET.SubElement(p, 'GivenName2').text = given_name
            if len(icfids) > 1:
                ET.SubElement(p, 'ICFId2').text = icfids[1]
            ET.SubElement(p, 'Club').text = row[7]
            ET.SubElement(p, 'Ranking').text = row[1]
            ET.SubElement(p, 'RankingPoints').text = row[1]
            birth = row[4].split()
            birth = list(map(lambda s: s.replace('#', ''), birth))
            if len(birth) > 0:
                ET.SubElement(p, 'Birthdate').text = f'{birth[0]}-01-01T00:00:00+01:00'
                if len(birth) > 1:
                    ET.SubElement(p, 'Birthdate2').text = f'{birth[1]}-01-01T00:00:00+01:00'
                ET.SubElement(p, 'Year').text = birth[0]
            ET.SubElement(p, 'CatId').text = row[5]
            ET.SubElement(p, 'IsTeam').text = 'false'
            ET.SubElement(p, '_Bib').text = row[6]
            format_xml(p)
    except StopIteration:
        pass
    except Exception as e:
        print(f'Exception when processing participant {i_line}')
        raise
    p.tail = '\n'
    return xml_data

def canoe2eskymo(classid, xml_data, bibs_data, day):
    '''Convert from Canoe123 XML to Eskymo CSV for import'''
    ns={'':'http://siwidata.com/Canoe123/Data.xsd'}
    days = set()
    for res in xml_data.iterfind('./Results', ns):
        raceid = res.find('RaceId', ns).text.strip().split('_')[-1]
        days.add(raceid)
        if len(days) > 1 and day is None:
            raise RuntimeError('Multiple races found, option --day is required')
        if day is not None and raceid != day:
            continue
        if res.find('Id', ns).text.split('.')[1] != classid:
            continue
        bib = res.find('Bib', ns).text.strip()
        if bib not in bibs_data:
            continue
        b = bibs_data[bib]
        if res.find('PrevStatus', ns) is None and res.find('PrevTime', ns) is None:
            i = 0
        else:
            i = 1
        print(bib, i)
        s = res.find('Status', ns)
        if s is not None and s.text is not None:
            s = s.text.strip()
        else:
            s = ''
        b[i]['p'] = '999'
        if (t := res.find('Time', ns)) is not None:
            b[i]['t'] = f'{int(t.text)//1000},{int(t.text)%1000:03}'
            p = res.find('Pen', ns)
            if p is not None:
                b[i]['p'] = p.text
        else:
            b[i]['t'] = s
    csv_data = [
        [k, v[0]['t'], v[0]['p'], v[1]['t'], v[1]['p']] for k, v in bibs_data.items()
    ]
    return csv_data

def eskymo2canoe_file(classid, csv_file, xml_file):
    with open(csv_file) as cf:
        reader = csv.reader(cf)
        csv_data = list(reader)
    try:
        xml_data = eskymo2canoe(classid, csv_data)
    except Exception as e:
        print(f'Exception when processing file {csv_file}')
        raise
    xml_data.write(xml_file, encoding='utf-8', short_empty_elements=False)

def canoe2eskymo_file(classid, xml_file, csv_file, bibs_file, day):
    xml_data = ET.parse(xml_file)
    with open(bibs_file) as bf:
        reader = csv.reader(bf)
        bibs_data = list(reader)
    bibs_data = {
        str(b[5]): [{'t': '', 'p': ''}, {'t': '', 'p': ''}]
        for b in bibs_data
        if except_none(lambda: int(b[5])) is not None
    }
    csv_data = canoe2eskymo(classid, xml_data, bibs_data, day)
    with open(csv_file, 'w') as cf:
        writer = csv.writer(cf)
        writer.writerows(csv_data)

XML_IDENT = 4

def format_xml(el):
    el.text = '\n' + (' ' * 2 * XML_IDENT)
    el.tail = '\n' + (' ' * XML_IDENT)
    prev = None
    for sub in el:
        if prev is not None:
            prev.tail = '\n' + (' ' * 2 * XML_IDENT)
        prev = sub
    prev.tail = '\n' + (' ' * XML_IDENT)

def except_none(f):
    try:
        return f()
    except Exception:
        return None
    
def cmdline():
    prog = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Convert start lists and results between Eskymo/CSV and Canoe123/XML',
        epilog='''
Conversions:

    e2c
        Converts a start list from Eskymo to Canoe123.
        Source file is Eskymo start list sheet exported as CSV with
           - charset UTF-8
           - delimiter ',' (comma)
           - quoting character '"' (double quote)
        Destination is a part of Canoe123 XML data, to be added into
        an event XML file.
    c2e
        Converts a Canoe123 XML file to a CSV file containing values
        for all result sheets in Eskymo. Parameters of the CSV file
        are the same as for e2c. 
'''
    )
    parser.add_argument(
        '-c', '--conv', choices=['e2c', 'c2e'], required=True,
        help='Direction of conversion: e2c = Eskymo to Canoe123, c2e=Canoe123 to Eskymo')
    parser.add_argument(
        '-C', '--classid', required=True,
        help='Class id as used in Canoe123')
    parser.add_argument(
        '-D', '--day', help='Race day of month, used only by -c c2e')
    parser.add_argument('source', help='Source file name: CSV for -c e2c, XML for -c c2e')
    parser.add_argument(
        'destination',
        help='Destination file name: XML for -c e2c, CSV for -c c2e')
    parser.add_argument(
        'bibs',
        help='Optional CSV with bibs, used only by -c c2e',
        nargs='?')
    args = parser.parse_args()
    if args.conv == 'e2c' and args.bibs is not None:
        print('Unexpected argument bibs')
        parser.print_help()
        exit(1)
    if args.conv == 'c2e' and args.bibs is None:
        args.bibs = args.destination
    return args

args = cmdline()
match args.conv:
    case 'e2c':
        eskymo2canoe_file(args.classid, args.source, args.destination)
    case 'c2e':
        canoe2eskymo_file(args.classid, args.source, args.destination, args.bibs, args.day)
    case _:
        assert False
