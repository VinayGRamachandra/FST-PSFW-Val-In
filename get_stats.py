

command_status = {}
total_pass = 0
total_fail = 0

with open('xx.text', 'r') as file:
    lines = file.readlines()

current_command = None
crash_count = 0

for line in lines:
    if line.startswith('START -->'):
        
        current_command = line.split('-->')[1].strip()
        
        if current_command not in command_status:
            command_status[current_command] = {'PASS': 0, 'FAIL': 0}
    elif 'STATUS -->' in line and current_command:
        if 'STATUS -->  PASS' in line:
            command_status[current_command]['PASS'] += 1
            total_pass+=1
        elif 'STATUS -->  FAIL' in line:
            command_status[current_command]['FAIL'] += 1
            total_fail+=1
        
        current_command = None
    if 'CRASH_DETECTED' in line:
        crash_count += 1

print("\n")
print(f"Total number of Crashes = {crash_count}")
print(f"Number of B2P commands in B2P Mailbox Specification: 28")
commands_count = len(command_status)
print(f"Number of Unique B2P commands in Trace: {commands_count}")

#for command in command_status.keys():
 #   print(f"command_names = {command}"  )

print(f"\nNumber of successful B2P commands : {total_pass}")
print(f"Number of Failed B2P commands: {total_fail}")
for command, status in command_status.items():
    if status['FAIL'] !=0:
        if command == "CR_PROXY":
            print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-12859)")
        elif command == "IO_CONFIG":
            print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-12855, https://jira.devtools.intel.com/browse/SERVERPMFW-12857)")
        elif command=="ADDDC_QUIESCE":
             print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-12861, https://jira.devtools.intel.com/browse/SERVERPMFW-12870)")
        elif command == "WRITE_PM_CONFIG" or command == "READ_PM_CONFIG":
             print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-12863, https://jira.devtools.intel.com/browse/SERVERPMFW-12865, https://jira.devtools.intel.com/browse/SERVERPMFW-11088)")
        elif command == "OC_TJ_MAX_OFFSET":
             print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-5560)")
        elif command == "PM_SECURITY_CONTROL":
              print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-11090)")
        elif command == "OOB_INIT_EPP":
              print(f"{command} ==> {status['FAIL']} (https://jira.devtools.intel.com/browse/SERVERPMFW-10656)")
        else:
            print(f"{command} ==>  {status['FAIL']} ")




            
