import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo

def generate_sphere(radius=1.0, stacks=16, slices=16):
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
    LIGHT_SIZE = 7

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.running = True

    def init_display(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Tutorial 11: Instanced Geometry")

        glClearColor(1, 1, 1, 1.0)
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
        const int SPOT_PARAMS = 5;
        const int SPOT_DIR = 6;
        uniform vec4 lights[ LIGHT_COUNT*LIGHT_SIZE ];
        varying vec3 EC_Light_half[LIGHT_COUNT];
        varying vec3 EC_Light_location[LIGHT_COUNT];
        varying float Light_distance[LIGHT_COUNT];
        varying vec3 baseNormal;
        """ % (self.LIGHT_COUNT, self.LIGHT_SIZE)

        phong_weightCalc = """
        vec3 phong_weightCalc(
            in vec3 light_pos, 
            in vec3 half_light, 
            in vec3 frag_normal, 
            in float shininess, 
            in float distance, 
            in vec4 attenuations, 
            in vec4 spot_params, 
            in vec4 spot_direction 
        ) {
            float n_dot_pos = max( 0.0, dot(frag_normal, light_pos) );
            float n_dot_half = 0.0;
            float attenuation = 1.0;
            if (n_dot_pos > -.05) {
                float spot_effect = 1.0;
                if (spot_params.w != 0.0) {
                    float spot_cos = dot(
                        gl_NormalMatrix * normalize(spot_direction.xyz),
                        normalize(-light_pos)
                    );
                    if (spot_cos <= spot_params.x) {
                        return vec3( 0.0, 0.0, 0.0 );
                    } else {
                        if (spot_cos == 1.0) {
                            spot_effect = 1.0;
                        } else {
                            spot_effect = pow(max(0.0001, (1.0-spot_params.x)/(1.0-spot_cos)), spot_params.y);
                        }
                    }
                }
                n_dot_half = pow(max(0.0,dot(half_light, frag_normal)), shininess);
                if (distance != 0.0) {
                    float calc_attenuation = 1.0/(
                        attenuations.x +
                        (attenuations.y * distance) +
                        (attenuations.z * distance * distance)
                    );
                    n_dot_half *= spot_effect;
                    n_dot_pos *= calc_attenuation;
                    n_dot_half *= calc_attenuation;
                    attenuation = calc_attenuation;
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
            "#extension GL_ARB_draw_instanced : enable\n" +
            lightConst + phong_preCalc + light_preCalc +
        """
        attribute vec3 Vertex_position;
        attribute vec3 Vertex_normal;
        uniform samplerBuffer offsets_table;
        
        void main() {
            vec3 offset = texelFetch( offsets_table, gl_InstanceIDARB ).xyz;
            vec3 final_position = Vertex_position + offset;
            
            gl_Position = gl_ModelViewProjectionMatrix * vec4(final_position, 1.0);
            baseNormal = gl_NormalMatrix * normalize(Vertex_normal);
            light_preCalc(final_position);
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
                    lights[j+ATTENUATION],
                    lights[j+SPOT_PARAMS],
                    lights[j+SPOT_DIR]
                );
                fragColor = (
                    fragColor
                    + (lights[j+AMBIENT] * material.ambient * weights.x)
                    + (lights[j+DIFFUSE] * material.diffuse * weights.y)
                    + (lights[j+SPECULAR] * material.specular * weights.z)
                );
            }
            gl_FragColor = clamp(fragColor, 0.0, 1.0);
        }
        """, GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(vertex, fragment)
        
        # Instantiate Texture Buffer
        hardlimit = glGetIntegerv(GL_MAX_TEXTURE_BUFFER_SIZE)
        count = min((15000, hardlimit // 16))
        
        scale = np.array([40, 40, 40, 0], dtype='f')
        offset = np.array([-20, -20, -40, 1], dtype='f')
        self.offset_array = (np.random.random(size=(count, 4)).astype('f') * scale) + offset
        self.instance_count = count
        
        self.tbo_vbo = glGenBuffers(1)
        glBindBuffer(GL_TEXTURE_BUFFER, self.tbo_vbo)
        glBufferData(GL_TEXTURE_BUFFER, self.offset_array.nbytes, self.offset_array, GL_STATIC_DRAW)
        
        self.tbo_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_BUFFER, self.tbo_tex)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, self.tbo_vbo)
        
        glBindBuffer(GL_TEXTURE_BUFFER, 0)
        glBindTexture(GL_TEXTURE_BUFFER, 0)
        
        # Instantiate geometry
        coords_data, indices_data = generate_sphere(radius=0.25, stacks=8, slices=8)
        self.count = len(indices_data)
        
        self.coords  = vbo.VBO(coords_data,  target=GL_ARRAY_BUFFER)
        self.indices = vbo.VBO(indices_data, target=GL_ELEMENT_ARRAY_BUFFER)
        self.stride = coords_data.shape[1] * 4

        self.uniform_locations = {}
        for uniform_name in (
            'Global_ambient',
            'material.ambient', 'material.diffuse',
            'material.specular', 'material.shininess',
            'offsets_table'
        ):
            loc = glGetUniformLocation(self.shader, uniform_name)
            self.uniform_locations[uniform_name] = loc
            
        self.uniform_locations['lights'] = glGetUniformLocation(self.shader, 'lights')
        
        for attr_name in ('Vertex_position', 'Vertex_normal'):
            loc = glGetAttribLocation(self.shader, attr_name)
            setattr(self, attr_name + '_loc', loc)

        self.UNIFORM_VALUES = [
            ('Global_ambient',(0.1, 0.1, 0.1, 1.0)),
            ('material.ambient',(0.1, 0.1, 0.1, 1.0)),
            ('material.diffuse',(1.0, 1.0, 1.0, 1.0)),
            ('material.specular',(0.4, 0.4, 0.4, 1.0)),
            ('material.shininess', 0.5),
        ]
        
        self.LIGHTS = np.array([
            0.05,0.05,0.05,1.0, 0.1,0.8,0.1,1.0, 0.0,0.05,0.0,1.0, 2.5,3.5,2.5,1.0, 0.0,1.0,1.0,1.0, math.cos(.25),1.0,0.0,1.0, -8,-20,-8.0,1.0,
            0.05,0.05,0.05,1.0, 0.8,0.1,0.1,1.0, 0.25,0.0,0.0,1.0, -2.5,2.5,2.5,1.0, 0.0,0.0,.125,1.0, math.cos(.25),1.25,0.0,1.0, 2.5,-5.5,-2.5,1.0,
            0.05,0.05,0.05,1.0, 0.1,0.1,1.0,1.0, 0.0,.25,.25,1.0, 0.0,-3.06,3.06,1.0, 2.0,0.0,0.0,1.0, math.cos(.15),.75,0.0,1.0, 0.0,3.06,-3.06,1.0,
        ], dtype='f')

        print("Each sphere has %d triangles, rendering %d instances -> %d triangles total" % (self.count//3, self.instance_count, (self.count//3)*self.instance_count))

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
                            
                # Bind texture buffer
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_BUFFER, self.tbo_tex)
                if self.uniform_locations.get('offsets_table') not in (None, -1):
                    glUniform1i(self.uniform_locations['offsets_table'], 0)

                glEnableVertexAttribArray(self.Vertex_position_loc)
                glEnableVertexAttribArray(self.Vertex_normal_loc)

                glVertexAttribPointer(self.Vertex_position_loc, 3, GL_FLOAT, False, self.stride, self.coords)
                glVertexAttribPointer(self.Vertex_normal_loc, 3, GL_FLOAT, False, self.stride, self.coords + (5 * 4))

                # DRAW INSTANCED
                if bool(glDrawElementsInstanced):
                    glDrawElementsInstanced(GL_TRIANGLES, self.count, GL_UNSIGNED_SHORT, self.indices, self.instance_count)
                else:
                    glDrawElementsInstancedARB(GL_TRIANGLES, self.count, GL_UNSIGNED_SHORT, self.indices, self.instance_count)

            finally:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_BUFFER, 0)
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
