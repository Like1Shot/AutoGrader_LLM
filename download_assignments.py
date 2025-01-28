import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from config import MOODLE_CONFIG
import pandas as pd
from datetime import datetime
from typing import List, Dict, Union

# Define default base directory in Documents
DEFAULT_BASE_DIR = os.path.expanduser("~/Documents/CU Boulder/Grading")

class AssignmentDownloader:
    def __init__(self, base_url: str, credentials: dict, base_dir: str = DEFAULT_BASE_DIR):
        """Initialize the downloader with Moodle credentials"""
        print("\n🔧 Initializing Assignment Downloader...")
        self.base_url = base_url
        self.credentials = credentials
        self.base_dir = base_dir
        self.session = requests.Session()
        self.authenticated = False
        
        # Create base directory structure
        print(f"📁 Creating base directory: {self.base_dir}")
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        print("✅ Initialization complete")
        
    def authenticate(self) -> bool:
        """Authenticate with Moodle using CU Boulder SSO"""
        print("\n🔐 Attempting authentication with CU Boulder Moodle...")
        try:
            print("  → Accessing login page...")
            login_url = f"{self.base_url}/login/index.php"
            response = self.session.get(login_url)
            
            print("  → Looking for SSO form...")
            soup = BeautifulSoup(response.text, 'html.parser')
            sso_form = soup.find('a', {'title': 'Login with CU Boulder FedAuth'})
            
            if sso_form:
                print("  → Following SSO redirect...")
                sso_url = sso_form['href']
                print(f"  → SSO URL: {sso_url}")
                sso_response = self.session.get(sso_url)
                
                print("  → Finding login form...")
                sso_soup = BeautifulSoup(sso_response.text, 'html.parser')
                login_form = sso_soup.find('form')
                
                if login_form:
                    # Get the form action URL and make it absolute
                    form_url = login_form.get('action')
                    print(f"  → Form URL: {form_url}")
                    
                    if form_url.startswith('/'):
                        # Use CU Boulder's SSO domain
                        form_url = f"https://fedauth.colorado.edu{form_url}"
                    print(f"  → Final form URL: {form_url}")
                    
                    print("  → Preparing login data...")
                    login_data = {}
                    
                    # Get all form inputs
                    for input_field in login_form.find_all('input'):
                        name = input_field.get('name')
                        value = input_field.get('value', '')
                        if name:
                            login_data[name] = value
                    
                    # Update with credentials
                    login_data.update({
                        'username': self.credentials['username'],
                        'password': self.credentials['password'],
                        '_eventId_proceed': ''
                    })
                    
                    print(f"  → Form fields: {list(login_data.keys())}")
                    
                    print("  → Submitting credentials...")
                    auth_response = self.session.post(
                        form_url, 
                        data=login_data, 
                        allow_redirects=True,
                        headers={
                            'Referer': sso_url,
                            'Origin': 'https://fedauth.colorado.edu',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    )
                    
                    print(f"  → Response status: {auth_response.status_code}")
                    
                    # Follow SAML redirect chain
                    if auth_response.ok:
                        print("  → Following SAML redirect chain...")
                        # Make a request to Moodle to verify login
                        verify_response = self.session.get(self.base_url)
                        if "Log out" in verify_response.text:
                            print("✅ Authentication successful")
                            self.authenticated = True
                            return True
                        else:
                            print("❌ Authentication failed: Not logged in after redirect")
                    else:
                        print(f"❌ Authentication failed: Bad response ({auth_response.status_code})")
                    
                print("❌ Authentication failed: Could not complete SSO process")
                return False
            
            print("❌ Authentication failed: SSO form not found")
            return False
            
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False

    def download(self, urls: Union[str, List[str]], course_name: str = "Default Course") -> pd.DataFrame:
        """Download assignments from one or multiple URLs"""
        print(f"\n📥 Starting download process for {course_name}...")
        
        if not self.authenticated and not self.authenticate():
            raise Exception("Authentication failed")

        # Convert single URL to list
        if isinstance(urls, str):
            urls = [urls]
            print(f"  → Converting single URL to list")

        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_output_dir = os.path.join(course_name, timestamp)
        print(f"  → Created timestamp directory: {timestamp}")

        total_urls = len(urls)
        for i, url in enumerate(urls, 1):
            try:
                print(f"\n📋 Processing assignment {i}/{total_urls}")
                print(f"  URL: {url}")
                
                # Modify URL to access grading interface
                grading_url = f"{url}&action=grading"
                
                # Create directory for assignment
                assignment_name = url.split('id=')[-1].split('&')[0]
                output_dir = os.path.join(self.base_dir, base_output_dir, f"assignment_{assignment_name}")
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                print(f"  → Created directory: {output_dir}")

                # Get submission links
                print("  → Fetching submission links...")
                response = self.session.get(grading_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the table with submissions
                table = soup.find('table', {'class': 'generaltable'})
                if not table:
                    raise Exception("Could not find submissions table")
                
                # Get all rows
                rows = table.find_all('tr')[1:]  # Skip header row
                print(f"  → Found {len(rows)} submissions")
                
                # Process each row
                for j, row in enumerate(rows, 1):
                    try:
                        # Get student name from the row
                        name_cell = row.find('td', {'class': 'cell c1'})
                        if not name_cell:
                            continue
                        student_name = name_cell.get_text(strip=True)
                        
                        # Find file submission link
                        file_cell = row.find('td', {'class': 'cell c5'})  # File submissions column
                        if not file_cell:
                            print(f"      ⚠️ No file submission cell found for {student_name}")
                            continue
                            
                        file_link = file_cell.find('a')
                        if not file_link:
                            print(f"      ⚠️ No submission found for {student_name}")
                            continue
                            
                        file_url = file_link['href']
                        print(f"    [{j}/{len(rows)}] Downloading {student_name}'s submission...")
                        
                        # Download file
                        pdf_response = self.session.get(file_url)
                        if pdf_response.ok:
                            # Clean student name for filename
                            safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).strip()
                            file_path = os.path.join(output_dir, f"{safe_name}.pdf")
                            with open(file_path, 'wb') as f:
                                f.write(pdf_response.content)
                            results.append({
                                'Assignment': assignment_name,
                                'Student': student_name,
                                'File': file_path,
                                'Timestamp': timestamp,
                                'Status': 'Success'
                            })
                            print(f"      ✅ Downloaded successfully")
                        else:
                            print(f"      ❌ Download failed")
                            
                    except Exception as e:
                        print(f"      ❌ Error processing submission: {str(e)}")
                    
            except Exception as e:
                error_msg = f"Error downloading from {url}: {str(e)}"
                print(f"❌ {error_msg}")
                results.append({
                    'Assignment': assignment_name,
                    'Student': 'N/A',
                    'File': 'N/A',
                    'Timestamp': timestamp,
                    'Status': f'Failed: {str(e)}'
                })

        # Create and save results
        print("\n📊 Generating download report...")
        df = pd.DataFrame(results)
        log_file = os.path.join(self.base_dir, base_output_dir, "download_log.csv")
        df.to_csv(log_file, index=False)
        print(f"  → Saved log to: {log_file}")
        
        # Print summary
        successful = len(df[df['Status'] == 'Success'])
        failed = len(df[df['Status'].str.startswith('Failed')])
        
        print("\n📋 Download Summary")
        print("================")
        print(f"Total assignments attempted: {len(urls)}")
        print(f"Total files downloaded: {successful}")
        print(f"Failed downloads: {failed}")
        print(f"\n📁 Files location: {os.path.join(self.base_dir, course_name)}")
        print("📝 Details available in download_log.csv")
        
        return df

def main():
    print("\n🚀 Starting Moodle Assignment Downloader")
    print("======================================")
    
    try:
        print("📖 Loading configuration...")
        from assignment_urls import ASSIGNMENT_URLS, COURSE_NAME
        print(f"  → Course: {COURSE_NAME}")
        print(f"  → URLs to process: {len(ASSIGNMENT_URLS)}")
    except ImportError:
        print("❌ Error: No assignment_urls.py found. Please provide URLs directly.")
        return

    print("\n🔧 Setting up downloader...")
    downloader = AssignmentDownloader(
        MOODLE_CONFIG['base_url'],
        MOODLE_CONFIG['credentials']
    )
    
    try:
        downloader.download(ASSIGNMENT_URLS, COURSE_NAME)
        print("\n✨ Process completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during download process: {str(e)}")
        print("Process terminated.")

if __name__ == "__main__":
    main() 