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
        """Extract skills from text with comprehensive skill detection"""
        
        # Comprehensive technical skills database
        skill_keywords = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'ruby', 'php', 
            'swift', 'kotlin', 'go', 'golang', 'rust', 'scala', 'perl', 'r', 'matlab',
            'objective-c', 'dart', 'lua', 'haskell', 'clojure', 'elixir', 'erlang',
            'groovy', 'vb.net', 'visual basic', 'cobol', 'fortran', 'assembly',
            
            # Web Frontend
            'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'tailwind', 'tailwindcss',
            'bootstrap', 'material ui', 'materialui', 'mui', 'chakra ui', 'ant design',
            'react', 'reactjs', 'react.js', 'redux', 'next.js', 'nextjs', 'gatsby',
            'angular', 'angularjs', 'vue', 'vuejs', 'vue.js', 'vuex', 'nuxt', 'nuxtjs',
            'svelte', 'ember', 'backbone', 'jquery', 'ajax', 'webpack', 'vite', 'parcel',
            'babel', 'eslint', 'prettier', 'npm', 'yarn', 'pnpm',
            
            # Web Backend
            'node.js', 'nodejs', 'node', 'express', 'expressjs', 'express.js', 'nestjs', 'fastify',
            'django', 'flask', 'fastapi', 'pyramid', 'tornado', 'bottle',
            'spring', 'spring boot', 'springboot', 'hibernate', 'maven', 'gradle',
            'rails', 'ruby on rails', 'sinatra',
            'laravel', 'symfony', 'codeigniter', 'yii',
            'asp.net', '.net', '.net core', 'dotnet', 'blazor',
            'gin', 'echo', 'fiber', 'beego',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'sql server', 'mssql',
            'mariadb', 'db2', 'teradata', 'snowflake', 'redshift',
            'mongodb', 'mongoose', 'couchdb', 'cassandra', 'dynamodb', 'firebase',
            'redis', 'memcached', 'elasticsearch', 'solr', 'neo4j', 'graphdb', 'arangodb',
            'influxdb', 'timescaledb', 'clickhouse',
            
            # Cloud & DevOps
            'aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds', 'cloudfront', 'sqs', 'sns',
            'azure', 'microsoft azure', 'azure devops',
            'gcp', 'google cloud', 'google cloud platform', 'bigquery', 'cloud functions',
            'heroku', 'digitalocean', 'linode', 'vercel', 'netlify', 'railway',
            'docker', 'kubernetes', 'k8s', 'openshift', 'rancher', 'helm',
            'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'packer',
            'jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis ci', 'bamboo',
            'ci/cd', 'cicd', 'continuous integration', 'continuous deployment',
            'nginx', 'apache', 'tomcat', 'iis', 'caddy',
            
            # Data Science & ML
            'machine learning', 'ml', 'deep learning', 'dl', 'artificial intelligence', 'ai',
            'neural networks', 'cnn', 'rnn', 'lstm', 'transformer', 'bert', 'gpt',
            'tensorflow', 'keras', 'pytorch', 'torch', 'caffe', 'mxnet', 'theano',
            'scikit-learn', 'sklearn', 'scipy', 'numpy', 'pandas', 'matplotlib', 'seaborn',
            'nltk', 'spacy', 'huggingface', 'transformers', 'opencv', 'cv2',
            'jupyter', 'jupyter notebook', 'colab', 'kaggle',
            'data science', 'data analysis', 'data analytics', 'data engineering',
            'data mining', 'data visualization', 'statistics', 'statistical analysis',
            'regression', 'classification', 'clustering', 'nlp', 'natural language processing',
            'computer vision', 'image processing', 'speech recognition',
            'mlops', 'mlflow', 'kubeflow', 'airflow', 'dvc',
            
            # Big Data
            'hadoop', 'hdfs', 'mapreduce', 'spark', 'pyspark', 'apache spark',
            'hive', 'pig', 'kafka', 'apache kafka', 'flink', 'storm', 'presto',
            'databricks', 'dbt', 'etl', 'data pipeline', 'data warehouse',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'ionic',
            'swiftui', 'uikit', 'jetpack compose', 'android studio', 'xcode',
            
            # APIs & Protocols
            'rest', 'rest api', 'restful', 'graphql', 'grpc', 'soap', 'websocket', 'websockets',
            'json', 'xml', 'yaml', 'protobuf', 'api design', 'openapi', 'swagger',
            'oauth', 'oauth2', 'jwt', 'saml', 'sso',
            
            # Version Control
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
            
            # Testing
            'unit testing', 'integration testing', 'e2e testing', 'tdd', 'bdd',
            'jest', 'mocha', 'chai', 'jasmine', 'cypress', 'selenium', 'playwright',
            'pytest', 'unittest', 'nose', 'robot framework',
            'junit', 'testng', 'mockito', 'powermock',
            'postman', 'insomnia', 'soapui',
            
            # Project Management & Methodologies
            'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'xp',
            'jira', 'confluence', 'trello', 'asana', 'monday', 'notion',
            
            # BI & Visualization
            'tableau', 'power bi', 'powerbi', 'looker', 'metabase', 'grafana',
            'excel', 'google sheets', 'qlik', 'sisense',
            'd3.js', 'd3', 'chart.js', 'plotly', 'highcharts',
            
            # Design & UX
            'figma', 'sketch', 'adobe xd', 'invision', 'zeplin',
            'photoshop', 'illustrator', 'ui/ux', 'ui design', 'ux design',
            'wireframing', 'prototyping', 'user research',
            
            # Security
            'cybersecurity', 'security', 'penetration testing', 'ethical hacking',
            'owasp', 'encryption', 'ssl', 'tls', 'https', 'firewall',
            'vulnerability assessment', 'siem', 'soc',
            
            # Networking
            'networking', 'tcp/ip', 'http', 'dns', 'load balancing',
            'vpn', 'routing', 'switching', 'cisco', 'ccna', 'ccnp',
            
            # Operating Systems
            'linux', 'unix', 'ubuntu', 'centos', 'debian', 'redhat', 'rhel', 'fedora',
            'windows', 'windows server', 'macos', 'shell scripting', 'bash', 'powershell',
            
            # Soft Skills
            'leadership', 'communication', 'teamwork', 'problem solving', 'problem-solving',
            'critical thinking', 'analytical', 'time management', 'project management',
            'presentation', 'public speaking', 'mentoring', 'collaboration',
            
            # Computer Science Fundamentals
            'data structures', 'algorithms', 'oop', 'object oriented programming',
            'design patterns', 'solid principles', 'system design', 'software architecture',
            'microservices', 'distributed systems', 'concurrency', 'multithreading',
            'data modeling', 'database design', 'normalization',
            
            # IT Operations & Administration
            'system administration', 'database administration', 'dba', 'server administration',
            'network administration', 'it support', 'help desk', 'technical support',
            'active directory', 'ldap', 'vmware', 'virtualization', 'hyper-v',
            
            # Enterprise Tools & Platforms  
            'servicenow', 'salesforce', 'sap', 'oracle erp', 'workday', 'dynamics 365',
            'sharepoint', 'office 365', 'microsoft 365', 'gsuite', 'google workspace',
            
            # Storage & Backup
            'storage', 'san', 'nas', 'backup', 'disaster recovery', 'raid',
            
            # Blockchain & Emerging Tech
            'blockchain', 'ethereum', 'solidity', 'web3', 'smart contracts',
            'iot', 'internet of things', 'embedded systems', 'arduino', 'raspberry pi',
            
            # CRM & ERP
            'crm', 'erp', 'customer relationship management',
        }
        
        skills = set()
        text_lower = text.lower()
        
        # Method 1: Direct keyword matching from comprehensive list
        for skill in skill_keywords:
            # Escape special characters for regex
            escaped_skill = re.escape(skill)
            # Match whole words only
            pattern = r'(?<![a-zA-Z])' + escaped_skill + r'(?![a-zA-Z])'
            if re.search(pattern, text_lower):
                # Clean up skill name for display
                display_skill = skill.replace('.', '').title() if '.' not in skill else skill
                if skill in ['aws', 'gcp', 'sql', 'html', 'css', 'api', 'ci/cd', 'ai', 'ml', 'dl', 'ui/ux']:
                    display_skill = skill.upper()
                elif skill in ['javascript', 'typescript', 'python', 'java', 'react', 'angular', 'vue', 'django', 'flask', 'nodejs', 'docker', 'kubernetes']:
                    display_skill = skill.capitalize() if len(skill) > 3 else skill.title()
                skills.add(display_skill)
        
        # Method 2: Extract skills from dedicated skills section
        # Only add skills that match our known skills database to avoid garbage extraction
        skills_section_patterns = [
            r'(?:technical\s+)?skills?\s*[:|\-|–]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[:|\-]|experience|education|projects|certifications|$)',
            r'competenc(?:y|ies)\s*[:|\-|–]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[:|\-]|$)',
            r'technologies?\s*[:|\-|–]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[:|\-]|$)',
            r'tools?\s*(?:&|and)?\s*technologies?\s*[:|\-|–]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[:|\-]|$)',
        ]
        
        for pattern in skills_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section_text = match.group(1)
                # Re-check this section against our known skills database
                # This avoids adding arbitrary multi-word chunks as skills
                section_lower = section_text.lower()
                for skill in skill_keywords:
                    escaped_skill = re.escape(skill)
                    skill_pattern = r'(?<![a-zA-Z])' + escaped_skill + r'(?![a-zA-Z])'
                    if re.search(skill_pattern, section_lower):
                        display_skill = skill.replace('.', '').title() if '.' not in skill else skill
                        if skill in ['aws', 'gcp', 'sql', 'html', 'css', 'api', 'ci/cd', 'ai', 'ml', 'dl', 'ui/ux']:
                            display_skill = skill.upper()
                        elif skill in ['javascript', 'typescript', 'python', 'java', 'react', 'angular', 'vue', 'django', 'flask', 'nodejs', 'docker', 'kubernetes']:
                            display_skill = skill.capitalize() if len(skill) > 3 else skill.title()
                        skills.add(display_skill)
        
        # Method 3: Extract skills near keywords like "proficient in", "experience with"
        # Re-check matched text against known skills database
        context_patterns = [
            r'(?:proficient|experienced|skilled|expertise|knowledge|familiar)\s+(?:in|with)\s+([A-Za-z0-9+#,\s\-]+?)(?:\.|,\s*(?:and|including)|$)',
            r'(?:worked|working)\s+with\s+([A-Za-z0-9+#,\s\-]+?)(?:\.|,\s*(?:and|including)|$)',
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match_text in matches:
                match_lower = match_text.lower()
                # Only add skills that match our database
                for skill in skill_keywords:
                    escaped_skill = re.escape(skill)
                    skill_pattern = r'(?<![a-zA-Z])' + escaped_skill + r'(?![a-zA-Z])'
                    if re.search(skill_pattern, match_lower):
                        display_skill = skill.replace('.', '').title() if '.' not in skill else skill
                        if skill in ['aws', 'gcp', 'sql', 'html', 'css', 'api', 'ci/cd', 'ai', 'ml', 'dl', 'ui/ux']:
                            display_skill = skill.upper()
                        elif skill in ['javascript', 'typescript', 'python', 'java', 'react', 'angular', 'vue', 'django', 'flask', 'nodejs', 'docker', 'kubernetes']:
                            display_skill = skill.capitalize() if len(skill) > 3 else skill.title()
                        skills.add(display_skill)
        
        # Clean up and format skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            # Skip if too short or just numbers
            if len(skill) < 2 or skill.isdigit():
                continue
            cleaned_skills.append(skill)
        
        # Sort skills: programming languages first, then frameworks, then others
        priority_skills = ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'SQL', 'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Docker', 'Kubernetes', 'Git']
        
        def skill_priority(s):
            s_lower = s.lower()
            for i, ps in enumerate(priority_skills):
                if ps.lower() in s_lower:
                    return i
            return len(priority_skills)
        
        cleaned_skills = sorted(set(cleaned_skills), key=skill_priority)
        
        return cleaned_skills[:30]  # Return up to 30 unique skills
    
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
        """Extract education information - minimal extraction"""
        # Return empty dict as education details are not needed
        return {}
    
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
