#!/usr/bin/env python
"""
Environment Verification Script for CMIS3234 Shader Tutorial

This script checks if all required packages are properly installed
and if your system supports the required OpenGL features.
"""

import sys

def check_python_version():
    """Check Python version"""
    print("="*60)
    print("1. Python Version Check")
    print("="*60)
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ WARNING: Python 3.10 or higher is recommended")
        return False
    else:
        print("✓ Python version is compatible")
        return True

def check_numpy():
    """Check NumPy installation"""
    print("\n" + "="*60)
    print("2. NumPy Check")
    print("="*60)
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
        
        # Test array creation
        test_array = np.array([[1, 2, 3], [4, 5, 6]], dtype='f')
        print(f"✓ Array creation test passed")
        return True
    except ImportError:
        print("❌ NumPy not found. Install with: pip install numpy")
        return False
    except Exception as e:
        print(f"❌ NumPy test failed: {e}")
        return False

def check_pygame():
    """Check Pygame installation"""
    print("\n" + "="*60)
    print("3. Pygame Check")
    print("="*60)
    try:
        import pygame
        print(f"✓ Pygame version: {pygame.__version__}")
        
        # Initialize pygame
        pygame.init()
        print("✓ Pygame initialization successful")
        pygame.quit()
        return True
    except ImportError:
        print("❌ Pygame not found. Install with: pip install pygame")
        return False
    except Exception as e:
        print(f"❌ Pygame test failed: {e}")
        return False

def check_pyopengl():
    """Check PyOpenGL installation"""
    print("\n" + "="*60)
    print("4. PyOpenGL Check")
    print("="*60)
    try:
        import OpenGL
        print(f"✓ PyOpenGL version: {OpenGL.__version__}")
        
        from OpenGL import GL
        print("✓ OpenGL.GL imported successfully")
        
        from OpenGL.GL import shaders
        print("✓ OpenGL.GL.shaders imported successfully")
        
        from OpenGL.arrays import vbo
        print("✓ OpenGL VBO support available")
        
        return True
    except ImportError as e:
        print(f"❌ PyOpenGL not found: {e}")
        print("Install with: pip install PyOpenGL PyOpenGL-accelerate")
        return False
    except Exception as e:
        print(f"❌ PyOpenGL test failed: {e}")
        return False

def check_opengl_support():
    """Check OpenGL version support"""
    print("\n" + "="*60)
    print("5. OpenGL Hardware Support Check")
    print("="*60)
    try:
        import pygame
        from pygame.locals import DOUBLEBUF, OPENGL, HIDDEN
        from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION, GL_SHADING_LANGUAGE_VERSION
        
        # Create a hidden window to get OpenGL context
        pygame.init()
        pygame.display.set_mode((100, 100), DOUBLEBUF | OPENGL | HIDDEN)
        
        # Get OpenGL information
        vendor = glGetString(GL_VENDOR)
        renderer = glGetString(GL_RENDERER)
        version = glGetString(GL_VERSION)
        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)
        
        print(f"Vendor: {vendor.decode() if vendor else 'Unknown'}")
        print(f"Renderer: {renderer.decode() if renderer else 'Unknown'}")
        print(f"OpenGL Version: {version.decode() if version else 'Unknown'}")
        print(f"GLSL Version: {glsl_version.decode() if glsl_version else 'Unknown'}")
        
        # Check version number
        if version:
            version_str = version.decode()
            major_version = int(version_str.split('.')[0])
            
            if major_version >= 2:
                print(f"✓ OpenGL {major_version}.x is supported (Required: 2.0+)")
                result = True
            else:
                print(f"❌ OpenGL {major_version}.x is too old (Required: 2.0+)")
                print("   Please update your graphics drivers")
                result = False
        else:
            print("❌ Could not determine OpenGL version")
            result = False
        
        pygame.quit()
        return result
        
    except Exception as e:
        print(f"❌ OpenGL support check failed: {e}")
        print("   This might indicate driver issues or unsupported hardware")
        return False

def check_optional_packages():
    """Check optional packages"""
    print("\n" + "="*60)
    print("6. Optional Packages")
    print("="*60)
    
    optional = {
        'glm': 'pip install PyGLM',
        'PIL': 'pip install Pillow'
    }
    
    for package, install_cmd in optional.items():
        try:
            if package == 'PIL':
                import PIL
                from PIL import Image
                print(f"✓ PIL (Pillow) available")
            elif package == 'glm':
                import glm
                print(f"✓ PyGLM available")
            else:
                exec(f"import {package}")
                print(f"✓ {package} available")
        except ImportError:
            print(f"○ {package} not installed (optional)")
            print(f"  Install with: {install_cmd}")

def main():
    """Run all checks"""
    print("\n" + "█"*60)
    print("  CMIS3234 - Shader Tutorial Environment Verification")
    print("█"*60 + "\n")
    
    results = []
    
    # Required checks
    results.append(("Python Version", check_python_version()))
    results.append(("NumPy", check_numpy()))
    results.append(("Pygame", check_pygame()))
    results.append(("PyOpenGL", check_pyopengl()))
    results.append(("OpenGL Support", check_opengl_support()))
    
    # Optional checks (don't affect overall result)
    check_optional_packages()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All required checks passed!")
        print("✓ Your environment is ready for the shader tutorials")
        print("\nRun 'python shader_intro.py' to start the first tutorial")
    else:
        print("❌ Some checks failed")
        print("Please install missing packages and update drivers if needed")
        print("\nTo install all required packages:")
        print("  pip install numpy pygame PyOpenGL PyOpenGL-accelerate")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
