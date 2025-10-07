#!/usr/bin/env python3
"""
Comprehensive project validation script
Checks for errors, inconsistencies, and best practices
"""
import os
import sys
import ast
import json
from pathlib import Path

# Try to import yaml, but don't fail if it's not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class ProjectValidator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        
    def add_error(self, message, file=None, line=None):
        """Add an error message"""
        error = f"ERROR: {message}"
        if file:
            error += f" (in {file}"
            if line:
                error += f" at line {line}"
            error += ")"
        self.errors.append(error)
        
    def add_warning(self, message, file=None, line=None):
        """Add a warning message"""
        warning = f"WARNING: {message}"
        if file:
            warning += f" (in {file}"
            if line:
                warning += f" at line {line}"
            warning += ")"
        self.warnings.append(warning)
    
    def check_python_syntax(self):
        """Check Python files for syntax errors"""
        print("Checking Python syntax...")
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the AST to check for syntax errors
                ast.parse(content, filename=str(py_file))
                
            except SyntaxError as e:
                self.add_error(f"Syntax error in {py_file.name}: {e.msg}", 
                              file=py_file.name, line=e.lineno)
            except Exception as e:
                self.add_error(f"Error parsing {py_file.name}: {str(e)}", 
                              file=py_file.name)
    
    def check_imports(self):
        """Check for import issues"""
        print("Checking imports...")
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(alias.name, py_file.name, node.lineno)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_import(node.module, py_file.name, node.lineno)
                            
            except Exception as e:
                self.add_error(f"Error checking imports in {py_file.name}: {str(e)}")
    
    def _check_import(self, module_name, file_name, line_no):
        """Check if an import is problematic"""
        # Known problematic imports
        problematic_imports = {
            'eval': "Use of eval() is dangerous - use json.loads() or ast.literal_eval()",
            'exec': "Use of exec() is dangerous",
            'pickle': "Pickle can be unsafe - consider using json or safer alternatives"
        }
        
        if module_name in problematic_imports:
            self.add_warning(problematic_imports[module_name], file=file_name, line=line_no)
    
    def check_docker_files(self):
        """Check Docker configuration files"""
        print("Checking Docker files...")
        
        # Check Dockerfile
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            self._check_dockerfile(dockerfile)
        else:
            self.add_error("Dockerfile not found")
        
        # Check docker-compose.yml
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            self._check_docker_compose(compose_file)
        else:
            self.add_error("docker-compose.yml not found")
    
    def _check_dockerfile(self, dockerfile):
        """Check Dockerfile for issues"""
        try:
            with open(dockerfile, 'r') as f:
                lines = f.readlines()
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for running as root
                if line.startswith('USER root') or (line.startswith('RUN') and 'sudo' in line):
                    self.add_warning("Running as root user - consider using non-root user", 
                                   file="Dockerfile", line=i)
                
                # Check for hardcoded secrets
                if any(secret in line.lower() for secret in ['password', 'secret', 'token', 'key']):
                    if not any(env_var in line for env_var in ['ENV', 'ARG']):
                        self.add_warning("Potential hardcoded secret in Dockerfile", 
                                       file="Dockerfile", line=i)
                
                # Check for proper cleanup
                if line.startswith('RUN apt-get') and 'rm -rf /var/lib/apt/lists/*' not in line:
                    self.add_warning("apt-get install without cleanup - add 'rm -rf /var/lib/apt/lists/*'", 
                                   file="Dockerfile", line=i)
                    
        except Exception as e:
            self.add_error(f"Error reading Dockerfile: {str(e)}")
    
    def _check_docker_compose(self, compose_file):
        """Check docker-compose.yml for issues"""
        if not YAML_AVAILABLE:
            self.add_warning("PyYAML not available - skipping docker-compose.yml validation")
            return
            
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            # Check for version (deprecated but still common)
            if 'version' in compose_data:
                self.add_warning("Docker Compose version is deprecated - remove version field")
            
            # Check for proper service configuration
            if 'services' in compose_data:
                for service_name, service_config in compose_data['services'].items():
                    self._check_service_config(service_name, service_config)
                    
        except yaml.YAMLError as e:
            self.add_error(f"Invalid YAML in docker-compose.yml: {str(e)}")
        except Exception as e:
            self.add_error(f"Error reading docker-compose.yml: {str(e)}")
    
    def _check_service_config(self, service_name, config):
        """Check individual service configuration"""
        # Check for health checks
        if 'healthcheck' not in config:
            self.add_warning(f"Service '{service_name}' missing health check")
        
        # Check for restart policy
        if 'restart' not in config:
            self.add_warning(f"Service '{service_name}' missing restart policy")
        
        # Check for proper environment variable usage
        if 'environment' in config:
            for env_var in config['environment']:
                if isinstance(env_var, str) and '=' in env_var:
                    key, value = env_var.split('=', 1)
                    if value and not value.startswith('${'):
                        self.add_warning(f"Hardcoded value for {key} in {service_name}")
    
    def check_requirements(self):
        """Check requirements.txt for issues"""
        print("Checking requirements.txt...")
        
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.add_error("requirements.txt not found")
            return
        
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for version pinning
                if '==' not in line and '>=' not in line and '~=' not in line:
                    self.add_warning(f"Unpinned dependency: {line.split()[0]}", 
                                   file="requirements.txt", line=i)
                
                # Check for known problematic packages
                if 'caffe' in line.lower():
                    self.add_warning("Caffe can be difficult to install - ensure Docker setup is correct")
                    
        except Exception as e:
            self.add_error(f"Error reading requirements.txt: {str(e)}")
    
    def check_security(self):
        """Check for security issues"""
        print("Checking security...")
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for dangerous functions
                dangerous_patterns = [
                    ('eval(', 'Use of eval() is dangerous'),
                    ('exec(', 'Use of exec() is dangerous'),
                    ('pickle.loads', 'Pickle can be unsafe'),
                    ('subprocess.call', 'subprocess calls can be dangerous'),
                    ('os.system', 'os.system calls can be dangerous')
                ]
                
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for pattern, message in dangerous_patterns:
                        if pattern in line:
                            self.add_warning(f"{message} in {py_file.name}", 
                                           file=py_file.name, line=i)
                            
            except Exception as e:
                self.add_error(f"Error checking security in {py_file.name}: {str(e)}")
    
    def check_file_structure(self):
        """Check project file structure"""
        print("Checking file structure...")
        
        required_files = [
            'bot.py',
            'config.py', 
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        for file_name in required_files:
            if not (self.project_root / file_name).exists():
                self.add_error(f"Required file missing: {file_name}")
        
        # Check for .env file
        env_file = self.project_root / '.env'
        if not env_file.exists():
            self.add_warning("No .env file found - create one from env.docker template")
    
    def run_all_checks(self):
        """Run all validation checks"""
        print("Starting project validation...")
        print("=" * 60)
        
        self.check_file_structure()
        self.check_python_syntax()
        self.check_imports()
        self.check_docker_files()
        self.check_requirements()
        self.check_security()
        
        # Print results
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\nAll checks passed! Your project looks good!")
            return True
        elif not self.errors:
            print(f"\nNo errors found, but {len(self.warnings)} warnings to review")
            return True
        else:
            print(f"\nFound {len(self.errors)} errors and {len(self.warnings)} warnings")
            return False

def main():
    """Main function"""
    validator = ProjectValidator()
    success = validator.run_all_checks()
    
    if success:
        print("\nProject validation completed successfully!")
        return 0
    else:
        print("\nProject validation found issues that need to be fixed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
