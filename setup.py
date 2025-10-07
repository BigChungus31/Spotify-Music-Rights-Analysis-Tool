"""
Setup Verification Script
Run this before executing main.py to ensure everything is configured correctly
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python version: {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required = ['requests', 'pandas', 'openpyxl']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print("\nTo install missing packages, run:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'dashboard.html',
        'unclaimedmusicalworkrightshares.tsv'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} found")
        else:
            print(f"✗ {filename} NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print("\nMissing files detected!")
        print("Make sure all required files are in the same directory.")
    
    return all_exist

def check_spotify_credentials():
    """Verify Spotify credentials are in main.py"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        if 'bec0b6e8f906412baea4aebf1dd977cb' in content:
            print("✓ Spotify Client ID found in main.py")
        else:
            print("✗ Spotify Client ID not found")
            return False
            
        if 'a809cde77b6b4d76b2ab577fe8f3fb25' in content:
            print("✓ Spotify Client Secret found in main.py")
        else:
            print("✗ Spotify Client Secret not found")
            return False
            
        return True
    except FileNotFoundError:
        print("✗ main.py not found")
        return False

def test_spotify_connection():
    """Test connection to Spotify API"""
    try:
        import requests
        
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': 'bec0b6e8f906412baea4aebf1dd977cb',
            'client_secret': 'a809cde77b6b4d76b2ab577fe8f3fb25',
        }, timeout=10)
        
        if auth_response.status_code == 200:
            print("✓ Spotify API connection successful")
            return True
        else:
            print(f"✗ Spotify API authentication failed (Status: {auth_response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Could not connect to Spotify API: {e}")
        return False

def check_dataset_structure():
    """Verify the TSV file can be loaded"""
    try:
        import pandas as pd
        
        # Read without header since the dataset doesn't have column names
        df = pd.read_csv('unclaimedmusicalworkrightshares.tsv', sep='\t', nrows=10, header=None)
        print(f"✓ Dataset loaded successfully ({len(df.columns)} columns, {len(df)} sample rows)")
        
        if len(df.columns) >= 4:
            print(f"✓ Dataset has expected structure (4+ columns)")
            # Check if column 3 (index 3) looks like ISRCs
            sample_isrcs = df[3].head(3).tolist()
            print(f"  Sample values from column 4 (ISRCs): {sample_isrcs}")
            
            # Validate ISRC format (2 letters + 3 alphanumeric + 7 digits)
            df['isrc_clean'] = df[3].astype(str).str.strip().str.upper()
            valid_count = df['isrc_clean'].str.match(r'^[A-Z]{2}[A-Z0-9]{3}\d{7}$').sum()
            if valid_count > 0:
                print(f"✓ Found {valid_count}/{len(df)} valid ISRC codes in sample")
                return True
            else:
                print(f"⚠ Warning: Column 4 values don't match standard ISRC format")
                return True  # Still return True as dataset is loadable
        else:
            print("⚠ Warning: Dataset has fewer than 4 columns")
            return False
    except FileNotFoundError:
        print("✗ Dataset file not found")
        return False
    except Exception as e:
        print(f"✗ Error reading dataset: {e}")
        return False

def main():
    print("=" * 60)
    print("SETUP VERIFICATION FOR SPOTIFY MUSIC RIGHTS ANALYZER")
    print("=" * 60)
    print()
    
    checks = {
        "Python Version": check_python_version(),
        "Required Packages": check_dependencies(),
        "Required Files": check_files(),
        "Spotify Credentials": check_spotify_credentials(),
        "Spotify API Connection": test_spotify_connection(),
        "Dataset Structure": check_dataset_structure()
    }
    
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:.<40} {status}")
    
    print()
    print(f"Score: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("ALL CHECKS PASSED!")
        print("You're ready to run: python main.py")
    else:
        print("SOME CHECKS FAILED")
        print("Please fix the issues above before running main.py")
        print("\nCommon fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Download the TSV file from Google Drive")
        print("  • Ensure all files are in the same directory")
    
    print("=" * 60)

if __name__ == "__main__":
    main()