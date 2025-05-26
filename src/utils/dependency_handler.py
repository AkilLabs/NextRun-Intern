"""
This module handles the dynamic installation of dependencies that are not always needed
but might be required for specific agent capabilities.
"""
import importlib
import subprocess
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_package_installed(package_name):
    """Check if a package is already installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, version=None):
    """Install a package using pip"""
    try:
        package_spec = f"{package_name}{f'=={version}' if version else ''}"
        logger.info(f"Installing {package_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        logger.info(f"Successfully installed {package_spec}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {str(e)}")
        return False

def ensure_selenium_installed():
    """Ensure Selenium and webdriver-manager are installed"""
    packages = {
        "selenium": "4.10.0",
        "webdriver_manager": "3.8.6"
    }
    
    all_installed = True
    for package, version in packages.items():
        if not is_package_installed(package):
            success = install_package(package, version)
            all_installed = all_installed and success
    
    return all_installed

def ensure_test_libraries_installed():
    """Ensure all testing libraries are installed"""
    packages = {
        "selenium": "4.10.0",
        "webdriver_manager": "3.8.6",
        "pytest": "8.0.0",
        "pytest-html": "4.1.1"
    }
    
    all_installed = True
    for package, version in packages.items():
        if not is_package_installed(package):
            success = install_package(package, version)
            all_installed = all_installed and success
    
    return all_installed
