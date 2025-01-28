import requests
from bs4 import BeautifulSoup
import pandas as pd
import PyPDF2
from pathlib import Path
import os
from typing import Dict, List
from config import MOODLE_CONFIG, ASSIGNMENT_CONFIG
from llm_grader import LLMGrader

class MoodleAutoGrader:
    def __init__(self, base_url: str, credentials: Dict[str, str]):
        """
        Initialize the autograder with Moodle credentials
        
        Args:
            base_url: The Moodle course URL
            credentials: Dict containing 'username' and 'password'
        """
        self.base_url = base_url
        self.credentials = credentials
        self.session = requests.Session()
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with Moodle using Google SSO"""
        try:
            # Start authentication process
            login_url = f"{self.base_url}/login/index.php"
            response = self.session.get(login_url)
            
            # Find Google SSO form and submit credentials
            soup = BeautifulSoup(response.text, 'html.parser')
            sso_form = soup.find('a', {'title': 'Login with CU Boulder FedAuth'})
            
            if sso_form:
                sso_url = sso_form['href']
                auth_response = self.session.post(sso_url, data=self.credentials)
                self.authenticated = auth_response.ok
                return self.authenticated
            return False
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

class AssignmentGrader:
    def __init__(self, rubric_path: str):
        """
        Initialize the grader with a rubric
        
        Args:
            rubric_path: Path to the rubric PDF file
        """
        self.rubric = self._load_rubric(rubric_path)
        self.llm_grader = LLMGrader()

    def _load_rubric(self, rubric_path: str) -> str:
        """Load and extract text from rubric PDF"""
        with open(rubric_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            rubric_text = ""
            for page in pdf_reader.pages:
                rubric_text += page.extract_text()
        return rubric_text

    def grade_submission(self, submission_path: str) -> Dict:
        """Grade a single submission"""
        # Extract text from submission
        with open(submission_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            submission_text = ""
            for page in pdf_reader.pages:
                submission_text += page.extract_text()

        # Use LLM grader to grade the submission
        return self.llm_grader.grade_submission(self.rubric, submission_text)

def grade_submissions(submissions_dir: str, rubric_path: str) -> pd.DataFrame:
    """
    Grade all submissions in a directory
    
    Args:
        submissions_dir: Directory containing PDF submissions
        rubric_path: Path to rubric PDF
    
    Returns:
        DataFrame with grading results
    """
    # Initialize grader
    assignment_grader = AssignmentGrader(rubric_path)
    
    # Grade submissions and collect results
    results = []
    for submission_path in Path(submissions_dir).glob('*.pdf'):
        student_name = submission_path.stem
        try:
            grade_result = assignment_grader.grade_submission(str(submission_path))
            results.append({
                'Student Name': student_name,
                'Grade': grade_result['grade'],
                'Feedback': grade_result['feedback'],
                'Status': 'Success'
            })
        except Exception as e:
            results.append({
                'Student Name': student_name,
                'Grade': 0,
                'Feedback': f'Error: {str(e)}',
                'Status': 'Failed'
            })
    
    return pd.DataFrame(results)

def main():
    # Grade submissions from a directory
    results_df = grade_submissions(
        ASSIGNMENT_CONFIG['output_dir'],
        ASSIGNMENT_CONFIG['rubric_path']
    )
    
    # Save results
    results_df.to_csv('grading_results.csv', index=False)
    print(f"Grading completed. Results saved to grading_results.csv")
    
    # Print summary
    print("\nGrading Summary:")
    print(f"Total submissions: {len(results_df)}")
    print(f"Successfully graded: {len(results_df[results_df['Status'] == 'Success'])}")
    print(f"Failed: {len(results_df[results_df['Status'] == 'Failed'])}")

if __name__ == "__main__":
    main() 