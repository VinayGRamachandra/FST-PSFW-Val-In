#!/usr/intel/bin/bash -f
#
# <details>
# Runs bias xml file for <count> iterations and populates VV logs to mailbox_fuzzing_log.xml
# <usage> mailbox_fuzz.sh <count> "./scripts/run_feature_xml.sh $MODEL_ROOT/verif/tests/fox2/kiwi/bias/feature_xml/<biasfile>"
# <example bios> mailbox_fuzz.sh 10 "./scripts/run_feature_xml.sh $MODEL_ROOT/verif/tests/fox2/kiwi/bias/feature_xml/bios.xml"
#




for (( i=1 ; i<=$1 ; i++ ));
do
  $2
done

# Mailbox Fuzzing xml Log creation
# Chdir to regressions
cd $MODEL_ROOT/regressions

rm fuzzing_log.xml
rm mailbox_fuzzing_log.xml
# find fox2run.log
for filename in $(find . -name "fox2run.log")

do
    echo $filename > /dev/null
    ag --no-numbers --no-filename "KIWI_XML_LOG" $filename > kiwi_tmp.xml
    sed -i 's/\<KIWI_XML_LOG\>//g' kiwi_tmp.xml
    type=$(grep -m 1 "KIWI_XML_LOG" "$filename" | sed 's/.*KIWI_XML_LOG//')
    

    if ag --silent "status 255" $filename; then
        echo "<crash_log>" >> kiwi_tmp.xml
        ag '\-E\-' $filename | tr '\n' ' ' >> kiwi_tmp.xml
        echo "</crash_log>" >> kiwi_tmp.xml
        head -n 1 kiwi_tmp.xml | sed 's/</<\//g' >> kiwi_tmp.xml
        sed -i "1i <file name=\"$filename\">" kiwi_tmp.xml
        echo "</file>" >> kiwi_tmp.xml
        if xmllint --noout --format kiwi_tmp.xml; then
            cat kiwi_tmp.xml >> fuzzing_log.xml
        else
            echo "ERROR : issue with the trace $filename"
            break
        fi
    else
        sed -i "1i <file name=\"$filename\">" kiwi_tmp.xml
        echo "</file>" >> kiwi_tmp.xml
         
        if xmllint --noout --format kiwi_tmp.xml; then
            cat kiwi_tmp.xml >> fuzzing_log.xml
        else
            echo "ERROR : issue with the trace $filename"
            break
        fi
      
    fi
    
done
sed -i '1i <root>' fuzzing_log.xml
echo "</root>" >> fuzzing_log.xml
xmllint --format fuzzing_log.xml >> mailbox_fuzzing_log.xml

command_type=$(echo "$type" | sed -n 's/.*MAILBOX_\([^_]*\)_CMD.*/\1/p' | tr '[:upper:]' '[:lower:]')
export command_type
python_script="$MODEL_ROOT/verif/tests/fox2/kiwi/helper_scripts/mailbox_error_code_check.py"
python3 $python_script
