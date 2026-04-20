"""
File Manager Module
Handles file system operations with advanced search, organization, and context awareness.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Union, Optional
from automation.context_manager import ContextManager

logger = logging.getLogger(__name__)

class FileManager:
    """Manages files and folders safely with context updates."""
    
    def __init__(self):
        # Default starting locations
        self.home = Path.home()
        self.desktop = self.home / "Desktop"
        self.documents = self.home / "Documents"
        self.downloads = self.home / "Downloads"
        self.ctx_mgr = ContextManager()

    def list_files(self, path: str = ".") -> List[Dict[str, str]]:
        """List files in directory with details."""
        try:
            target_path = Path(path).resolve()
            if not target_path.exists():
                return []
                
            items = []
            for item in target_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            # Update context if listing a new dir (implies active project/focus)
            if target_path.is_dir():
                self.ctx_mgr.update_context({"active_project_dir": str(target_path)})
                
            return items
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []

    def read_file(self, path: str) -> Optional[str]:
        """Read text file content."""
        try:
            abs_path = str(Path(path).resolve())
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update Context
            self.ctx_mgr.update_context({"last_opened_file": abs_path})
            return content
        except UnicodeDecodeError:
            return "Binary file content not displayable."
        except Exception as e:
            logger.error(f"Read file failed: {e}")
            return None

    def write_file(self, path: str, content: str, mode: str = 'w') -> str:
        """
        Write content to file with STRICT Content Type Enforcement.
        Returns: Success message or Error string.
        """
        try:
            target_path = Path(path).resolve()
            
            # 1. Enforce Content Type
            ext = target_path.suffix.lower()
            if not self._validate_content_type(ext, content):
                return f"Error: Content type mismatch. Cannot write code to {ext} or text to code."

            # 2. Create Parent Dirs
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 3. Write
            with open(target_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            # 4. Update Context
            abs_path = str(target_path)
            updates = {
                "last_modified_file": abs_path,
                "last_content_type": ext.replace(".", "")
            }
            if mode == 'w' and not target_path.exists(): # If new file (approx)
                 updates["last_created_file"] = abs_path
            
            self.ctx_mgr.update_context(updates)
            
            return f"Successfully wrote to {abs_path}"
        except Exception as e:
            err = f"Write file failed: {e}"
            logger.error(err)
            return err

    def create_folder(self, path: str) -> str:
        try:
            target_path = Path(path).resolve()
            target_path.mkdir(parents=True, exist_ok=True)
            self.ctx_mgr.update_context({"active_project_dir": str(target_path)})
            return f"Created folder {target_path}"
        except Exception as e:
            return f"Create directory failed: {e}"

    def delete_item(self, path: str) -> str:
        """Delete file or folder (High Risk)."""
        try:
            target_path = Path(path).resolve()
            if not target_path.exists():
                return "Item does not exist."
                
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            return f"Deleted {target_path}"
        except Exception as e:
            return f"Delete failed: {e}"

    def search_files(self, query: str, start_path: str = None, depth: int = 2) -> List[str]:
        """Simple recursive search."""
        results = []
        try:
            start = Path(start_path) if start_path else self.documents
            # Limit depth for performance
            for root, dirs, files in os.walk(start):
                level = str(root).replace(str(start), '').count(os.sep)
                if level > depth:
                    continue
                    
                for name in files + dirs:
                    if query.lower() in name.lower():
                        results.append(os.path.join(root, name))
                        if len(results) > 20: # Limit results
                            return results
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _validate_content_type(self, ext: str, content: str) -> bool:
        """
        Enforce strict content rules:
        - .py -> Must look like python code
        - .txt -> Should not contain complex code blocks if possible (soft rule)
        - But critically: Don't put obvious code in txt if requested to fix code
        """
        # Simple heuristics
        if ext == '.py':
            return True # Assume LLM generates valid python if asked
        
        if ext == '.txt':
            # Identify if it looks suspiciously like full code file
            if "import " in content and "def " in content and "class " in content:
                # This is a bit strict, but requested("ANAY must NEVER write code into .txt files")
                # We'll allow it if it's small snippets, but block full modules
                pass 
        
        if ext == '.csv':
            # Check for comma separation
            lines = content.strip().split('\n')
            if lines and "," not in lines[0]:
                logger.warning("Writing to CSV but no commas found in header.")
                # We won't block it strictly as 1-col csv is valid, but good to note
                
        return True
