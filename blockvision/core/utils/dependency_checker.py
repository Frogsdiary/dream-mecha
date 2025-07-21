"""
Dependency Checker - BlockVision Core
Checks for required dependencies and provides helpful error messages
"""

import sys
from typing import Dict, List, Tuple


class DependencyChecker:
    """Checks for required dependencies"""
    
    def __init__(self):
        self.required_packages = {
            'PIL': 'Pillow',
            'numpy': 'numpy',
            'PyQt5': 'PyQt5'
        }
        
        self.optional_packages = {
            'cv2': 'opencv-python',
            'pyopengl': 'PyOpenGL'
        }
    
    def check_dependencies(self) -> Tuple[bool, List[str], List[str]]:
        """Check all dependencies and return status"""
        missing_required = []
        missing_optional = []
        
        # Check required packages
        for package, pip_name in self.required_packages.items():
            if not self._is_package_available(package):
                missing_required.append(pip_name)
        
        # Check optional packages
        for package, pip_name in self.optional_packages.items():
            if not self._is_package_available(package):
                missing_optional.append(pip_name)
        
        all_required_available = len(missing_required) == 0
        return all_required_available, missing_required, missing_optional
    
    def _is_package_available(self, package_name: str) -> bool:
        """Check if a package is available"""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
    
    def get_installation_instructions(self, missing_packages: List[str]) -> str:
        """Get installation instructions for missing packages"""
        if not missing_packages:
            return "All dependencies are available."
        
        instructions = "Missing packages. Install with:\n"
        instructions += "pip install " + " ".join(missing_packages)
        return instructions
    
    def check_image_loader_dependencies(self) -> bool:
        """Check if image loader dependencies are available"""
        try:
            from PIL import Image, ImageOps
            import numpy as np
            return True
        except ImportError as e:
            print(f"Image loader dependencies missing: {e}")
            return False


# Global dependency checker instance
_dependency_checker = None


def get_dependency_checker() -> DependencyChecker:
    """Get the global dependency checker instance"""
    global _dependency_checker
    if _dependency_checker is None:
        _dependency_checker = DependencyChecker()
    return _dependency_checker


def check_blockvision_dependencies() -> bool:
    """Check if BlockVision can run with current dependencies"""
    checker = get_dependency_checker()
    available, missing_required, missing_optional = checker.check_dependencies()
    
    if not available:
        print("❌ BlockVision dependencies missing:")
        print(checker.get_installation_instructions(missing_required))
        return False
    
    if missing_optional:
        print("⚠️  Optional dependencies missing (some features may not work):")
        print(checker.get_installation_instructions(missing_optional))
    
    return True 