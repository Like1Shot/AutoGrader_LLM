import requests
from bs4 import BeautifulSoup
import pandas as pd
import PyPDF2
import ollama
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

    def download_submissions(self, assignment_url: str, output_dir: str) -> List[str]:
        """
        Download all student PDF submissions from the given assignment URL
        
        Args:
            assignment_url: URL to the assignment submission page
            output_dir: Directory to save downloaded submissions
        
        Returns:
            List of paths to downloaded PDFs
        """
        if not self.authenticated:
            raise Exception("Not authenticated. Please authenticate first.")

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        downloaded_files = []

        try:
            response = self.session.get(assignment_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all submission links
            submission_links = soup.find_all('a', href=lambda x: x and 'submission' in x)
            
            for link in submission_links:
                file_url = link['href']
                student_name = link.get_text().strip()
                
                # Download PDF
                pdf_response = self.session.get(file_url)
                if pdf_response.ok:
                    file_path = os.path.join(output_dir, f"{student_name}.pdf")
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                    downloaded_files.append(file_path)

            return downloaded_files
        except Exception as e:
            print(f"Error downloading submissions: {str(e)}")
            return []

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

def main():
    # Initialize grader with configuration
    moodle_grader = MoodleAutoGrader(
        MOODLE_CONFIG['base_url'],
        MOODLE_CONFIG['credentials']
    )
    
    # Authenticate
    if not moodle_grader.authenticate():
        print("Authentication failed")
        return
    
    # Download submissions
    submissions = moodle_grader.download_submissions(
        ASSIGNMENT_CONFIG['url'],
        ASSIGNMENT_CONFIG['output_dir']
    )
    
    # Initialize assignment grader
    assignment_grader = AssignmentGrader(ASSIGNMENT_CONFIG['rubric_path'])
    
    # Grade submissions and collect results
    results = []
    for submission_path in submissions:
        student_name = Path(submission_path).stem
        grade_result = assignment_grader.grade_submission(submission_path)
        
        results.append({
            'Student Name': student_name,
            'Grade': grade_result['grade'],
            'Feedback': grade_result['feedback']
        })
    
    # Create and save results CSV
    df = pd.DataFrame(results)
    df.to_csv('grading_results.csv', index=False)
    print(f"Grading completed. Results saved to grading_results.csv")

if __name__ == "__main__":
    main() 