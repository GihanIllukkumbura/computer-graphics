import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo

def generate_sphere(radius=1.0, stacks=32, slices=32):
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

class TestContext:
    LIGHT_COUNT = 3
    LIGHT_SIZE = 5

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True

    def init_display(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 09: Point Lights")

        glClearColor(0.05, 0.05, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def OnInit(self):
        lightConst = """
        const int LIGHT_COUNT = %s;
        const int LIGHT_SIZE = %s;
        const int AMBIENT = 0;
        const int DIFFUSE = 1;
        const int SPECULAR = 2;
        const int POSITION = 3;
        const int ATTENUATION = 4;
        uniform vec4 lights[ LIGHT_COUNT*LIGHT_SIZE ];
        varying vec3 EC_Light_half[LIGHT_COUNT];
        varying vec3 EC_Light_location[LIGHT_COUNT];
        varying float Light_distance[LIGHT_COUNT];
        varying vec3 baseNormal;
        """ % (self.LIGHT_COUNT, self.LIGHT_SIZE)

        phong_weightCalc = """
        vec3 phong_weightCalc(
            in vec3 light_pos, // light position/direction
            in vec3 half_light, // half-way vector between light and view
            in vec3 frag_normal, // geometry normal
            in float shininess, // shininess exponent
            in float distance, // distance for attenuation calculation...
            in vec4 attenuations // attenuation parameters...
        ) {
            float n_dot_pos = max( 0.0, dot( frag_normal, light_pos ));
            float n_dot_half = 0.0;
            float attenuation = 1.0;
            if (n_dot_pos > -.05) {
                n_dot_half = pow(max(0.0,dot( half_light, frag_normal )), shininess);
                if (distance != 0.0) {
                    attenuation = clamp(
                        0.0, 1.0, 1.0 / (
                            attenuations.x +
                            (attenuations.y * distance) +
                            (attenuations.z * distance * distance)
                        )
                    );
                    n_dot_pos *= attenuation;
                    n_dot_half *= attenuation;
                }
            }
            return vec3( attenuation, n_dot_pos, n_dot_half);
        }
        """

        phong_preCalc = """
        void phong_preCalc(
            in vec3 vertex_position,
            in vec4 light_position,
            out float light_distance,
            out vec3 ec_light_location,
            out vec3 ec_light_half
        ) {
            if (light_position.w == 0.0) {
                ec_light_location = normalize( gl_NormalMatrix * light_position.xyz );
                light_distance = 0.0;
            } else {
                vec3 ms_vec = (light_position.xyz - vertex_position);
                vec3 light_direction = gl_NormalMatrix * ms_vec;
                ec_light_location = normalize( light_direction );
                light_distance = abs(length( ms_vec ));
            }
            ec_light_half = normalize(ec_light_location + vec3( 0,0,1 ));
        }
        """
        
        light_preCalc = """
        void light_preCalc( in vec3 vertex_position ) {
            for (int i = 0; i< LIGHT_COUNT; i++ ) {
                int j = i * LIGHT_SIZE;
                phong_preCalc(
                    vertex_position,
                    lights[j+POSITION],
                    Light_distance[i],
                    EC_Light_location[i],
                    EC_Light_half[i]
                );
            }
        }
        """

        vertex = shaders.compileShader(
            lightConst + phong_preCalc + light_preCalc +
        """
        attribute vec3 Vertex_position;
        attribute vec3 Vertex_normal;
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * vec4(Vertex_position, 1.0);
            baseNormal = gl_NormalMatrix * normalize(Vertex_normal);
            light_preCalc(Vertex_position);
        }""", GL_VERTEX_SHADER)
        
        fragment = shaders.compileShader(
            lightConst + phong_weightCalc + """
        struct Material {
            vec4 ambient;
            vec4 diffuse;
            vec4 specular;
            float shininess;
        };
        uniform Material material;
        uniform vec4 Global_ambient;
        void main() {
            vec4 fragColor = Global_ambient * material.ambient;
            int i,j;
            vec3 normal = normalize(baseNormal);
            for (i=0; i<LIGHT_COUNT; i++) {
                j = i* LIGHT_SIZE;
                vec3 weights = phong_weightCalc(
                    normalize(EC_Light_location[i]),
                    normalize(EC_Light_half[i]),
                    normal,
                    material.shininess,
                    abs(Light_distance[i]),
                    lights[j+ATTENUATION]
                );
                fragColor = (
                    fragColor
                    + (lights[j+AMBIENT] * material.ambient * weights.x)
                    + (lights[j+DIFFUSE] * material.diffuse * weights.y)
                    + (lights[j+SPECULAR] * material.specular * weights.z)
                );
            }
            gl_FragColor = fragColor;
        }
        """, GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(vertex, fragment)
        
        coords_data, indices_data = generate_sphere(radius=1.0, stacks=32, slices=32)
        self.count = len(indices_data)
        
        self.coords  = vbo.VBO(coords_data,  target=GL_ARRAY_BUFFER)
        self.indices = vbo.VBO(indices_data, target=GL_ELEMENT_ARRAY_BUFFER)
        self.stride = coords_data.shape[1] * 4

        self.uniform_locations = {}
        for uniform_name in (
            'Global_ambient',
            'material.ambient', 'material.diffuse',
            'material.specular', 'material.shininess',
        ):
            loc = glGetUniformLocation(self.shader, uniform_name)
            self.uniform_locations[uniform_name] = loc
            
        self.uniform_locations['lights'] = glGetUniformLocation(self.shader, 'lights')
        
        for attr_name in ('Vertex_position', 'Vertex_normal'):
            loc = glGetAttribLocation(self.shader, attr_name)
            setattr(self, attr_name + '_loc', loc)

        self.UNIFORM_VALUES = [
            ('Global_ambient',(0.05, 0.05, 0.05, 1.0)),
            ('material.ambient',(0.2, 0.2, 0.2, 1.0)),
            ('material.diffuse',(0.5, 0.5, 0.5, 1.0)),
            ('material.specular',(0.8, 0.8, 0.8, 1.0)),
            ('material.shininess', 2.0),
        ]
        
        self.LIGHTS = np.array([
            0.05,0.05,0.05,1.0, 0.1,0.8,0.1,1.0, 0.0,1.0,0.0,1.0, 2.5,2.5,2.5,1.0, 0.0,0.15,0.0,1.0,
            0.05,0.05,0.05,1.0, 0.8,0.1,0.1,1.0, 1.0,0.0,0.0,1.0, -2.5,2.5,2.5,1.0, 0.0,0.0,0.15,1.0,
            0.05,0.05,0.05,1.0, 0.1,0.1,0.8,1.0, 0.0,0.0,1.0,1.0, 0.0,-3.06,3.06,1.0, 0.15,0.0,0.0,1.0,
        ], dtype='f')

    def Render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.0)
        
        glUseProgram(self.shader)
        try:
            self.coords.bind()
            self.indices.bind()
            try:
                glUniform4fv(self.uniform_locations['lights'], self.LIGHT_COUNT * self.LIGHT_SIZE, self.LIGHTS)
                
                for uniform, value in self.UNIFORM_VALUES:
                    loc = self.uniform_locations.get(uniform)
                    if loc not in (None, -1):
                        if isinstance(value, tuple):
                            if len(value) == 4:
                                glUniform4f(loc, *value)
                            elif len(value) == 3:
                                glUniform3f(loc, *value)
                        else:
                            glUniform1f(loc, value)

                glEnableVertexAttribArray(self.Vertex_position_loc)
                glEnableVertexAttribArray(self.Vertex_normal_loc)

                glVertexAttribPointer(self.Vertex_position_loc, 3, GL_FLOAT, False, self.stride, self.coords)
                glVertexAttribPointer(self.Vertex_normal_loc, 3, GL_FLOAT, False, self.stride, self.coords + (5 * 4))

                glDrawElements(GL_TRIANGLES, self.count, GL_UNSIGNED_SHORT, self.indices)

            finally:
                self.coords.unbind()
                self.indices.unbind()
                glDisableVertexAttribArray(self.Vertex_position_loc)
                glDisableVertexAttribArray(self.Vertex_normal_loc)
        finally:
            glUseProgram(0)

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
        while self.running:
            self.handle_events()
            self.Render()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    context = TestContext()
    context.main_loop()
