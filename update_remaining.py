import re

# List of files to update
files = [
    "tutorials/3Ddrawing/08_3d_rotation_xyz.py",
    "tutorials/3Ddrawing/09_3d_reflection.py",
    "tutorials/3Ddrawing/10_3d_shearing.py",
]

render_key_mappings = '''
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

for fpath in files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    # 1. Add zoom = 1.0 after view_angle_y
    content = content.replace(
        "        self.view_angle_y = 0.0\n        \n        # Mouse tracking",
        "        self.view_angle_y = 0.0\n        self.zoom = 1.0\n        \n        # Mouse tracking"
    )
    
    # 2. Add zoom reset in reset_all
    content = content.replace(
        "        self.view_angle_y = 0.0\n\n    def is_point_in_rect",
        "        self.view_angle_y = 0.0\n        self.zoom = 1.0\n\n    def is_point_in_rect"
    )
    
    # 3. Add scroll wheel zoom handling
    content = content.replace(
        "                    self.mouse_dragging = False\n            elif event.type == pygame.MOUSEBUTTONUP:",
        "                    self.mouse_dragging = False\n                elif event.button == 4:  # Scroll wheel up - zoom in\n                    self.zoom = min(3.0, self.zoom * 1.1)\n                elif event.button == 5:  # Scroll wheel down - zoom out\n                    self.zoom = max(0.3, self.zoom / 1.1)\n            elif event.type == pygame.MOUSEBUTTONUP:"
    )
    
    # 4. Add keyboard zoom - find the line before MOUSEBUTTONUP and add zoom keys
    if "elif event.key == pygame.K_RIGHT:" in content and "self.zoom" not in content:
        # Find a good insertion point - after the last key handler
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '            elif event.type == pygame.MOUSEBUTTONDOWN:' in line:
                # Insert before this line
                zoom_handler = "                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:\n                    self.zoom = min(3.0, self.zoom + 0.1)\n                if event.key == pygame.K_MINUS:\n                    self.zoom = max(0.3, self.zoom - 0.1)"
                lines.insert(i, zoom_handler)
                content = '\n'.join(lines)
                break
    
    # 5. Add zoom scale after glTranslatef
    content = content.replace(
        "        glTranslatef(0, 0, -10)\n        glRotatef(self.view_angle_x, 1, 0, 0)",
        "        glTranslatef(0, 0, -10)\n        glScalef(self.zoom, self.zoom, self.zoom)\n        glRotatef(self.view_angle_x, 1, 0, 0)"
    )
    
    # 6. Call render_key_mappings in render_hud
    content = content.replace(
        "        glDisable(GL_DEPTH_TEST)\n\n        # Draw reset button",
        "        glDisable(GL_DEPTH_TEST)\n\n        self.render_key_mappings()\n\n        # Draw reset button"
    )
    
    # 7. Add the render_key_mappings method before run()
    if "def render_key_mappings" not in content:
        content = content.replace(
            "\n    def run(self) -> None:",
            render_key_mappings + "\n    def run(self) -> None:"
        )
    
    with open(fpath, 'w') as f:
        f.write(content)
    
    print(f"Updated: {fpath}")

print("All files updated successfully!")
