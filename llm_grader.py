from typing import Dict, List
from pathlib import Path
import PyPDF2
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import pandas as pd
from operator import itemgetter
import os

# Define the expected output structure
class GradingResult(BaseModel):
    grade: float = Field(description="The numerical grade for the submission")
    feedback: str = Field(description="Detailed feedback explaining the grade")

class LLMGrader:
    GRADING_TEMPLATE = """
    Please grade this assignment according to the following rubric:
    {rubric_content}
    
    Student submission:
    {submission_content}
    
    Provide a grade out of 100 and detailed feedback.
    """

    def __init__(self, model_name: str = "llama2"):
        """Initialize the LLM grader with LangChain components"""
        self.llm = OllamaLLM(model=model_name)
        
        self.output_parser = PydanticOutputParser(pydantic_object=GradingResult)
        self.grading_chain = self._create_grading_chain()

    def _load_text(self, file_path: str) -> str:
        """Extract text from a file (PDF or Markdown)"""
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
        else:  # Handle markdown or text files
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        return text

    def grade_submission(self, rubric_text: str, submission_text: str) -> Dict:
        """Grade a single submission using LangChain"""
        try:
            result = self.grading_chain.invoke({
                "rubric_content": rubric_text,
                "submission_content": submission_text
            })
            
            # Parse the result
            try:
                parsed_result = self.output_parser.parse(result)
                return {
                    'grade': parsed_result.grade,
                    'feedback': parsed_result.feedback
                }
            except Exception as parse_error:
                # Fallback to basic parsing if structured parsing fails
                return self._basic_parse_result(result)
            
        except Exception as e:
            print(f"Error grading submission: {str(e)}")
            return {
                'grade': 0,
                'feedback': f"Error during grading: {str(e)}"
            }

    def _basic_parse_result(self, result: str) -> Dict:
        """Fallback parsing method for when structured parsing fails"""
        return {
            'grade': 0,
            'feedback': f"Failed to parse grading result: {result}"
        }

    def _create_grading_chain(self):
        """Create the LangChain grading chain"""
        prompt = PromptTemplate(
            template=self.GRADING_TEMPLATE,
            input_variables=["rubric_content", "submission_content"]
        )
        return prompt | self.llm | self.output_parser

def parse_student_name(directory_name):
    """Extract first and last name from directory name."""
    # Split at '_assignsubmission_file_'
    name_part = directory_name.split('_assignsubmission_file_')[0]
    # Split the name into parts
    name_parts = name_part.strip().split(' ')
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        # Get last name and remove ID number (everything after and including '_')
        last_name = ' '.join(name_parts[1:])  # Handle multi-word last names
        last_name = last_name.split('_')[0]  # Remove ID number
        return first_name, last_name
    return '', ''  # Return empty strings if parsing fails

def find_python_file(directory):
    """Find the first .py file in the directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                return os.path.join(root, file)
    return None

def read_directory_contents(directory):
    """Read all text files in a directory and combine their contents."""
    contents = []
    print(f"\nScanning directory: {directory}")
    print(f"Directory exists: {os.path.exists(directory)}")
    
    try:
        files_list = list(os.walk(directory))
        print(f"Files found in directory: {files_list}")
        
        for root, dirs, files in files_list:
            print(f"\nIn subdirectory: {root}")
            print(f"Found files: {files}")
            
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Checking file: {file_path}")
                
                try:
                    # Handle different file types
                    if file.endswith('.pdf'):
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = ''
                            for page in pdf_reader.pages:
                                text += page.extract_text() + '\n'
                            contents.append(text)
                            print(f"Successfully read PDF: {file_path}")
                    
                    elif file.endswith(('.py', '.cpp', '.txt', '.md', '.text')):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            contents.append(content)
                            print(f"Successfully read file: {file_path}")
                    
                    else:
                        print(f"Skipping file {file_path} - unsupported file type")
                        
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
    
    except Exception as e:
        print(f"Error walking directory {directory}: {str(e)}")
    
    if not contents:
        print(f"No readable content found in {directory}")
        return None
    
    return '\n\n'.join(contents)

def grade_assignments(submissions_dir, rubric_path, output_path):
    results = []
    
    print(f"\nStarting grading process")
    print(f"Submissions directory: {submissions_dir}")
    print(f"Rubric path: {rubric_path}")
    print(f"Output path: {output_path}")
    
    # Load rubric text
    with open(rubric_path, 'r') as f:
        rubric_text = f.read()
    
    # Initialize grader
    grader = LLMGrader()
    
    for submission_dir in os.listdir(submissions_dir):
        if '_assignsubmission_file_' in submission_dir:
            print(f"\nProcessing submission: {submission_dir}")
            first_name, last_name = parse_student_name(submission_dir)
            print(f"Student: {first_name} {last_name}")
            
            # Read all text contents from the submission directory
            full_submission_dir = os.path.join(submissions_dir, submission_dir)
            submission_text = read_directory_contents(full_submission_dir)
            
            if submission_text is None:
                grade_result = {
                    'grade': 0,
                    'feedback': f'No readable content found in submission directory: {full_submission_dir}'
                }
            else:
                try:
                    # Pass the text content directly to the grading method
                    grade_result = grader.grade_submission(rubric_text=rubric_text, submission_text=submission_text)
                except Exception as e:
                    print(f"Error during grading: {str(e)}")
                    grade_result = {
                        'grade': 0,
                        'feedback': f'Error during grading: {str(e)}'
                    }
            
            results.append({
                'First Name': first_name,
                'Last Name': last_name,
                'Grade': grade_result['grade'],
                'Feedback': grade_result['feedback']
            })
    
    print(f"\nSaving results to: {output_path}")
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return results

if __name__ == "__main__":
    from config_local import COURSE_CONFIG, GRADING_CONFIG, ASSIGNMENT_NAME
    
    # Use paths from config
    submissions_dir = COURSE_CONFIG['assignments_dir']
    rubric_path = GRADING_CONFIG['rubric_path']
    
    # Create output directory within the assignment folder
    output_dir = os.path.join(COURSE_CONFIG['assignments_dir'], 'grades')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{COURSE_CONFIG['number']}_{ASSIGNMENT_NAME}_grades.{GRADING_CONFIG['output_format']}")
    
    grade_assignments(submissions_dir, rubric_path, output_path) 