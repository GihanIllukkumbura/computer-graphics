#! /usr/bin/env python


import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


class TestContext:
    """This shader passes color from an input array to the fragment shader,
    which interpolates the values across the face (via a 'varying' data type).
    """
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True
    
    def init_display(self):
        """Initialize Pygame and OpenGL"""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 02: Shader Colors")
        
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
        
        # Demonstration of shader compilation error handling
        try:
            shaders.compileShader( """ void main() { """, GL_VERTEX_SHADER )
        except (GLError, RuntimeError) as err:
            print('Example of shader compile error:', err)
        else:
            raise RuntimeError( """Didn't catch compilation error!""" )
        
        # Vertex Shader with Varying Values
        # The 'varying' keyword creates a variable that gets interpolated
        # between the vertex shader and fragment shader
        vertex = shaders.compileShader(
            """
            varying vec4 vertex_color;
            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                vertex_color = gl_Color;
            }""", GL_VERTEX_SHADER)
        
        # Fragment Shader
        # Receives the interpolated vertex_color for each fragment
        fragment = shaders.compileShader("""
            varying vec4 vertex_color;
            void main() {
                gl_FragColor = vertex_color ;
            }""", GL_FRAGMENT_SHADER)
        
        # Compile the complete shader program
        self.shader = shaders.compileProgram(vertex, fragment)
        
        # Create VBO with packed vertex and color data
        # Each row has 6 values: [x, y, z, r, g, b]
        # First 3 values are position, last 3 are RGB color
        self.vbo = vbo.VBO(
            np.array( [
                # Triangle 1: blends from green to yellow to cyan
                [  1, 1, 0,  1,1,0 ],  # Green
                [ -1,-1, 0,  1,1,0 ],  # Yellow
                [  1,-1, 0,  0,1,1 ],  # Cyan
                # Triangle 2 & 3: various colors blending
                [  2,-1, 0,  1,0,0 ],  # Red
                [  3,-1, 0,  0,1,0 ],  # Green
                [  2, 1, 0,  0,0,1 ],  # Blue
                [  2,-1, 0,  1,0,0 ],  # Red
                [  4, 1, 0,  0,0,1 ],  # Blue
                [  2, 1, 0,  0,1,1 ],  # Cyan
            ], dtype='f')
        )
        
        print("\n=== Tutorial 02: Shader Colors ===")
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("Shader compiled successfully!")
        print("VBO created with packed position and color data")
    
    def Render( self):
        """Render the geometry for the scene."""
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Enable our shader
        glUseProgram(self.shader)
        
        try:
            # Bind the VBO
            self.vbo.bind()
            try:
                # Enable both vertex and color arrays
                glEnableClientState(GL_VERTEX_ARRAY)
                glEnableClientState(GL_COLOR_ARRAY)
                
                # Setup vertex pointer
                # Parameters: size (3 values), type, stride (24 bytes), pointer
                # Stride = 6 floats * 4 bytes = 24 bytes between each vertex record
                glVertexPointer(3, GL_FLOAT, 24, self.vbo )
                
                # Setup color pointer
                # Starts 12 bytes (3 floats) after the vertex data
                glColorPointer(3, GL_FLOAT, 24, self.vbo+12 )
                
                # Draw all triangles
                glDrawArrays(GL_TRIANGLES, 0, 9)
                
            finally:
                # Clean up
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableClientState(GL_COLOR_ARRAY)
        finally:
            glUseProgram( 0 )
    
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
        print("\nYou should see colorful triangles with gradient blending!")
        
        while self.running:
            self.handle_events()
            self.Render()
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()


if __name__ == "__main__":
    print("="*60)
    print("Tutorial 02: Shader Colors - Varying Values")
    print("="*60)
    
    context = TestContext()
    context.main_loop()
