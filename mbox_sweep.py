import xml.etree.ElementTree as ET
import xml_operations
import create_xml_dictionary
import pprint



spec_xml_file_path = "bios_mailbox.xml"
spec = create_xml_dictionary.parse_spec_xml(spec_xml_file_path)
checkers_xml_file_path = "error_codes_1.xml"
error_codes, spec_globals = create_xml_dictionary.parse_error_codes_xml(checkers_xml_file_path)
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
                print("\n")
                #print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                print("****************************************************************************************")
                print("START --> ", mbox_cmd.find('cmd_name').text)

                #pprint.pprint(trace)
                # Check 1 : if <crash_log> exists => test_result = FAIL
                if mbox_cmd.find('crash_log') is not None:
                    print("CRASH_DETECTED")
                    add_test_result.text = 'FAIL'
                    mbox_cmd.append(add_test_result)
                    continue

                # Check 2 : if no errors codes are defined for the mbox cmd , always expect NO_ERROR
                if error_codes.get(mbox_cmd.find('cmd_name').text) is None:
                    print("NO_ERROR_CODES")
                    add_test_remark.text = 'NO ERROR CODES Defined'
                    if mbox_cmd.find('./response/error').text == 'NO_ERROR':
                        add_test_result.text = 'PASS'
                    else:
                        add_test_result.text = 'FAIL'
                else:
                # Check 3 : run_all command rules/checkers
                    #print("PROCESSING_ERROR_CODES")
                    trace = create_xml_dictionary.populate_trace_cmd(mbox_cmd, spec)
                    valid_error_codes = xml_operations.process_cmd_rules(trace, spec , error_codes, spec_globals)
                    #print(valid_error_codes)
                    add_test_result.text = 'FAIL'
                    #if valid_error_codes == []:
                     #   add_test_result.text = 'PASS'

                    print("FW_ERROR ->",mbox_cmd.find('./response/error').text,"VALID_CODES ->", valid_error_codes )
    
                    if len(valid_error_codes) != 0:
                        if mbox_cmd.find('./response/error').text in valid_error_codes:
                            print("FW_ERROR ->",mbox_cmd.find('./response/error').text,", VALID_CODES ->", valid_error_codes )
                            add_test_result.text = 'PASS'
                    else:
                        if mbox_cmd.find('./response/error').text == 'NO_ERROR':
                            add_test_result.text = 'PASS'

                        #elif valid_error_codes == []:
                         #   add_test_result.text = 'PASS'

                               
                      



                
                mbox_cmd.append(add_test_result)
                mbox_cmd.append(add_test_remark)
                print("END --> ", mbox_cmd.find('cmd_name').text, "STATUS --> ", add_test_result.text)
                #print("STATUS --> ", add_test_result.text)
                #print("END --> ", mbox_cmd.find('cmd_name').text)
                #print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                print("****************************************************************************************")
                # pprint.pprint(trace)
                # pprint.pprint("---------------------------------")

trace_tree.write("trace_out.xml")
#pprint.pprint(spec['SVID_VR_HANDLER'])
#pprint.pprint(error_codes['bios_error_codes']['SVID_VR_HANDLER'])
#pprint.pprint(error_codes['bios_error_codes']['SVID_VR_HANDLER']['rule'])

