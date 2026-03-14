#! /usr/bin/env python
"""
Introduction to Shaders: Specular Highlights, Indexed Geometry, Directional Lighting

This tutorial builds on Tutorial 05 by adding:
- Specular lighting (Blinn-Phong method)
- Per-FRAGMENT lighting (moves work from vertex shader to fragment shader)
- Indexed geometry rendering (glDrawElements + GL_ELEMENT_ARRAY_BUFFER)
- Procedurally generated sphere geometry

Key new concepts:
  • Blinn-Phong: uses a "half-vector" (bisector of light + eye) to approximate
    specular highlight cheaply and accurately
  • Per-fragment lighting: normals are interpolated per-fragment for smooth shading
  • glDrawElements: renders shared vertices via an index buffer (no duplication)
  • Two VBOs bound to two different targets simultaneously
"""

import math
import ctypes
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo


# ---------------------------------------------------------------------------
# Sphere geometry generator
# ---------------------------------------------------------------------------
# Generates a UV sphere with:
#   - coords VBO: interleaved [pos.x, pos.y, pos.z, u, v, norm.x, norm.y, norm.z]
#     (8 floats per vertex, matching the OpenGLContext Sphere layout)
#   - indices VBO: triangles encoded as unsigned shorts
#   - count: number of indices
#
# For a UNIT sphere centred at the origin: normal == position vector.
# The texture coords (u, v) are included purely to keep the stride at 32 bytes
# (8 floats), matching the layout referenced in the tutorial's stride calculation.
# ---------------------------------------------------------------------------

def generate_sphere(radius=1.0, stacks=24, slices=24):
    """Return (coords_array, indices_array) for a UV sphere.

    coords_array: float32, shape (N, 8)  → [x, y, z, u, v, nx, ny, nz]
    indices_array: uint16, shape (M,)    → flat list of triangle indices
    """
    vertices = []
    for stack in range(stacks + 1):
        phi = math.pi / 2 - stack * math.pi / stacks       # +π/2 … -π/2
        y   = radius * math.sin(phi)
        r   = radius * math.cos(phi)
        for sl in range(slices + 1):
            theta = sl * 2 * math.pi / slices
            x  =  r * math.cos(theta)
            z  =  r * math.sin(theta)
            u  =  sl  / slices
            v  =  stack / stacks
            # For a unit sphere normal == normalised position
            nx, ny, nz = x / radius, y / radius, z / radius
            vertices.append([x, y, z, u, v, nx, ny, nz])

    indices = []
    for stack in range(stacks):
        for sl in range(slices):
            first  = stack * (slices + 1) + sl
            second = first + slices + 1
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])

    coords_array  = np.array(vertices, dtype='f')
    indices_array = np.array(indices,  dtype=np.uint16)
    return coords_array, indices_array


# ---------------------------------------------------------------------------
# Updated Blinn-Phong weight function
# ---------------------------------------------------------------------------
# Now returns a vec2:
#   .x = diffuse weight  (same as Tutorial 05)
#   .y = specular weight (new — Blinn-Phong half-vector method)
#
# The "half vector" H is the bisector of the light direction and the eye
# direction. Using H instead of the true reflection vector avoids an expensive
# reflect() call and is considered more physically accurate for many materials.
#
# n_dot_half is only calculated when the surface faces the light (n_dot_pos > 0)
# to avoid a "halo" of specular on the dark side of the object.
# The 0.05 fudge factor slightly widens the transition at the terminator.
# ---------------------------------------------------------------------------
PHONG_WEIGHT_CALC = """
vec2 phong_weightCalc(
    in vec3 light_pos,    // normalised light direction (eye-space)
    in vec3 half_light,   // half-way vector (eye-space)
    in vec3 frag_normal,  // normalised surface normal (eye-space)
    in float shininess    // material shininess exponent
) {
    float n_dot_pos  = max( 0.0, dot( frag_normal, light_pos ) );
    float n_dot_half = 0.0;
    if (n_dot_pos > -0.05) {
        n_dot_half = pow( max(0.0, dot( half_light, frag_normal )), shininess );
    }
    return vec2( n_dot_pos, n_dot_half );
}
"""


