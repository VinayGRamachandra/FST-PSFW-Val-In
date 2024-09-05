############create_xml


import xml.etree.ElementTree as ET
import pprint
import re


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














#######xml_operations






def get_strings_between_parentheses(s):
    matches = re.findall(r'\((.*?)\)', s)
    return matches

def find_logical_operator(s):
    matches = re.findall(r'\)\s*(.*?)\s*\(', s)
    return matches

def find_operator(s):
    # Regular expression to match arithmetic and conditional operators
    pattern = r'&|not_in|is_in|==|!=|>=|<=|>|<|//'
    matches = re.findall(pattern, s)
    return matches


# Function to apply an arithmetic operator based on a given operator string
def apply_arthimetic_operator(operator_str, *args):

    # Define lambda functions for arithmetic operations
    arthimetic_operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else None,
    }

    if operator_str in operations:
        return arthimetic_operations[operator_str](*args)
    else:
        return None


# Function ?to apply a logical operator based on a given operator string
def apply_logical_operator(operator_str, *args):

    # Define lambda functions for logical operations
    logical_operations = {
        'and': lambda *args: all(args),
        'or': lambda *args: any(args),
        'not': lambda x: not x,
        'xor': lambda *args: sum(args) % 2 == 1
    }

    if operator_str in logical_operations:
        if operator_str == 'not':
            return logical_operations[operator_str](args[0])
        else:
            return logical_operations[operator_str](*args)
    else:
        return None


# Function to apply a conditional operator based on a given operator string
def apply_conditional_operator(operator_str, *args):

    # Define lambda functions for conditional operations
    conditional_operations = {
        '<': lambda x, y: x < y,
        '>': lambda x, y: x > y,
        '<=': lambda x, y: x <= y,
        '>=': lambda x, y: x >= y,
        '==': lambda x, y: x == y,
        '!=': lambda x, y: x != y
    }

    if operator_str in conditional_operations:
        return conditional_operations[operator_str](*args)
    else:
        return None


def apply_operation(operation , left, right):
   
    out = False
    if operation == '&':
        if left & right: 
            out = True
    elif operation == 'not_in':
        if int(left) not in list(right):
            out = True
    elif operation == 'is_in':
        if int(left) in list(right):
            out = True
    else:
        out = apply_conditional_operator(operation, left , right)

    return out


def find_key(nested_dict, key):
    if key in nested_dict:
        return nested_dict[key]
    
    for k, v in nested_dict.items():
        if isinstance(v, dict):
            result = find_key(v, key)
            if result is not None:
                return result
    
    return None

def get_operand_val(operand, trace, spec, error_codes, spec_globals):
    oper = operand.strip()
    if 'tag.' in oper:
        if 'timing' == oper.replace('tag.',""):
            if find_key(trace, 'stage') == 'runtime':
                val = 7
            elif find_key(trace, 'stage') == 'reset':
                val = 0
            else:
                val = find_key(trace, 'phase')
                val = int(val.replace('PH',""))
        else:
            val = find_key(trace, oper.replace('tag.',""))
            val = int(val)
    elif 'field.' in operand:
        val = find_key(trace, oper.replace('field.',""))
        val = int(val)
    elif 'key.' in oper:
        val = find_key(spec, oper.replace('key.',""))
        val = int(val['val'])
    elif 'globals.' in oper:
        val = find_key(spec_globals, oper.replace('globals.',""))
        if oper.replace('globals.',"") == "DMR_VALID_VR_ADDRESS":

            str_val = val.replace('[',"")
            str_val = str_val.replace(']',"")
            val = []
            for i in str_val.split(','):
                val.append(int(i))
        else:
            if "0x" in val:
                val = int(val,16)
            else:
                val = int(val)
    else:
        if "0x0" in oper:
            val = int(oper,16)
        else:
            val = int(oper)
    return val


def process_rule(rule, trace, spec, error_codes, spec_globals):
    out = False
    operator = find_operator(rule)
    operands = rule.split(operator[0])
    #print("operands" , operands , "operator" , operator)

    left = get_operand_val(operands[0], trace, spec, error_codes, spec_globals)
    right = get_operand_val(operands[1], trace, spec, error_codes, spec_globals)
    #print("left", left , "right" , right)
    #print(left, operator, right)
    out = apply_operation(operator[0], left, right)


    return out 


def process_cmd_rules(trace, spec, error_codes, spec_globals):
    error = 'NO_ERROR'
    #print("+++++++++++++++++++++++++++++++++++++++++")
    #print("trace ")

    #pprint.pprint(trace)
    key = list(trace.keys())
    #print("\n")
    #print("error_codes")
    #pprint.pprint(error_codes[key[0]])
    #print("\n")
    #print("spec")
    #pprint.pprint(spec[key[0]])
    #print("\n")
    valid_error_codes = []
    for ekey , evalue in error_codes[key[0]].items():
        out_1 = False
        out = False
        for rule in evalue:
            logical_oper = find_logical_operator(rule)
            sub_rule = get_strings_between_parentheses(rule)
            #print("rule" , rule ,"logical_oper" , logical_oper)
            #print(rule, logical_oper)
            if not logical_oper:
                #print("No logical operation")
                out = process_rule(sub_rule[0], trace, spec, error_codes, spec_globals)
            else:
                #print("sub_rule[0]",sub_rule[0],"sub_rule[1]",sub_rule[1])
                out = apply_logical_operator(logical_oper[0], 
                                             process_rule(sub_rule[0], trace, spec, error_codes, spec_globals), 
                                             process_rule(sub_rule[1], trace, spec, error_codes, spec_globals))
            

            out_1 = out_1 or out
            #print(f"out====={out}")
            #print(f"out = {out_1}")
            #print("\n")
        if out_1:
            valid_error_codes.append(ekey)
    #print("Valid error codes expected -> ", valid_error_codes)
    
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return valid_error_codes








