#! /usr/bin/env python
"""
Introduction to Shaders: Attribute Values (Tweening)

This tutorial builds on the previous tutorial by:
- Defining attribute values in shaders
- Defining arrays to feed attribute values
- Eliminating most of our remaining legacy code
- Defining a simple "tween" geometry animation

Instead of using the legacy glVertexPointer/glColorPointer, we now
define arbitrary vertex attributes. We store TWO positions per vertex
and use a uniform "tween" fraction to smoothly interpolate between them
each frame - this is known as "tweening" (in-betweening).
"""

import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


class TestContext:
    """Demonstrates use of vertex attribute types in GLSL.

    Key concepts:
    - Attribute values (per-vertex data, not just position/colour)
    - glVertexAttribPointer replaces glVertexPointer/glColorPointer
    - Tween animation by mixing two positions in the vertex shader
    - Uniform fraction drives the animation
    """

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True

        # Animation state
        self.tween_fraction = 0.0   # 0.0 → 1.0 animation value
        self._anim_time = 0.0       # accumulated seconds
        self.anim_duration = 2.0    # seconds for one full cycle

    # ------------------------------------------------------------------
    # Display initialisation
    # ------------------------------------------------------------------

    def init_display(self):
        """Initialize Pygame and OpenGL."""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 04: Attribute Values (Tweening)")

        glClearColor(0.1, 0.1, 0.1, 1.0)   # dark background

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    # ------------------------------------------------------------------
    # Shader and VBO setup
    # ------------------------------------------------------------------

    def OnInit(self):
        """Compile shaders, build VBO, query attribute/uniform locations."""

        # ------------------------------------------------------------------
        # Vertex shader
        # ------------------------------------------------------------------
        # New concepts introduced here:
        #
        # uniform float tween  - a value in [0..1] fed from Python each frame,
        #                         controlling how far the vertex has "tweened"
        #                         towards its alternate position.
        #
        # attribute vec3 position - the vertex's "start" position
        # attribute vec3 tweened  - the vertex's "end" position
        # attribute vec3 color    - per-vertex colour
        #
        # The built-in GLSL function mix(a, b, t) linearly interpolates between
        # a and b using t:
        #     result = a*(1-t) + b*t
        #
        # When tween=0.0  → gl_Position comes entirely from 'position'
        # When tween=1.0  → gl_Position comes entirely from 'tweened'
        # When tween=0.5  → halfway between the two positions
        # ------------------------------------------------------------------

        vertex = shaders.compileShader("""
            uniform float tween;

            attribute vec3 position;
            attribute vec3 tweened;
            attribute vec3 color;

            varying vec4 baseColor;

            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * mix(
                    vec4( position, 1.0 ),
                    vec4( tweened,  1.0 ),
                    tween
                );
                baseColor = vec4(color, 1.0);
            }
        """, GL_VERTEX_SHADER)

        # Fragment shader is unchanged from Tutorial 02/03 - just output
        # the interpolated colour passed from the vertex shader.
        fragment = shaders.compileShader("""
            varying vec4 baseColor;
            void main() {
                gl_FragColor = baseColor;
            }
        """, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vertex, fragment)

        # ------------------------------------------------------------------
        # VBO data
        # ------------------------------------------------------------------
        # Each vertex row has 9 floats:
        #   [pos.x, pos.y, pos.z,  tweened.x, tweened.y, tweened.z,  r, g, b]
        #
        # Two triangles sharing two vertices:
        #   Triangle 1 (left):  rows 0-2
        #   Triangle 2 (right): rows 3-8  (indices 3,4,5 + 6,7,8)
        #
        # The "tweened" columns move some vertices to dramatically different
        # positions so the animation is easy to see.
        # ------------------------------------------------------------------
        self.vbo = vbo.VBO(
            np.array([
                #  position        tweened         color
                [  0,  1,  0,    1,  3,  0,    0, 1, 0 ],   # top        → shoots up
                [ -1, -1,  0,   -1, -1,  0,    1, 1, 0 ],   # bottom-left (stays)
                [  1, -1,  0,    1, -1,  0,    0, 1, 1 ],   # bottom-right (stays)
                [  2, -1,  0,    2, -1,  0,    1, 0, 0 ],   # right-bottom (stays)
                [  4, -1,  0,    4, -1,  0,    0, 1, 0 ],   # far-right-bottom
                [  4,  1,  0,    4,  9,  0,    0, 0, 1 ],   # far-right-top → shoots up
                [  2, -1,  0,    2, -1,  0,    1, 0, 0 ],
                [  4,  1,  0,    1,  3,  0,    0, 0, 1 ],   # tweens to left
                [  2,  1,  0,    1, -1,  0,    0, 1, 1 ],   # tweens left+down
            ], dtype='f')
        )

        # ------------------------------------------------------------------
        # Query attribute and uniform locations
        # ------------------------------------------------------------------
        # Unlike uniforms, attribute locations are queried with
        # glGetAttribLocation().  We use these integer handles later when
        # calling glVertexAttribPointer() to tell the GPU which bytes of the
        # VBO feed which attribute.
        # ------------------------------------------------------------------
        self.position_location = glGetAttribLocation(self.shader, 'position')
        self.tweened_location   = glGetAttribLocation(self.shader, 'tweened')
        self.color_location     = glGetAttribLocation(self.shader, 'color')
        self.tween_location     = glGetUniformLocation(self.shader, 'tween')

        print("\n=== Tutorial 04: Attribute Values (Tweening) ===")
        print("OpenGL Version :", glGetString(GL_VERSION).decode())
        print("GLSL Version   :", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
        print("Shader compiled successfully!")
        print(f"Attribute locations  → position:{self.position_location}  "
              f"tweened:{self.tweened_location}  color:{self.color_location}")
        print(f"Uniform  location   → tween:{self.tween_location}")

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def Render(self):
        """Render the geometry for the current frame."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(-1.5, 0.0, -10.0)   # centre the scene

        glUseProgram(self.shader)

        # Upload the current tween fraction to the GPU
        glUniform1f(self.tween_location, self.tween_fraction)

        try:
            self.vbo.bind()
            try:
                # stride = 9 floats × 4 bytes = 36 bytes per vertex
                stride = 9 * 4

                # Enable each attribute array before describing it
                glEnableVertexAttribArray(self.position_location)
                glEnableVertexAttribArray(self.tweened_location)
                glEnableVertexAttribArray(self.color_location)

                # glVertexAttribPointer(location, size, type, normalized, stride, pointer)
                #   location   - which attribute slot
                #   size       - number of components (3 = xyz)
                #   type       - GL_FLOAT
                #   normalized - False (raw floats, no normalization)
                #   stride     - bytes between consecutive vertex records
                #   pointer    - byte offset into VBO where this attribute starts

                glVertexAttribPointer(
                    self.position_location,
                    3, GL_FLOAT, False, stride, self.vbo          # offset 0
                )
                glVertexAttribPointer(
                    self.tweened_location,
                    3, GL_FLOAT, False, stride, self.vbo + 12     # offset 12 bytes (3 floats)
                )
                glVertexAttribPointer(
                    self.color_location,
                    3, GL_FLOAT, False, stride, self.vbo + 24     # offset 24 bytes (6 floats)
                )

                glDrawArrays(GL_TRIANGLES, 0, 9)

            finally:
                self.vbo.unbind()
                # Always disable attribute arrays to avoid reading stale pointers
                glDisableVertexAttribArray(self.position_location)
                glDisableVertexAttribArray(self.tweened_location)
                glDisableVertexAttribArray(self.color_location)

        finally:
            glUseProgram(0)

    # ------------------------------------------------------------------
    # Animation timer
    # ------------------------------------------------------------------

    def update_tween(self, dt):
        """Advance the tween animation.

        The animation runs 0→1 over anim_duration seconds, then loops.
        We fold the value back so it ping-pongs 0→1→0, giving a smooth
        back-and-forth motion.
        """
        self._anim_time = (self._anim_time + dt) % self.anim_duration
        frac = self._anim_time / self.anim_duration   # 0.0 → 1.0

        # Ping-pong: first half 0→1, second half 1→0
        if frac > 0.5:
            frac = 1.0 - frac
        frac *= 2.0   # rescale back to [0, 1]

        self.tween_fraction = frac

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_events(self):
        """Handle Pygame input events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_SPACE:
                    # Pause / resume animation by toggling speed
                    pass   # extend if needed

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def main_loop(self):
        """Initialise and run the application."""
        self.init_display()
        self.OnInit()

        clock = pygame.time.Clock()

        print("\n=== Controls ===")
        print("ESC   - Exit")
        print("Watch the triangles smoothly morph between two shapes!")

        while self.running:
            dt = clock.tick(60) / 1000.0   # seconds since last frame
            self.handle_events()
            self.update_tween(dt)
            self.Render()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("Tutorial 04: Attribute Values (Tweening)")
    print("=" * 60)
    context = TestContext()
    context.main_loop()
