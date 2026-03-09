#!/usr/bin/env python
"""
Tutorial 2: Colored Geometry with Vertex Attributes

This tutorial extends the first tutorial by introducing:
- Vertex attributes (color data per vertex)
- Interpolation between vertices
- Multiple data streams in VBO

Based on shader introduction tutorials for CMIS3234
"""

import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


class ColoredShaderContext:
    """Demonstrates vertex colors and interpolation"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True
        
    def init_display(self):
        """Initialize Pygame and OpenGL"""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Colored Geometry - CMIS3234 Tutorial 2")
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -8)
        
    def on_init(self):
        """Initialize shaders with vertex color support"""
        
        # ===== VERTEX SHADER WITH ATTRIBUTES =====
        # Now we introduce the concept of "varying" variables
        # These are passed from vertex shader to fragment shader
        # The GPU automatically interpolates these values across the triangle surface
        #
        # attribute vec3 vertexColor - color data we provide for each vertex
        # varying vec3 fragmentColor - interpolated color passed to fragment shader
        
        VERTEX_SHADER = shaders.compileShader("""#version 120
        
        // Attribute: input data that comes from the VBO (per-vertex)
        attribute vec3 vertexColor;
        
        // Varying: output data that goes to the fragment shader (interpolated)
        varying vec3 fragmentColor;
        
        void main() {
            // Transform vertex position as before
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            
            // Pass the color to the fragment shader
            // OpenGL will automatically interpolate this across the triangle
            fragmentColor = vertexColor;
        }
        """, GL_VERTEX_SHADER)
        
        # ===== FRAGMENT SHADER WITH INTERPOLATED COLORS =====
        # Now instead of a fixed color, we use the interpolated color
        # from the vertex shader
        #
        # The "varying" variable receives an interpolated value
        # For example, if one vertex is red (1,0,0) and another is blue (0,0,1),
        # the fragments between them will be purple shades
        
        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        
        // Varying: receives interpolated data from vertex shader
        varying vec3 fragmentColor;
        
        void main() {
            // Use the interpolated color, with full opacity (alpha = 1)
            gl_FragColor = vec4(fragmentColor, 1.0);
        }
        """, GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        
        # ===== INTERLEAVED VBO DATA =====
        # Modern OpenGL prefers "interleaved" data where all attributes
        # for a vertex are stored together:
        # [x, y, z, r, g, b] for each vertex
        #
        # This is more efficient than separate arrays
        
        # Create triangles with per-vertex colors
        # Format: [x, y, z, r, g, b] per vertex
        vertices = np.array([
            # Triangle 1 - RGB corners (classic color triangle)
            [ -3.0,  1.0, 0.0,   1.0, 0.0, 0.0],  # Top - Red
            [ -4.0, -1.0, 0.0,   0.0, 1.0, 0.0],  # Bottom-left - Green
            [ -2.0, -1.0, 0.0,   0.0, 0.0, 1.0],  # Bottom-right - Blue
            
            # Triangle 2 - Gradient from red to green
            [ -1.0,  1.0, 0.0,   1.0, 0.0, 0.0],  # Top - Red
            [ -1.0, -1.0, 0.0,   0.0, 1.0, 0.0],  # Bottom-left - Green
            [  1.0, -1.0, 0.0,   0.0, 1.0, 0.0],  # Bottom-right - Green
            
            # Triangle 3 - Cyan, Magenta, Yellow
            [  2.0,  1.0, 0.0,   0.0, 1.0, 1.0],  # Top - Cyan
            [  1.0, -1.0, 0.0,   1.0, 0.0, 1.0],  # Bottom-left - Magenta
            [  3.0, -1.0, 0.0,   1.0, 1.0, 0.0],  # Bottom-right - Yellow
            
            # Square (two triangles) - White to black gradient
            #  Triangle 1
            [  4.0,  1.0, 0.0,   1.0, 1.0, 1.0],  # Top-left - White
            [  4.0, -1.0, 0.0,   0.0, 0.0, 0.0],  # Bottom-left - Black
            [  6.0, -1.0, 0.0,   0.0, 0.0, 0.0],  # Bottom-right - Black
            #  Triangle 2
            [  4.0,  1.0, 0.0,   1.0, 1.0, 1.0],  # Top-left - White
            [  6.0, -1.0, 0.0,   0.0, 0.0, 0.0],  # Bottom-right - Black
            [  6.0,  1.0, 0.0,   1.0, 1.0, 1.0],  # Top-right - White
        ], dtype='f')
        
        self.vbo = vbo.VBO(vertices)
        
        # Get the location of our vertexColor attribute in the shader
        self.color_location = glGetAttribLocation(self.shader, 'vertexColor')
        
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("\nColored shader compiled successfully!")
        print(f"Vertex color attribute location: {self.color_location}")
        print("VBO created with 15 vertices (5 triangles)")
        print("\nColor interpolation concepts:")
        print("- Each vertex has its own color")
        print("- GPU interpolates colors smoothly across triangles")
        print("- Creates beautiful gradients automatically!")
        
    def render(self):
        """Render colored geometry"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        shaders.glUseProgram(self.shader)
        
        try:
            self.vbo.bind()
            try:
                # Calculate stride (bytes between consecutive vertices)
                # Each vertex has 6 floats: 3 for position (x,y,z) + 3 for color (r,g,b)
                # Each float is 4 bytes, so stride = 6 * 4 = 24 bytes
                stride = 6 * 4  # 24 bytes
                
                # Enable and set position attribute (first 3 floats)
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(
                    3,              # 3 components per vertex (x, y, z)
                    GL_FLOAT,       # data type
                    stride,         # bytes between consecutive vertices
                    self.vbo        # buffer object
                )
                
                # Enable and set color attribute (next 3 floats, offset by 12 bytes)
                glEnableVertexAttribArray(self.color_location)
                glVertexAttribPointer(
                    self.color_location,  # attribute location
                    3,                    # 3 components per color (r, g, b)
                    GL_FLOAT,             # data type
                    GL_FALSE,             # don't normalize
                    stride,               # bytes between consecutive vertices
                    ctypes.c_void_p(12)   # offset: 3 floats * 4 bytes = 12 bytes
                )
                
                # Draw all triangles
                glDrawArrays(GL_TRIANGLES, 0, 15)
                
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableVertexAttribArray(self.color_location)
        finally:
            shaders.glUseProgram(0)
    
    def handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
    
    def main_loop(self):
        """Main application loop"""
        self.init_display()
        self.on_init()
        
        clock = pygame.time.Clock()
        
        print("\n=== Controls ===")
        print("ESC - Exit application")
        print("\nObserve the color gradients!")
        print("Notice how colors smoothly blend between vertices")
        
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    print("="*60)
    print("CMIS3234 - Shader-based OpenGL Programming")
    print("Tutorial 2: Colored Geometry with Vertex Attributes")
    print("="*60)
    print("\nNew Concepts:")
    print("- Vertex attributes (per-vertex data)")
    print("- Varying variables (interpolated data)")
    print("- Interleaved VBO data")
    print("- Automatic color interpolation")
    print("="*60 + "\n")
    
    context = ColoredShaderContext()
    context.main_loop()
