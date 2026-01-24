import sys
import os

# Redirect output to file
log_file = open('jan5_script_log.txt', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

# Import and run
from create_jan5_middle_scores import create_middle_score_tests
create_middle_score_tests()

# Close file
log_file.close()
print("Done - check jan5_script_log.txt")
