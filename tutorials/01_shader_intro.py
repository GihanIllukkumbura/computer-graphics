#! /usr/bin/env python
"""
Introduction to Shaders: First steps (Basic Geometry)

This tutorial teaches:
- What a vertex shader *must* do in GLSL
- What a fragment shader *must* do
- What a VBO object looks like
- How to activate and deactivate shaders and VBOs
- How to render simple geometry
"""

import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


class TestContext:
    """Creates a simple vertex shader..."""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True
    
    def init_display(self):
        """Initialize Pygame and OpenGL"""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 01: Shader Introduction")
        
        # Set white background color
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        # Set up perspective projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Move the camera back 10 units
        glTranslatef(0.0, 0.0, -10)
    
    def OnInit( self ):
        """Initialize the context once we have a valid OpenGL environ"""
        
        # Vertex Shader
        # The vertex shader calculates the position of each vertex
        # It MUST generate a gl_Position value (a vec4)
        VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", GL_VERTEX_SHADER)
        
        # Fragment Shader
        # The fragment shader determines the color of each pixel
        # It MUST generate a gl_FragColor value (a vec4)
        # Here we create a pure green opaque color
        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", GL_FRAGMENT_SHADER)
        
        # Compile the shader program
        # This links the vertex and fragment shaders together
        self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        
        # Create Vertex Buffer Object (VBO)
        # This stores our geometry data on the graphics card
        # Each row represents one vertex with 3 coordinates (x, y, z)
        # We're defining 3 triangles here (9 vertices total)
        self.vbo = vbo.VBO(
            np.array( [
                [  0, 1, 0 ],  # Triangle 1 - vertex 1
                [ -1,-1, 0 ],  # Triangle 1 - vertex 2
                [  1,-1, 0 ],  # Triangle 1 - vertex 3
                [  2,-1, 0 ],  # Triangle 2 - vertex 1
                [  4,-1, 0 ],  # Triangle 2 - vertex 2
                [  4, 1, 0 ],  # Triangle 2 - vertex 3
                [  2,-1, 0 ],  # Triangle 3 - vertex 1
                [  4, 1, 0 ],  # Triangle 3 - vertex 2
                [  2, 1, 0 ],  # Triangle 3 - vertex 3
            ], dtype='f')
        )
        
        print("\n=== Tutorial 01: Shader Introduction ===")
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("Shader compiled successfully!")
        print("VBO created with 9 vertices (3 triangles)")
    
    def Render( self):
        """Render the geometry for the scene."""
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Tell OpenGL to use our compiled shader
        shaders.glUseProgram(self.shader)
        
        try:
            # Bind the VBO (make it active)
            self.vbo.bind()
            try:
                # Enable vertex array processing
                glEnableClientState(GL_VERTEX_ARRAY)
                
                # Tell OpenGL where to find vertex data
                glVertexPointerf( self.vbo )
                
                # Draw the triangles (9 vertices = 3 triangles)
                glDrawArrays(GL_TRIANGLES, 0, 9)
                
            finally:
                # Clean up: unbind VBO and disable vertex array
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
        finally:
            # Clean up: disable the shader
            shaders.glUseProgram( 0 )
    
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
        self.OnInit()
        
        clock = pygame.time.Clock()
        
        print("\n=== Controls ===")
        print("ESC - Exit application")
        print("\nYou should see a green triangle and square!")
        
        while self.running:
            self.handle_events()
            self.Render()
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()


if __name__ == "__main__":
    print("="*60)
    print("Tutorial 01: Introduction to Shaders - Basic Geometry")
    print("="*60)
    
    context = TestContext()
    context.main_loop()
