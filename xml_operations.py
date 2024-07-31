import xml.etree.ElementTree as ET
import pprint
import re

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
    print("operands" , operands , "operator" , operator)

    left = get_operand_val(operands[0], trace, spec, error_codes, spec_globals)
    right = get_operand_val(operands[1], trace, spec, error_codes, spec_globals)
    print("left", left , "right" , right)
    out = apply_operation(operator[0], left, right)


    return out 


def process_cmd_rules(trace, spec, error_codes, spec_globals):
    error = 'NO_ERROR'
    print("+++++++++++++++++++++++++++++++++++++++++")
    print("trace")
    pprint.pprint(trace)
    key = list(trace.keys())
    print("error_codes")
    pprint.pprint(error_codes[key[0]])
    print("spec")
    pprint.pprint(spec[key[0]])
    valid_error_codes = []
    for ekey , evalue in error_codes[key[0]].items():
        out_1 = False
        out = False
        for rule in evalue:
            logical_oper = find_logical_operator(rule)
            sub_rule = get_strings_between_parentheses(rule)
            print("rule" , rule ,"logical_oper" , logical_oper)
            if not logical_oper:
                print("No logical operation")
                out = process_rule(sub_rule[0], trace, spec, error_codes, spec_globals)
            else:
                print("sub_rule[0]",sub_rule[0],"sub_rule[1]",sub_rule[1])
                out = apply_logical_operator(logical_oper[0], 
                                             process_rule(sub_rule[0], trace, spec, error_codes, spec_globals), 
                                             process_rule(sub_rule[1], trace, spec, error_codes, spec_globals))
            

            out_1 = out_1 or out
            print(f"out====={out}")
            print(f"out1 ==== {out_1}")
        if out_1:
            valid_error_codes.append(ekey)
    print("Valid error codes", valid_error_codes)
    print("+++++++++++++++++++++++++++++++++++++++++")
    return valid_error_codes

