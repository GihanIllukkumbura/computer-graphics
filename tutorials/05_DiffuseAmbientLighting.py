#! /usr/bin/env python
"""
Introduction to Shaders: Diffuse, Ambient, Directional Lighting

This tutorial builds on earlier tutorials by adding:
- Ambient lighting (global + per-light)
- Diffuse lighting (Lambertian reflectance)
- Directional lights (like the Sun)
- Normals as vertex attributes
- The Normal Matrix for correct light-space transforms
- A "bow window" geometry to show lighting angle effects

Key new concept: the vertex shader now CALCULATES a colour from
physics-based lighting equations rather than just passing through
a colour that was stored in the VBO.
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


# ---------------------------------------------------------------------------
# GLSL helper function (prepended to the vertex shader source)
# ---------------------------------------------------------------------------
# phong_weightCalc computes how strongly a directional light illuminates a
# surface at a given fragment, based purely on the angle between the surface
# normal and the light direction (Lambert's Law).
#
# Both vectors MUST be normalised before calling.
#
# Returns a single float in [0, 1]:
#   0  → surface faces away from light (or is perpendicular)
#   1  → surface faces directly toward light
# ---------------------------------------------------------------------------
PHONG_WEIGHT_CALC = """
float phong_weightCalc(
    in vec3 light_pos,    // normalised light direction (eye-space)
    in vec3 frag_normal   // normalised surface normal (eye-space)
) {
    // dot product of normal and light gives cos(angle) between them
    // max(0, ...) clamps to zero for surfaces facing away from the light
    float n_dot_pos = max( 0.0, dot( frag_normal, light_pos ) );
    return n_dot_pos;
}
"""


class TestContext:
    """Demonstrates ambient + diffuse directional lighting in GLSL.

    New concepts:
    - Normals as per-vertex attributes
    - gl_NormalMatrix for transforming normals to eye-space
    - Ambient lighting: global constant + per-light contribution
    - Diffuse lighting: Lambertian dot-product calculation
    - A custom GLSL helper function (phong_weightCalc)
    """

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True

    # ------------------------------------------------------------------
    # Display initialisation
    # ------------------------------------------------------------------

    def init_display(self):
        """Initialize Pygame and OpenGL."""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 05: Diffuse & Ambient Lighting")

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

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
        # The vertex shader now CALCULATES the output colour from lighting
        # equations rather than reading it from the VBO.
        #
        # Uniforms (same value for all vertices in one draw call):
        #   Global_ambient   - constant light always present in the scene
        #   Light_ambient    - ambient contribution of the active light
        #   Light_diffuse    - diffuse (direct) colour of the light
        #   Light_location   - direction vector pointing TOWARD the light
        #   Material_ambient - how much ambient light the material reflects
        #   Material_diffuse - how much diffuse light the material reflects
        #
        # Attributes (per-vertex, from VBO):
        #   Vertex_position - 3D position (replaces old gl_Vertex / glVertexPointer)
        #   Vertex_normal   - surface normal at this vertex
        #
        # gl_NormalMatrix: a 3×3 matrix that correctly transforms normals
        #   when the model-view matrix has scaling/rotation. Always use this
        #   instead of multiplying normals by gl_ModelViewMatrix directly.
        #
        # Eye-space: we transform both the normal and the light direction
        #   into "eye space" (camera-relative coordinates) so the dot product
        #   gives the correct angle. Most lighting docs assume eye-space.
        # ------------------------------------------------------------------

        vertex = shaders.compileShader(PHONG_WEIGHT_CALC + """
            uniform vec4 Global_ambient;
            uniform vec4 Light_ambient;
            uniform vec4 Light_diffuse;
            uniform vec3 Light_location;
            uniform vec4 Material_ambient;
            uniform vec4 Material_diffuse;

            attribute vec3 Vertex_position;
            attribute vec3 Vertex_normal;

            varying vec4 baseColor;

            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * vec4(
                    Vertex_position, 1.0
                );

                // Transform the light direction into eye space
                vec3 EC_Light_location = gl_NormalMatrix * Light_location;

                // Calculate diffuse weight using Lambert's Law
                float diffuse_weight = phong_weightCalc(
                    normalize(EC_Light_location),
                    normalize(gl_NormalMatrix * Vertex_normal)
                );

                // Combine: global ambient + light ambient + diffuse
                baseColor = clamp(
                    (Global_ambient  * Material_ambient)
                  + (Light_ambient   * Material_ambient)
                  + (Light_diffuse   * Material_diffuse * diffuse_weight),
                    0.0, 1.0
                );
            }
        """, GL_VERTEX_SHADER)

        # Fragment shader is trivially simple - all work is in the vertex shader
        fragment = shaders.compileShader("""
            varying vec4 baseColor;
            void main() {
                gl_FragColor = baseColor;
            }
        """, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vertex, fragment)

        # ------------------------------------------------------------------
        # VBO: "Bow Window" geometry
        # ------------------------------------------------------------------
        # 18 vertices (6 triangles) forming three panels angled like a
        # bay/bow window — left panel, centre panel, right panel.
        # Each vertex: [pos.x, pos.y, pos.z,  normal.x, normal.y, normal.z]
        # stride = 6 floats × 4 bytes = 24 bytes
        #
        # The panels are positioned so that each faces a slightly different
        # direction relative to the light, making the diffuse shading
        # clearly visible as brightness differences between panels.
        # ------------------------------------------------------------------
        self.vbo = vbo.VBO(
            np.array([
                # Left panel  (faces left-forward, normal ≈ (-1, 0, 1))
                [ -1, 0, 0,  -1, 0, 1 ],
                [  0, 0, 1,  -1, 0, 2 ],
                [  0, 1, 1,  -1, 0, 2 ],
                [ -1, 0, 0,  -1, 0, 1 ],
                [  0, 1, 1,  -1, 0, 2 ],
                [ -1, 1, 0,  -1, 0, 1 ],
                # Centre panel (faces forward, normal ≈ (0, 0, 1))
                [  0, 0, 1,  -1, 0, 2 ],
                [  1, 0, 1,   1, 0, 2 ],
                [  1, 1, 1,   1, 0, 2 ],
                [  0, 0, 1,  -1, 0, 2 ],
                [  1, 1, 1,   1, 0, 2 ],
                [  0, 1, 1,  -1, 0, 2 ],
                # Right panel (faces right-forward, normal ≈ (1, 0, 1))
                [  1, 0, 1,   1, 0, 2 ],
                [  2, 0, 0,   1, 0, 1 ],
                [  2, 1, 0,   1, 0, 1 ],
                [  1, 0, 1,   1, 0, 2 ],
                [  2, 1, 0,   1, 0, 1 ],
                [  1, 1, 1,   1, 0, 2 ],
            ], dtype='f')
        )

        # ------------------------------------------------------------------
        # Query all uniform and attribute locations
        # ------------------------------------------------------------------
        # We iterate over names to keep setup concise.
        # Locations are stored as instance attributes: self.Global_ambient_loc, etc.
        # ------------------------------------------------------------------
        for uniform_name in (
            'Global_ambient',
            'Light_ambient', 'Light_diffuse', 'Light_location',
            'Material_ambient', 'Material_diffuse',
        ):
            loc = glGetUniformLocation(self.shader, uniform_name)
            if loc in (None, -1):
                print(f"WARNING: uniform not found: {uniform_name}")
            setattr(self, uniform_name + '_loc', loc)

        for attr_name in ('Vertex_position', 'Vertex_normal'):
            loc = glGetAttribLocation(self.shader, attr_name)
            if loc in (None, -1):
                print(f"WARNING: attribute not found: {attr_name}")
            setattr(self, attr_name + '_loc', loc)

        print("\n=== Tutorial 05: Diffuse & Ambient Lighting ===")
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print("Shader compiled OK")
        print(f"Attribute locations → Vertex_position:{self.Vertex_position_loc}  "
              f"Vertex_normal:{self.Vertex_normal_loc}")

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def Render(self):
        """Render the bow-window geometry with per-vertex lighting."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(-0.5, -0.5, -5.0)   # centre the bow window

        glUseProgram(self.shader)

        try:
            self.vbo.bind()
            try:
                # -- Set lighting and material uniforms ----------------------
                # Global ambient: slight red tinge so you can see it
                glUniform4f(self.Global_ambient_loc,   0.3, 0.05, 0.05, 1.0)
                # Light: white, positioned upper-right in the scene
                glUniform4f(self.Light_ambient_loc,    0.2, 0.2, 0.2, 1.0)
                glUniform4f(self.Light_diffuse_loc,    1.0, 1.0, 1.0, 1.0)
                glUniform3f(self.Light_location_loc,   2.0, 2.0, 10.0)
                # Material: white-ish, reflects most of both ambient and diffuse
                glUniform4f(self.Material_ambient_loc, 0.2, 0.2, 0.2, 1.0)
                glUniform4f(self.Material_diffuse_loc, 1.0, 1.0, 1.0, 1.0)

                # -- Bind attribute arrays -----------------------------------
                stride = 6 * 4   # 6 floats × 4 bytes = 24

                glEnableVertexAttribArray(self.Vertex_position_loc)
                glEnableVertexAttribArray(self.Vertex_normal_loc)

                glVertexAttribPointer(
                    self.Vertex_position_loc,
                    3, GL_FLOAT, False, stride, self.vbo        # offset 0
                )
                glVertexAttribPointer(
                    self.Vertex_normal_loc,
                    3, GL_FLOAT, False, stride, self.vbo + 12   # offset 12 bytes
                )

                glDrawArrays(GL_TRIANGLES, 0, 18)

            finally:
                self.vbo.unbind()
                glDisableVertexAttribArray(self.Vertex_position_loc)
                glDisableVertexAttribArray(self.Vertex_normal_loc)

        finally:
            glUseProgram(0)

    # ------------------------------------------------------------------
    # Event handling & main loop
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.running = False

    def main_loop(self):
        self.init_display()
        self.OnInit()

        clock = pygame.time.Clock()

        print("\n=== Controls ===")
        print("ESC - Exit")
        print("Notice the three bow-window panels lit differently by the directional light.")

        while self.running:
            self.handle_events()
            self.Render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("Tutorial 05: Diffuse, Ambient, Directional Lighting")
    print("=" * 60)
    context = TestContext()
    context.main_loop()
