import pdfplumber
import docx
import re
import spacy
from typing import Dict, List, Optional
from pathlib import Path
import json


class ResumeParser:
    """Parse resumes and extract key information"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract information"""
        # Convert to Path for OS-agnostic operations
        path = Path(file_path)
        
        # Extract text based on file extension
        suffix = path.suffix.lower()
        if suffix == '.pdf':
            text = self._extract_pdf_text(str(path))
        elif suffix == '.docx':
            text = self._extract_docx_text(str(path))
        elif suffix == '.txt':
            # Use newline='' for consistent line ending handling across OS
            with open(path, 'r', encoding='utf-8', newline='') as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file format")
        
        # Parse information
        parsed_data = {
            "raw_text": text,
            "skills": self._extract_skills(text),
            "experience_years": self._extract_experience_years(text),
            "education": self._extract_education(text),
            "projects": self._extract_projects(text),
            "contact": self._extract_contact(text),
            "certifications": self._extract_certifications(text),
            "raw_data": {"full_text": text}
        }
        
        return parsed_data
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        # Common technical skills
        skill_keywords = [
            'python', 'java', 'javascript', 'c\\+\\+', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
            'html', 'css', 'rest api', 'graphql', 'microservices',
            'agile', 'scrum', 'jira', 'ci/cd', 'devops',
            'data analysis', 'pandas', 'numpy', 'scikit-learn', 'tableau', 'power bi'
        ]
        
        skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            pattern = r'\b' + skill.replace('+', r'\+').replace('.', r'\.') + r'\b'
            if re.search(pattern, text_lower):
                skills.append(skill.replace('\\+', '+').replace(r'\.', '.'))
        
        # Extract from skills section
        skills_section = re.search(r'skills?:?(.*?)(?=\n\n|\n[A-Z]|\Z)', text, re.IGNORECASE | re.DOTALL)
        if skills_section:
            section_text = skills_section.group(1)
            # Extract words that might be skills
            potential_skills = re.findall(r'\b[A-Za-z][A-Za-z0-9+#\.]*\b', section_text)
            skills.extend([s for s in potential_skills if len(s) > 2 and s.lower() not in ['and', 'the', 'with', 'for']])
        
        return list(set(skills))[:20]  # Return unique skills, max 20
    
    def _extract_experience_years(self, text: str) -> Optional[float]:
        """Extract years of experience"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Look for patterns like "5 years", "3+ years", "2-3 years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*\d+\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, TypeError):
                    pass
        
        # Count work experience entries
        work_section = re.search(r'(?:work\s+)?experience:?(.*?)(?=education|projects|skills|\Z)', 
                                text, re.IGNORECASE | re.DOTALL)
        if work_section:
            # Count date ranges
            date_ranges = re.findall(r'(?:19|20)\d{2}\s*-\s*(?:(?:19|20)\d{2}|present|current)', 
                                    work_section.group(1), re.IGNORECASE)
            if date_ranges:
                total_years = 0
                for date_range in date_ranges:
                    years = re.findall(r'(?:19|20)\d{2}', date_range)
                    if len(years) == 2:
                        total_years += int(years[1]) - int(years[0])
                    elif 'present' in date_range.lower() or 'current' in date_range.lower():
                        total_years += current_year - int(years[0])
                return float(total_years) if total_years > 0 else None
        
        return None
    
    def _extract_education(self, text: str) -> Dict:
        """Extract education information"""
        education = {
            "degrees": [],
            "institutions": [],
            "fields": []
        }
        
        # Find education section
        edu_section = re.search(r'education:?(.*?)(?=experience|projects|skills|\Z)', 
                               text, re.IGNORECASE | re.DOTALL)
        
        if edu_section:
            section_text = edu_section.group(1)
            
            # Extract degrees
            degrees = ['ph\.?d', 'doctor', 'master', 'm\.?s\.?', 'm\.?tech', 'bachelor', 'b\.?s\.?', 'b\.?tech', 'b\.?e\.?', 'diploma']
            for degree in degrees:
                if re.search(degree, section_text, re.IGNORECASE):
                    education["degrees"].append(degree.replace(r'\.?', '.'))
            
            # Extract years
            years = re.findall(r'(?:19|20)\d{2}', section_text)
            if years:
                education["years"] = years
            
            # Extract institutions (capitalized words, likely names)
            institutions = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s+(?:University|Institute|College|School))?', section_text)
            education["institutions"] = institutions[:3]
        
        return education
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Find projects section
        proj_section = re.search(r'projects?:?(.*?)(?=experience|education|skills|\Z)', 
                                text, re.IGNORECASE | re.DOTALL)
        
        if proj_section:
            section_text = proj_section.group(1)
            
            # Split by bullet points or numbers
            project_items = re.split(r'\n\s*[•\-\*\d]+\.?\s+', section_text)
            
            for item in project_items[:5]:  # Max 5 projects
                if len(item.strip()) > 20:
                    # Extract first line as title
                    lines = item.strip().split('\n')
                    title = lines[0][:100] if lines else item[:100]
                    
                    projects.append({
                        "title": title.strip(),
                        "description": item.strip()[:300]
                    })
        
        return projects
    
    def _extract_contact(self, text: str) -> Dict:
        """Extract contact information"""
        contact = {}
        
        # Email
        email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email:
            contact["email"] = email.group(0)
        
        # Phone
        phone = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone:
            contact["phone"] = phone.group(0)
        
        # LinkedIn
        linkedin = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin:
            contact["linkedin"] = linkedin.group(0)
        
        # GitHub
        github = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github:
            contact["github"] = github.group(0)
        
        return contact
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        cert_section = re.search(r'certifications?:?(.*?)(?=\n\n|\n[A-Z][a-z]+:|\Z)', 
                                text, re.IGNORECASE | re.DOTALL)
        
        if cert_section:
            section_text = cert_section.group(1)
            # Split by bullet points or lines
            cert_items = re.split(r'\n\s*[•\-\*]?\s*', section_text)
            certifications = [c.strip() for c in cert_items if len(c.strip()) > 5][:10]
        
        return certifications
