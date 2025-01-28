# Moodle AutoGrader with LLM

An automated grading system that authenticates with CU Boulder's Moodle platform, downloads student submissions, and uses Ollama (LLM) to grade assignments based on provided rubrics.

## 🌟 Features

- Secure Moodle authentication with CU Boulder credentials
- Automatic PDF submission downloads
- LLM-powered grading using Ollama
- Structured grade reports in CSV format
- Secure configuration handling
- Detailed feedback generation

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Ollama installed and running
- CU Boulder Moodle access credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Like1Shot/AutoGrader_LLM.git
cd AutoGrader_LLM
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

### Configuration

1. Create your local configuration:
```bash
cp config.py config.local.py
```

2. Edit `config.local.py` with your credentials:
```python
MOODLE_CONFIG = {
    'base_url': 'https://applied.cs.colorado.edu',
    'credentials': {
        'username': 'your_identikey@colorado.edu',
        'password': 'your_password'
    }
}

ASSIGNMENT_CONFIG = {
    'url': 'your_assignment_url',
    'rubric_path': 'path_to_rubric.pdf',
    'output_dir': 'submissions'
}
```

## 📁 Project Structure

```
AutoGrader/
├── moodle_autograder.py   # Main application
├── llm_grader.py          # LLM grading logic
├── config.py              # Configuration template
├── config.local.py        # Local configuration (gitignored)
├── requirements.txt       # Dependencies
└── .gitignore            # Git ignore rules
```

## 🔧 Usage

1. Set up your configuration in `config.local.py`
2. Place your rubric PDF in the specified location
3. Run the autograder:
```bash
python moodle_autograder.py
```

### What it does:
1. Authenticates with CU Boulder Moodle
2. Downloads student PDF submissions
3. Processes each submission with Ollama
4. Generates a CSV report with grades and feedback

## 📊 Output

The system generates:
- Student submissions in your specified output directory
- `grading_results.csv` containing:
  - Student names
  - Numerical grades
  - Detailed feedback

## 🔒 Security Notes

- `config.local.py` is gitignored to protect credentials
- Use virtual environments for dependency isolation
- Keep your credentials secure
- Regularly update dependencies

## 📦 Dependencies

```
requests
beautifulsoup4
pandas
PyPDF2
ollama
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

[Your chosen license]

## ✨ Acknowledgments

- CU Boulder Applied Computer Science Department
- Ollama project contributors

## ⚠️ Disclaimer

This tool is intended for educational purposes. Always ensure you have appropriate permissions when accessing and processing student submissions.