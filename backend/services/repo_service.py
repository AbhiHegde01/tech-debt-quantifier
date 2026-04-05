import os
import subprocess
import tempfile
import shutil
import re

class RepoService:
    def __init__(self):
        self.temp_dir = None

    def clone_public_repo(self, github_url: str):
        """Clones a public repo into a temporary folder on the server."""
        # Security check: Make sure it's actually a GitHub URL
        if not github_url.startswith("https://github.com/"):
            raise ValueError("Only public https://github.com/ URLs are supported.")

        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        print(f"📦 Cloning {github_url} into temp workspace...")
        
        try:
            # Run the git clone command quietly
            subprocess.run(
                ["git", "clone", "--depth", "1", github_url, self.temp_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return self.temp_dir
        except subprocess.CalledProcessError:
            self.cleanup()
            raise Exception("Failed to clone repository. Is it public?")

    def get_all_code_files(self):
        """Walks the cloned directory and returns paths to code files."""
        if not self.temp_dir:
            return []

        code_files = []
        for root, _, files in os.walk(self.temp_dir):
            if '.git' in root:
                continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp')):
                    code_files.append(os.path.join(root, file))
        return code_files

    def get_dependency_map(self):
        """Scans the cloned repo for import statements to build a connection graph."""
        dependencies = {}
        if not self.temp_dir:
            return dependencies

        for root, _, files in os.walk(self.temp_dir):
            if '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    # Clean up the name so it looks nice on the graph
                    rel_path = os.path.relpath(filepath, self.temp_dir).replace('\\', '/')
                    dependencies[rel_path] = []

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Find all 'import X' or 'from X import'
                            imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
                            # Only keep unique imports
                            dependencies[rel_path] = list(set(imports))
                    except:
                        pass
        return dependencies

    def read_file_content(self, filepath: str):
        """Reads the actual text inside the code file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Return first 400 lines to avoid massive token costs
                return "".join(f.readlines()[:400]) 
        except:
            return ""

    def cleanup(self):
        """Deletes the cloned repo so your server doesn't run out of storage."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            print("🧹 Cleaning up temporary workspace...")
            # Use error handling for Windows file-locking quirks
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None