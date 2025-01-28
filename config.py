import os
from pathlib import Path

# Base paths
BASE_DIR = os.path.expanduser("~/Documents/CU Boulder/Grading")

# Course configuration
COURSE_CONFIG = {
    'number': 'DEFAULT-COURSE',  # Override this in config.local.py
    'assignments_dir': None,  # Will be set based on course number
}

# Grading configuration
GRADING_CONFIG = {
    'rubric_path': None,  # Set this in config.local.py
    'output_dir': os.path.join(BASE_DIR, 'reports'),
    'output_format': 'csv',
    'submission_pattern': '*_assignsubmission_file_',
}

# LLM configuration
LLM_CONFIG = {
    'model_name': 'llama2:3.2',
    'temperature': 0.1,
    'max_tokens': 1000,
}

# File patterns
FILE_PATTERNS = {
    'submissions': '*.pdf',
    'student_folder_pattern': '*_*_assignsubmission_file_'
}

# Report configuration
REPORT_CONFIG = {
    'filename_template': '{course}_grades_{timestamp}.csv',
    'timestamp_format': '%Y%m%d_%H%M%S',
    'columns': [
        'Student',
        'Grade',
        'Feedback',
        'Submission Path',
        'Status',
        'Timestamp'
    ]
}

# try:
#     # Try to import local config and override settings
#     from config_local import *
    
#     # Set dependent paths if not explicitly set in local config
#     if COURSE_CONFIG['assignments_dir'] is None:
#         COURSE_CONFIG['assignments_dir'] = os.path.join(BASE_DIR, COURSE_CONFIG['number'])
    
#     # Create necessary directories
#     for directory in [
#         BASE_DIR,
#         COURSE_CONFIG['assignments_dir'],
#         GRADING_CONFIG['output_dir'],
#     ]:
#         os.makedirs(directory, exist_ok=True)
    
#     # Create rubrics directory if rubric path is set
#     if GRADING_CONFIG['rubric_path']:
#         os.makedirs(os.path.dirname(GRADING_CONFIG['rubric_path']), exist_ok=True)
        
# except ImportError:
#     print("⚠️  No config_local.py found. Using default settings.")
#     print("ℹ️  Create a config_local.py file to override default settings.")
