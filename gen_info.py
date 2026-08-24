#!/usr/bin/env python3
"""
gen_info.py - Script for generating and writing system information to info.txt

Author: Senior Software Engineer
Date: 2026-08-24
Purpose: Create a clean, modular script that writes structured data to a text file.
"""

import os
from datetime import datetime


def get_system_info() -> dict:
    """
    Gather system information including current date/time and environment details.
    
    Returns:
        dict: Dictionary containing various system metrics and configurations.
    """
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "working_directory": os.getcwd(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.name,
        "cwd_exists": os.path.exists("./")
    }


def write_to_info_file(data: dict, filename: str = "info.txt") -> bool:
    """
    Write structured data to an info text file.
    
    Args:
        data (dict): Dictionary containing the information to write.
        filename (str): Name of the output file (default: "info.txt").
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# System Information Report\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
            
            f.write("=" * 60 + "\n")
            f.write("\n# End of Report\n")
        
        return True
    except IOError as e:
        print(f"Error writing to file: {e}")
        return False


def main():
    """Main execution function that generates and writes system info."""
    # Gather system information
    info = get_system_info()
    
    # Write to info.txt
    if write_to_info_file(info):
        print("✓ Successfully wrote information to info.txt")
        print(f"  Current timestamp: {info['timestamp']}")
        return True
    else:
        print("✗ Failed to write information to file")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
