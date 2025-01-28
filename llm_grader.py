from typing import Dict
import ollama
import PyPDF2

class LLMGrader:
    def __init__(self, model_name: str = "llama2:3.2"):
        """Initialize the LLM grader"""
        self.ollama_client = ollama.Client()
        self.model_name = model_name

    def create_grading_prompt(self, rubric_text: str, submission_text: str) -> str:
        """Create the prompt for the LLM"""
        return f"""
        Please grade this student submission according to the following rubric:
        
        Rubric:
        {rubric_text}
        
        Student Submission:
        {submission_text}
        
        Please provide your response in the following format:
        Grade: [numerical grade out of 100]
        Feedback: [detailed feedback explaining the grade]
        """

    def extract_grade_and_feedback(self, response_text: str) -> Dict:
        """Extract grade and feedback from LLM response"""
        import re
        
        # Extract grade
        grade_match = re.search(r'Grade:\s*(\d{1,3})', response_text)
        grade = int(grade_match.group(1)) if grade_match else 0
        
        # Extract feedback
        feedback_match = re.search(r'Feedback:(.*)', response_text, re.DOTALL)
        feedback = feedback_match.group(1).strip() if feedback_match else response_text
        
        return {
            'grade': grade,
            'feedback': feedback
        }

    def grade_submission(self, rubric_text: str, submission_text: str) -> Dict:
        """Grade a submission using the LLM"""
        prompt = self.create_grading_prompt(rubric_text, submission_text)
        
        response = self.ollama_client.generate(
            model=self.model_name,
            prompt=prompt,
            max_tokens=1000
        )
        
        return self.extract_grade_and_feedback(response.text) 