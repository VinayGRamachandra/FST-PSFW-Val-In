import xml.etree.ElementTree as ET
import pprint


def parse_spec_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    command_elements = root.findall(".//command")
    spec={}
    for command in command_elements:
        command_name = command.find('name').text
        opcode = command.find('opcode').text
        spec[command_name]={'opcode' : opcode, 'interface':{}}

        if command.find("deprecated") is not None:
            for field in command.findall('deprecated'):
                spec[command_name]['deprecated']={"project":field.attrib['project']}

        if command.find("lock_event") is not None:
            for field in command.findall('lock_event'):
                spec[command_name]['lock_event']={"stage":field.attrib['lock'], "phase":field.attrib["type"]}

        if command.find('interface') is not None:
            for field in command.find('interface'):
                for field_names in field:
                    spec[command_name]['interface'][field.find("name").text] = {'lsb':int(field.find('lsb').text), 
                                                                                'num_bits':int(field.find('num_bits').text)} #use this method when needed multiple elements inside a field

                if field.findall('enum') is not None:
                    for enum in field.findall('enum'):
                        spec[command_name]["interface"][field.find("name").text][enum.attrib['key']] = {'val' : int(enum.attrib['val'],16)}

                        for data in command.findall('data'):
                            if data.get('dir') and data.get('key') is not None:
                                if data.attrib['dir'] == 'in':
                                    if data.attrib['key'] == enum.attrib['key']:
                                        if data.findall('field') is not None:
                                            spec[command_name]["interface"][field.find("name").text][enum.attrib["key"]]["data_in"] = {}
                                            for field_data in data.findall('field'):
                                                spec[command_name]["interface"][field.find("name").text][enum.attrib["key"]]["data_in"][field_data.find('name').text] = {"lsb":int(field_data.find('lsb').text), 
                                                                                                                                                                         "num_bits":int(field_data.find('num_bits').text)}
                            
    return spec

def parse_error_codes_xml(xml_file_path):

    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    error_codes = {}
    spec_globals = {}
    for code in root.findall('./*'):
        error_codes[code.tag] = {}
        for rule in code.findall('rule'):
            error_codes[code.tag][rule.attrib['code']] = []
            for xx in rule.findall('if'):
                error_codes[code.tag][rule.attrib['code']].append(xx.text)
    gspec = root.find('spec_globals')
    spec_globals = {}
    for elem in gspec.findall('./*'):
        spec_globals[elem.tag] = elem.findtext('val')
    return error_codes, spec_globals

def extract_bits(number, k, p):
    # Right shift the number by p-1 bits to get the desired bits at the rightmost end of the number
    shifted_number = number >> p
 
    # Mask the rightmost k bits to get rid of any additional bits on the left
    mask = (1 << k) - 1
    extracted_bits = shifted_number & mask
 
    # Convert the extracted bits to decimal
    extracted_number = bin(extracted_bits)[2:]
    decimal_value = int(extracted_number, 2)
 
    return decimal_value
 
def populate_trace_cmd(mbox_cmd, spec):

    trace = {}
    cmd_key = mbox_cmd.find('cmd_name').text
    sub_cmd_key = mbox_cmd.find('cmd_name').text
    timing = mbox_cmd.find('exec_timing_info')
    response_data = mbox_cmd.find('./response/data').text
    command_data = mbox_cmd.find('./command/data').text
     
    trace[cmd_key] = { 'opcode' : spec[cmd_key]['opcode'] }
    trace[cmd_key]['timing'] = { 'stage' : timing.get('stage') , 'phase' : timing.get('phase') }
    trace[cmd_key]['interface']= {}
    trace[cmd_key]['response_data']= response_data
    trace[cmd_key]['command_data']= command_data
    for key in spec[cmd_key]['interface'].keys():
        trace[cmd_key]['interface'][key] = extract_bits(int(mbox_cmd.find('command').find('interface').text), 
                                                        int(spec[cmd_key]['interface'][key]['num_bits']), 
                                                        int(spec[cmd_key]['interface'][key]['lsb']))
         
        for enum_key in spec[cmd_key]['interface'][key].keys():
            if (enum_key != 'lsb' and enum_key != 'num_bits'):
                if spec[cmd_key]['interface'][key][enum_key]['val'] == trace[cmd_key]['interface'][key]:
                    if spec[cmd_key]['interface'][key][enum_key].get('data_in') is not None:
                        data_keys = spec[cmd_key]['interface'][key][enum_key]['data_in'].keys()
                        trace[cmd_key]['data'] = {}
                        for data_key in data_keys:
                            trace[cmd_key]['data'][data_key] = extract_bits(int(mbox_cmd.find('command').find('data').text),
                                                                            int(spec[cmd_key]['interface'][key][enum_key]['data_in'][data_key]['num_bits']), 
                                                                            int(spec[cmd_key]['interface'][key][enum_key]['data_in'][data_key]['lsb']))
    return trace
