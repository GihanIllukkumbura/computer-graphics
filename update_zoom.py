#!/usr/bin/env python3
"""Update 3D tutorial files with zoom functionality."""

import re
import sys

files = [
    "tutorials/3Ddrawing/08_3d_rotation_xyz.py",
    "tutorials/3Ddrawing/09_3d_reflection.py",
    "tutorials/3Ddrawing/10_3d_shearing.py",
]

render_key_mappings_method = '''
    def render_key_mappings(self) -> None:
        """Render key mappings in top-right corner."""
        # Key mappings displayed in top-right
        key_mappings = [
            "=== KEY MAPPINGS ===",
            "",
            "VIEW CONTROL:",
            "Mouse Drag: Rotate view",
            "Scroll Wheel: Zoom in/out",
            "+/-: Zoom in/out",
            "",
            "PARAMETERS:",
            "Left/Right: Primary param",
            "Up/Down: Secondary param",
            "Ctrl+Up/Down: Z-axis",
            "Shift: Fine adjustment",
            "",
            "RESET & EXIT:",
            "R: Reset all",
            "Q/ESC: Quit",
        ]
        
        # Display in top-right corner
        x_offset = self.width - 280
        y_offset = 20
        
        glColor3f(0.7, 0.7, 0.7)
        for line in key_mappings:
            # Text positioning (using simple OpenGL rendering)
            # This is a placeholder - actual text rendering would use font texture
            y_offset += 16
'''

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add zoom initialization after view_angle_y
        content = re.sub(
            r"(self\.view_angle_y = 0\.0)\n(\s+# Mouse tracking)",
            r"\1\n        self.zoom = 1.0\n\2",
            content
        )
        
        # 2. Add zoom to reset_all() - add at the end of reset_all
        content = re.sub(
            r"(def reset_all\(self\).*?self\.view_angle_y = 0\.0)",
            r"\1\n        self.zoom = 1.0",
            content,
            flags=re.DOTALL
        )
        
        # 3. Update MOUSEBUTTONDOWN to handle scroll wheel
        pattern = r"(elif event\.type == pygame\.MOUSEBUTTONDOWN:\n\s+if event\.button == 1:.*?self\.mouse_dragging = False)\n(\s+elif event\.type)"
        replacement = r"""\1
                elif event.button == 4:  # Scroll wheel up - zoom in
                    self.zoom = min(3.0, self.zoom * 1.1)
                elif event.button == 5:  # Scroll wheel down - zoom out
                    self.zoom = max(0.3, self.zoom / 1.1)
\2"""
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 4. Add keyboard zoom handling - add after the key handlers
        # Find the pattern where we need to add keyboard zoom
        pattern = r"(if event\.key == pygame\.K_.*?:\n\s+\w+.*?)\n(\s+elif event\.type == pygame\.MOUSEBUTTONDOWN:)"
        
        # More specific: find a line with step and add after UP/DOWN handling
        if "elif event.key == pygame.K_UP:" in content or "if event.key == pygame.K_UP:" in content:
            # Look for the pattern after any key handling
            lines = content.split('\n')
            insert_idx = -1
            for i, line in enumerate(lines):
                if 'elif event.type == pygame.MOUSEBUTTONDOWN:' in line:
                    # Go backwards from this line to find where keyboard handling ends
                    if i > 0 and 'self.zoom' not in '\n'.join(lines[max(0, i-20):i]):
                        insert_idx = i
                        break
            
            if insert_idx > 0:
                # Insert zoom handling before this line
                zoom_lines = [
                    "                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:",
                    "                    self.zoom = min(3.0, self.zoom + 0.1)",
                    "                if event.key == pygame.K_MINUS:",
                    "                    self.zoom = max(0.3, self.zoom - 0.1)",
                ]
                for zoom_line in reversed(zoom_lines):
                    lines.insert(insert_idx, zoom_line)
                content = '\n'.join(lines)
        
        # 5. Add zoom scale in render() after glTranslatef
        content = re.sub(
            r"(glTranslatef\(0, 0, -10\))\n(\s+glRotatef)",
            r"\1\n        glScalef(self.zoom, self.zoom, self.zoom)\n\2",
            content
        )
        
        # 6. Add render_key_mappings() call in render_hud()
        content = re.sub(
            r"(glDisable\(GL_DEPTH_TEST\))\n\n(\s+# Draw reset button)",
            r"\1\n\n        self.render_key_mappings()\n\n\2",
            content
        )
        
        # 7. Add render_key_mappings() method before run()
        if "def render_key_mappings" not in content:
            # Insert before run() method
            content = re.sub(
                r"(\n    def run\(self\) -> None:)",
                render_key_mappings_method + r"\n\n    def run(self) -> None:",
                content
            )
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {filepath}")
        else:
            print(f"⚠ No changes for {filepath}")
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        import traceback
        traceback.print_exc()

print("\nDone!")
