#!/usr/bin/env python
"""
Introduction to Shaders: First steps (Basic Geometry)

This tutorial introduces modern, low-level 3D rendering techniques using GLSL shaders.
Based on: https://pyopengl.sourceforge.net/context/tutorials/shader_intro.html

In this tutorial we'll learn:
- What a vertex shader *must* do in GLSL
- What a fragment shader *must* do
- What a VBO object looks like
- How to activate and deactivate shaders and VBOs
- How to render simple geometry

Modified to use Pygame instead of OpenGLContext for Python 3.12+ compatibility.
"""

import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


class ShaderContext:
    """Creates a simple vertex shader demonstration"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True
        
    def init_display(self):
        """Initialize Pygame and OpenGL"""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Shader Introduction - CMIS3234")
        
        # Set up perspective projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Simple perspective matrix
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Move the camera back 10 units
        glTranslatef(0.0, 0.0, -10)
        
    def on_init(self):
        """
        Initialize OpenGL shaders and VBO
        Called after OpenGL context is created
        """
        
        # ===== VERTEX SHADER =====
        # The vertex shader must calculate a vertex position for each vertex.
        # It only needs to do one thing: generate a gl_Position value (vec4).
        #
        # gl_Vertex: built-in variable representing the vertex from fixed-function pipeline
        # gl_ModelViewProjectionMatrix: transforms model-space coordinates to view-space
        # 
        # The final vertex position is calculated with a dot-product of the 
        # model-view matrix and the vertex to be transformed.
        
        VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", GL_VERTEX_SHADER)
        
        # ===== FRAGMENT SHADER =====
        # After vertex processing, the GL generates "fragments" (possible pixels).
        # The fragment shader determines what colour each fragment should be.
        # It only *needs* to do one thing: generate a gl_FragColor value (vec4).
        #
        # Here we create a pure green opaque color for each pixel.
        # vec4(red, green, blue, alpha) - values from 0.0 to 1.0
        
        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", GL_FRAGMENT_SHADER)
        
        # Compile the shader program by linking vertex and fragment shaders
        # The shader program is an opaque GLuint token used to refer to the shader
        self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        
        # ===== VERTEX BUFFER OBJECT (VBO) =====
        # Modern OpenGL prefers loading data onto the video card via VBOs.
        # VBOs are flexible data-storage areas reserved on the card.
        #
        # We use a Numpy array to define vertex data (3 floats per vertex).
        # Modern cards work best with tightly-packed vertex data.
        #
        # Modern OpenGL only supports triangle and point-type geometry.
        # Here we create one triangle and a square (two triangles with shared vertices).
        
        self.vbo = vbo.VBO(
            np.array([
                # First triangle
                [  0,  1, 0 ],
                [ -1, -1, 0 ],
                [  1, -1, 0 ],
                # Second triangle (part of square)
                [  2, -1, 0 ],
                [  4, -1, 0 ],
                [  4,  1, 0 ],
                # Third triangle (completes square)
                [  2, -1, 0 ],
                [  4,  1, 0 ],
                [  2,  1, 0 ],
            ], dtype='f')
        )
        
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("\nShader compiled successfully!")
        print("VBO created with 9 vertices (3 triangles)")
        
    def render(self):
        """
        Render the geometry for the scene
        """
        # Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # ===== RENDERING =====
        # Tell OpenGL to use our compiled shader program
        shaders.glUseProgram(self.shader)
        
        try:
            # Enable and bind our VBO as the source for geometric data
            self.vbo.bind()
            try:
                # Tell OpenGL to process vertex (location) data from our VBO
                # The VBO acts like regular array data, but stored on the GPU
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointerf(self.vbo)
                
                # Draw triangles using 9 vertices (3 triangles)
                # glDrawArrays always draws "in sequence" from the vertex array
                glDrawArrays(GL_TRIANGLES, 0, 9)
                
            finally:
                # Clean up: unbind VBO and disable vertex array
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
        finally:
            # Unbind shader to allow fixed-function rendering
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
        print("\nYou should see a green triangle and square!")
        
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()


if __name__ == "__main__":
    print("="*60)
    print("CMIS3234 - Shader-based OpenGL Programming")
    print("Tutorial: Introduction to Shaders - Basic Geometry")
    print("="*60)
    
    context = ShaderContext()
    context.main_loop()
