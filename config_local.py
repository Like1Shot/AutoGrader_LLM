import os

BASE_DIR = os.path.join(os.path.expanduser("~/Documents/CU Boulder/Grading"))

COURSE_NUM = 'CSPB-1300'
ASSIGNMENT_NAME = 'Lab2'

# Course configuration
COURSE_CONFIG = {
    'number': COURSE_NUM,
    'assignments_dir': os.path.join(BASE_DIR, COURSE_NUM, ASSIGNMENT_NAME),
}

# Grading configuration
GRADING_CONFIG = {
    'rubric_path': os.path.join(BASE_DIR, COURSE_NUM, 'Rubrics', f'{ASSIGNMENT_NAME}_Rubric.md'),
    'output_dir': os.path.join(BASE_DIR, COURSE_NUM, 'Reports'),
    'output_format': 'csv',
    'submission_pattern': '*_assignsubmission_file_',
}

# LLM configuration
LLM_CONFIG = {
    'model_name': 'llama2',
    'temperature': 0.1,  # Lower for more consistent grading
    'max_tokens': 1000,
}
