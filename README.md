# AutoGrader

An automated grading system using LangChain and Ollama for local LLM-based assignment grading. ONLY use as assistant for grading and not as the final grade!

## Features
- Local LLM grading using Ollama
- Supports PDF submissions and Markdown rubrics
- Batch processing of student submissions
- Structured grade reports in CSV format
- Configurable grading parameters

## Prerequisites
- Python 3.8+
- Ollama installed and running
- llama2 model pulled in Ollama

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AutoGrader.git
cd AutoGrader
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install and set up Ollama:
```bash
# Install Ollama (see https://ollama.ai)
ollama serve
ollama pull llama2
```

## Configuration

1. Copy the example config:
```bash
cp config_local.py.example config_local.py
```

2. Update `config_local.py` with your settings:
```python
COURSE_NUM = 'CSPB-1300'  # Your course number
ASSIGNMENT_NAME = 'Lab2'   # Assignment name
```

## Directory Structure
```
~/Documents/CU Boulder/Grading/
├── CSPB-1300/
│   ├── Lab2/
│   │   ├── Student1_XXXXX_assignsubmission_file_/
│   │   │   └── submission.pdf
│   │   └── Student2_XXXXX_assignsubmission_file_/
│   │       └── submission.pdf
│   ├── Rubrics/
│   │   └── Lab2_Rubric.md
│   └── Reports/
│       └── CSPB-1300_grades_20240220_143022.csv
```

## Usage

1. Place student submissions in the appropriate directory:
   - Path: `~/Documents/CU Boulder/Grading/[COURSE_NUM]/[ASSIGNMENT_NAME]/`
   - Format: `[Student Name]_[ID]_assignsubmission_file_/submission.pdf`

2. Create your rubric:
   - Path: `~/Documents/CU Boulder/Grading/[COURSE_NUM]/Rubrics/[ASSIGNMENT_NAME]_Rubric.md`

3. Run the grader:
```bash
python llm_grader.py
```

## Output
- Grades and feedback are saved to a CSV file
- Default location: `~/Documents/CU Boulder/Grading/[COURSE_NUM]/[ASSIGNMENT_NAME]/grades/`
- Format: `[COURSE_NUM]_[ASSIGNMENT_NAME]_grades.csv`

## Dependencies
- langchain==0.1.9
- langchain-core==0.1.22
- langchain-community==0.0.24
- langchain-ollama==0.0.3
- pandas==2.2.1
- PyPDF2==3.0.1
- pydantic==2.6.1
- ollama==0.1.6

## Contributing
Feel free to submit issues and pull requests.

## License
MIT License