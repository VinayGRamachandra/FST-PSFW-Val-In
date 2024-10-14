import os
import xml.etree.ElementTree as ET


def extract_burger_content_from_file(file_path): 
    burger_content = ''
    crashlog_added = False
    try:
    
        with open(file_path, 'r') as infile:
            lines = infile.readlines()
                
        
        for line in lines:
            if 'KIWI_XML_LOG' in line:
                content_after_burger = line.split('KIWI_XML_LOG')[1].strip()
                burger_content += f"    {content_after_burger}\n"
            
            if 'status 255' in line and not crashlog_added:
        
                burger_content += "    <crash_log> Spurious MCA hit. MCA hit is - MCA_PMSB_TIMEOUT </crash_log>\n"
                crashlog_added = True



    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

    return burger_content

def parse_logs_and_generate_xml(root_directory, output_file):
    xml_content = ''  
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file == "fox2run.log":
                log_file_path = os.path.join(subdir, file)
                #print(f"Processing: {log_file_path}")        
                content = extract_burger_content_from_file(log_file_path)
                if content:
                   
                    xml_content += content           
    final_xml_content = xml_content #xml_header + xml_content + xml_footer
    with open(output_file, 'w') as outfile:
        outfile.write(final_xml_content)
root_directory = '/nfs/site/disks/xpg_dmrhub_0441/yraju/firmware.management.primecode.validation/regressions'  
output_file = 'final_output.xml'  
parse_logs_and_generate_xml(root_directory, output_file)


def fix_unclosed_mailbox_commands(input_file, output_file):
    try:
        input_file_path = os.path.abspath(input_file)
         
        with open(input_file, 'r') as infile:
            lines = infile.readlines()
        
        fixed_lines = []
        open_mailbox = False  
        fixed_lines.append('<?xml version="1.0"?>\n<root>\n')
        fixed_lines.append(f'  <file name="{input_file_path}">\n')
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("<MAILBOX_INTERNAL_CMD>"):
                if open_mailbox:
                    
                    fixed_lines.append("    </MAILBOX_INTERNAL_CMD>\n")
                    open_mailbox = False
                open_mailbox = True  

            if stripped_line.startswith("</MAILBOX_INTERNAL_CMD>"):
                open_mailbox = False
            
            fixed_lines.append(line)
        if open_mailbox:
            fixed_lines.append("  </MAILBOX_INTERNAL_CMD>\n")

        fixed_lines.append('  </file>\n')
        fixed_lines.append('</root>\n')
        
        with open(output_file, 'w') as outfile:
            outfile.writelines(fixed_lines)

    except FileNotFoundError:
        print(f"The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_file = 'final_output.xml'  
output_file = 'fixed_output.xml'  
fix_unclosed_mailbox_commands(input_file, output_file)


from xml.dom import minidom
import xml.etree.ElementTree as ET


def prettify_xml(elem):
    
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml=reparsed.toprettyxml(indent="   ")
    lines = [line for line in pretty_xml.splitlines() if line.strip()]
    return "\n".join(lines)

def format_xml(input_file, output_file):
    try:
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        pretty_xml = prettify_xml(root)

        
        with open(output_file, 'w') as outfile:
            outfile.write(pretty_xml)

    except FileNotFoundError:
        print(f"The file {input_file} does not exist.")
    except ET.ParseError as e:
        print(f"An error occurred while parsing the XML file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

input_file = 'fixed_output.xml' 
output_file = 'internal_fuzzing_log.xml' 
format_xml(input_file, output_file)
