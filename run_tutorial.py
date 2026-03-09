#!/usr/bin/env python
"""
Tutorial Launcher for CMIS3234 Shader Programming

This script provides an easy menu to run any of the shader tutorials.
"""

import sys
import os
import subprocess

def print_header():
    """Print the header"""
    print("\n" + "="*70)
    print(" "*15 + "CMIS3234 - Shader Programming Tutorials")
    print("="*70 + "\n")

def print_menu():
    """Print the tutorial menu"""
    print("Available Tutorials:")
    print("-" * 70)
    print("  0. Verify Environment - Check if everything is installed correctly")
    print("  1. Shader Introduction - Basic geometry and shaders")
    print("  2. Colored Geometry - Vertex attributes and interpolation")
    print("-" * 70)
    print("  Q. Quit")
    print()

def get_python_executable():
    """Get the correct Python executable (prefer venv if available)"""
    venv_python = os.path.join("shader_tutorial_venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

def run_tutorial(script_name):
    """Run a tutorial script"""
    if not os.path.exists(script_name):
        print(f"\n❌ Error: {script_name} not found!")
        return False
    
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70 + "\n")
    
    python_exe = get_python_executable()
    try:
        # Run the tutorial
        result = subprocess.run([python_exe, script_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tutorial exited with error code: {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Tutorial interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error running tutorial: {e}")
        return False

def show_tutorial_info(tutorial_num):
    """Show information about a tutorial"""
    info = {
        0: {
            "name": "Environment Verification",
            "description": "Checks if all required packages are installed and OpenGL is supported",
            "concepts": ["Python packages", "OpenGL support", "Hardware capabilities"],
            "script": "verify_environment.py"
        },
        1: {
            "name": "Shader Introduction",
            "description": "Basic vertex and fragment shaders with solid green geometry",
            "concepts": ["Vertex shaders", "Fragment shaders", "VBOs", "Basic rendering"],
            "script": "shader_intro.py"
        },
        2: {
            "name": "Colored Geometry",
            "description": "Vertex attributes and automatic color interpolation",
            "concepts": ["Vertex attributes", "Varying variables", "Interpolation", "Color gradients"],
            "script": "shader_colors.py"
        }
    }
    
    if tutorial_num in info:
        t = info[tutorial_num]
        print(f"\n📚 {t['name']}")
        print("-" * 70)
        print(f"Description: {t['description']}")
        print(f"\nKey Concepts:")
        for concept in t['concepts']:
            print(f"  • {concept}")
        print("-" * 70)
        return t['script']
    return None

def main():
    """Main program loop"""
    print_header()
    
    # Check if we're in the right directory
    if not os.path.exists("README_Shader_Tutorial.md"):
        print("⚠️  Warning: Please run this script from the 'computer graphics' directory")
        print("   Expected location: E:\\Z_PROJECTS\\presentaion creation\\computer graphics\\")
        print()
    
    # Check for virtual environment
    venv_path = "shader_tutorial_venv"
    if os.path.exists(venv_path):
        print(f"✓ Virtual environment found: {venv_path}")
    else:
        print(f"⚠️  Virtual environment not found: {venv_path}")
        print("   Consider creating it with: python -m venv shader_tutorial_venv")
    
    print()
    
    while True:
        print_menu()
        choice = input("Select tutorial number (0-2) or Q to quit: ").strip().upper()
        
        if choice == 'Q':
            print("\n👋 Goodbye! Happy shader programming!")
            break
        
        try:
            tutorial_num = int(choice)
            if tutorial_num < 0 or tutorial_num > 2:
                print("❌ Invalid choice. Please select 0, 1, 2, or Q")
                continue
            
            script = show_tutorial_info(tutorial_num)
            if script:
                input("\nPress ENTER to start the tutorial (or Ctrl+C to cancel)...")
                
                success = run_tutorial(script)
                
                if success:
                    print(f"\n✓ Tutorial completed successfully!")
                else:
                    print(f"\n⚠️  Tutorial ended")
                
                input("\nPress ENTER to return to menu...")
                print("\n" * 2)
        
        except ValueError:
            print("❌ Invalid input. Please enter a number (0-2) or Q")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user")
        sys.exit(0)