###########mbox_sweep


spec_xml_file_path = "bios_mailbox.xml"
spec = parse_spec_xml(spec_xml_file_path)
checkers_xml_file_path = "error_codes_1.xml"
error_codes, spec_globals = parse_error_codes_xml(checkers_xml_file_path)
#pprint.pprint(spec)
#pprint.pprint(error_codes)
#pprint.pprint(spec_globals)

trace_tree = ET.parse("mailbox_fuzzing_log.xml")
trace_root = trace_tree.getroot()
if trace_root.findall('file') is not None:
    for file in trace_root.findall('file'):
        if file.findall('MAILBOX_BIOS_CMD') is not None:
            for mbox_cmd in file.findall('MAILBOX_BIOS_CMD'):
                add_test_result = ET.Element('test_result')
                add_test_remark = ET.Element('test_remark')
                #print("\n")
                #print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                #print("****************************************************************************************")
                #print("START --> ", mbox_cmd.find('cmd_name').text)

                #pprint.pprint(trace)
                # Check 1 : if <crash_log> exists => test_result = FAIL
                if mbox_cmd.find('crash_log') is not None:
                    #print("CRASH_DETECTED")
                    add_test_result.text = 'FAIL'
                    mbox_cmd.append(add_test_result)
                    continue

                # Check 2 : if no errors codes are defined for the mbox cmd , always expect NO_ERROR
                if error_codes.get(mbox_cmd.find('cmd_name').text) is None:
                    #print("NO_ERROR_CODES")
                    add_test_remark.text = 'NO ERROR CODES Defined'
                    if mbox_cmd.find('./response/error').text == 'NO_ERROR':
                        add_test_result.text = 'PASS'
                    else:
                        add_test_result.text = 'FAIL'
                else:
                # Check 3 : run_all command rules/checkers
                    #print("PROCESSING_ERROR_CODES")
                    trace = populate_trace_cmd(mbox_cmd, spec)
                    valid_error_codes = process_cmd_rules(trace, spec , error_codes, spec_globals)
                    #print(valid_error_codes)
                    add_test_result.text = 'FAIL'
                    #if valid_error_codes == []:
                     #   add_test_result.text = 'PASS'

                    #print("FW_ERROR ->",mbox_cmd.find('./response/error').text,"VALID_CODES ->", valid_error_codes )
    
                    if len(valid_error_codes) != 0:
                        if mbox_cmd.find('./response/error').text in valid_error_codes:
                            #print("FW_ERROR ->",mbox_cmd.find('./response/error').text,", VALID_CODES ->", valid_error_codes )
                            add_test_result.text = 'PASS'
                    else:
                        if mbox_cmd.find('./response/error').text == 'NO_ERROR':
                            add_test_result.text = 'PASS'

                        #elif valid_error_codes == []:
                         #   add_test_result.text = 'PASS'

                               
                      



                
                mbox_cmd.append(add_test_result)
                mbox_cmd.append(add_test_remark)
                #print("END --> ", mbox_cmd.find('cmd_name').text, "STATUS --> ", add_test_result.text)
                #print("STATUS --> ", add_test_result.text)
                #print("END --> ", mbox_cmd.find('cmd_name').text)
                #print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                #print("****************************************************************************************")
                # pprint.pprint(trace)
                # pprint.pprint("---------------------------------")

trace_tree.write("trace_out_1.xml")
#pprint.pprint(spec['SVID_VR_HANDLER'])
#pprint.pprint(error_codes['bios_error_codes']['SVID_VR_HANDLER'])
#pprint.pprint(error_codes['bios_error_codes']['SVID_VR_HANDLER']['rule'])

def trace_stats(trace_out_file_path):
    tree = ET.parse(trace_out_file_path)
    root = tree.getroot()
    crash_count=0
    test_pass=0
    test_fail=0
    unique_cmd_name_list=[]
    if root.findall('file') is not None:
        for file in root.findall('file'):
            if file.findall('MAILBOX_BIOS_CMD') is not None:
                for mbox_cmd in file.findall('MAILBOX_BIOS_CMD'):
                    crash_count=0
                    
#                    for cmd in mbox_cmd:
#
#                        test_result = cmd.find('test_result')
#                        if test_result is not None and test_result.text == 'PASS':
#                        
#                        print(f"{}yes")
#                        #for test_result in mbox_cmd.find('test_result'):
#                        #if test_result.text=="PASS":
#                            test_pass+=1

                    test_remark = mbox_cmd.findall(".//test_remark")
                    
                    if mbox_cmd.find('crash_log') is not None:
                        for crashes in mbox_cmd.findall('crash_log'):
                            crash_count+=1
                        
                    if mbox_cmd.find('cmd_name').text not in unique_cmd_name_list:
                        unique_cmd_name_list.append(mbox_cmd.find('cmd_name').text)
                        num_commands = len(unique_cmd_name_list)
                        
                            #unique_cmd_name_list.append(cmd)
                    
                            #num_of_unique_cmd = len(unique_cmd_name_list)
                for result in file.findall('.//test_result'):
                    if result.text == 'PASS':
                        test_pass+=1
                    if result.text == 'FAIL':
                        test_fail+=1
                            


    print(f"Total number of Crashes = {crash_count}")
    print(f"Number of unique B2P commands in Trace = {num_commands}")
    print(f"Number of Successful B2P commands: {test_pass}")
    print(f"Number of Failed B2P commands: {test_fail}")
    
    return crash_count, num_commands#unique_cmd_name_list


trace_out_file_path = "trace_out_1.xml"
crash_count, num_commands = trace_stats(trace_out_file_path) 