class TestContext:
    """Demonstrates Blinn-Phong specular highlights with per-fragment lighting
    on an indexed sphere mesh.

    New concepts vs Tutorial 05:
    - Specular highlights via Blinn-Phong half-vector
    - Fragment shader does the lighting (smoother result)
    - Vertex shader only interpolates the normal
    - glDrawElements with a separate index VBO
    """

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True

    # ------------------------------------------------------------------
    # Display initialisation
    # ------------------------------------------------------------------

    def init_display(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 06: Specular Blinn-Phong + Indexed Sphere")

        glClearColor(0.05, 0.05, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    # ------------------------------------------------------------------
    # Shader and geometry setup
    # ------------------------------------------------------------------

    def OnInit(self):
        """Compile shaders, build sphere VBOs, query locations."""

        # ------------------------------------------------------------------
        # Vertex shader — very simple!
        # ------------------------------------------------------------------
        # All lighting is now done in the FRAGMENT shader.
        # The vertex shader only:
        #   1. Transforms the vertex position to clip space (as always)
        #   2. Transforms the normal to eye-space and passes it as a varying
        #
        # The normal is then INTERPOLATED across the triangle by the rasteriser
        # and arrives in the fragment shader as a per-pixel value — this is
        # what gives smooth (Phong) shading instead of flat shading.
        # ------------------------------------------------------------------
        vertex = shaders.compileShader("""
            attribute vec3 Vertex_position;
            attribute vec3 Vertex_normal;
            varying vec3 baseNormal;
            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * vec4(
                    Vertex_position, 1.0
                );
                // Transform normal to eye-space and pass to fragment shader
                baseNormal = gl_NormalMatrix * normalize(Vertex_normal);
            }
        """, GL_VERTEX_SHADER)

        # ------------------------------------------------------------------
        # Fragment shader — Blinn-Phong per-fragment lighting
        # ------------------------------------------------------------------
        # This shader runs once per PIXEL (potentially millions of times per
        # frame) instead of once per vertex — much more expensive, but produces
        # smooth specular highlights that don't shift or disappear with vertex count.
        #
        # Half-vector calculation (eye-space):
        #   In eye-space the camera is always at (0,0,0), so the eye direction
        #   is always (0,0,-1). The half-vector H = normalize(L + Eye_dir).
        #
        # New uniforms vs Tutorial 05:
        #   Light_specular    - specular colour of the light (yellow here)
        #   Material_specular - how much specular light the material reflects
        #   Material_shininess - controls the size/sharpness of the highlight
        # ------------------------------------------------------------------
        fragment = shaders.compileShader(PHONG_WEIGHT_CALC + """
            uniform vec4  Global_ambient;
            uniform vec4  Light_ambient;
            uniform vec4  Light_diffuse;
            uniform vec4  Light_specular;
            uniform vec3  Light_location;
            uniform float Material_shininess;
            uniform vec4  Material_specular;
            uniform vec4  Material_ambient;
            uniform vec4  Material_diffuse;
            varying vec3  baseNormal;

            void main() {
                // Normalise interpolated normal (interpolation can shrink it)
                vec3 frag_normal = normalize(baseNormal);

                // Transform light direction into eye-space
                vec3 EC_Light_location = normalize(gl_NormalMatrix * Light_location);

                // Half-vector: bisector of light and eye directions (eye-space)
                // Eye direction in eye-space is always (0, 0, -1)
                vec3 Light_half = normalize(EC_Light_location - vec3(0.0, 0.0, -1.0));

                // Get diffuse and specular weights
                vec2 weights = phong_weightCalc(
                    EC_Light_location,
                    Light_half,
                    frag_normal,
                    Material_shininess
                );

                gl_FragColor = clamp(
                    (Global_ambient  * Material_ambient)
                  + (Light_ambient   * Material_ambient)
                  + (Light_diffuse   * Material_diffuse  * weights.x)
                  + (Light_specular  * Material_specular * weights.y),
                    0.0, 1.0
                );
            }
        """, GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vertex, fragment)

        # ------------------------------------------------------------------
        # Sphere geometry (indexed)
        # ------------------------------------------------------------------
        # coords_data: float32, shape (N, 8)
        #   [x, y, z, u, v, nx, ny, nz]
        #   position at offset 0, normal at offset 5*4=20 bytes
        #
        # indices_data: uint16, flat array of triangle vertex indices
        #
        # Two VBOs use different TARGETS:
        #   coords  → GL_ARRAY_BUFFER         (vertex data)
        #   indices → GL_ELEMENT_ARRAY_BUFFER  (index data)
        # Both can be bound at the same time without conflict!
        # ------------------------------------------------------------------
        coords_data, indices_data = generate_sphere(radius=1.0, stacks=32, slices=32)
        self.count = len(indices_data)

        self.coords  = vbo.VBO(coords_data,  target=GL_ARRAY_BUFFER)
        self.indices = vbo.VBO(indices_data, target=GL_ELEMENT_ARRAY_BUFFER)

        # stride: 8 floats × 4 bytes = 32 bytes per vertex record
        self.stride = coords_data.shape[1] * 4   # = 32

        # ------------------------------------------------------------------
        # Query uniform and attribute locations
        # ------------------------------------------------------------------
        for uniform_name in (
            'Global_ambient',
            'Light_ambient', 'Light_diffuse', 'Light_specular', 'Light_location',
            'Material_ambient', 'Material_diffuse',
            'Material_shininess', 'Material_specular',
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

        print("\n=== Tutorial 06: Specular Blinn-Phong + Indexed Sphere ===")
        print("OpenGL Version:", glGetString(GL_VERSION).decode())
        print(f"Sphere: {len(coords_data)} vertices, {self.count} indices")
        print(f"Stride: {self.stride} bytes, normal offset: {5 * 4} bytes")

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def Render(self):
        """Render the sphere with per-fragment Blinn-Phong lighting."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.0)

        glUseProgram(self.shader)

        try:
            # Bind BOTH VBOs — they go to different targets, no conflict
            self.coords.bind()   # → GL_ARRAY_BUFFER
            self.indices.bind()  # → GL_ELEMENT_ARRAY_BUFFER

            try:
                # -- Set uniforms --------------------------------------------
                glUniform4f(self.Global_ambient_loc,    0.05, 0.05, 0.05, 1.0)
                glUniform4f(self.Light_ambient_loc,      0.1,  0.1,  0.1, 1.0)
                glUniform4f(self.Light_diffuse_loc,     0.25, 0.25, 0.25, 1.0)
                # Yellowish specular — easy to see on the sphere surface
                glUniform4f(self.Light_specular_loc,    0.0,  1.0,  0.0, 1.0)
                # Light "just over the right shoulder" of the camera
                glUniform3f(self.Light_location_loc,    6.0,  2.0,  4.0)

                glUniform4f(self.Material_ambient_loc,   0.1,  0.1,  0.1, 1.0)
                glUniform4f(self.Material_diffuse_loc,  0.15, 0.15, 0.15, 1.0)
                # Bright white specular + very shiny surface
                glUniform4f(self.Material_specular_loc, 1.0,  1.0,  1.0, 1.0)
                # High shininess = small, sharp highlight
                glUniform1f(self.Material_shininess_loc, 0.95)

                # -- Bind attribute arrays -----------------------------------
                glEnableVertexAttribArray(self.Vertex_position_loc)
                glEnableVertexAttribArray(self.Vertex_normal_loc)

                # Position: first 3 floats, offset 0
                glVertexAttribPointer(
                    self.Vertex_position_loc,
                    3, GL_FLOAT, False, self.stride, self.coords
                )
                # Normal: 3 floats starting at byte 20 (after x,y,z,u,v)
                glVertexAttribPointer(
                    self.Vertex_normal_loc,
                    3, GL_FLOAT, False, self.stride, self.coords + (5 * 4)
                )

                # -- Indexed draw call ---------------------------------------
                # glDrawElements reads vertex indices from GL_ELEMENT_ARRAY_BUFFER
                # and uses them to index into GL_ARRAY_BUFFER for vertex data.
                # This allows vertices to be shared between triangles.
                glDrawElements(
                    GL_TRIANGLES,       # primitive type
                    self.count,         # number of indices
                    GL_UNSIGNED_SHORT,  # index data type (uint16)
                    self.indices        # pointer (uses bound ELEMENT_ARRAY_BUFFER)
                )

            finally:
                self.coords.unbind()    # unbind GL_ARRAY_BUFFER
                self.indices.unbind()   # unbind GL_ELEMENT_ARRAY_BUFFER
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
        print("Observe the yellow specular highlight on the sphere (Blinn-Phong).")

        while self.running:
            self.handle_events()
            self.Render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("Tutorial 06: Specular Highlights, Indexed Geometry")
    print("=" * 60)
    context = TestContext()
    context.main_loop()
