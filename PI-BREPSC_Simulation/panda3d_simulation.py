from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, AmbientLight, DirectionalLight, LVector4, CardMaker, NodePath, GeomVertexWriter, GeomVertexFormat, GeomVertexData, GeomTriangles, Geom, GeomNode, Point3, LColor
import random

class TrafficLight:
    def __init__(self, app, pos, hpr=(0, 0, 0)):
        self.app = app
        self.model = NodePath('traffic_light')
        self.model.reparentTo(app.render)
        self.model.setPos(pos)
        self.model.setHpr(hpr)

        # Pole
        pole_length = 20 # Much taller
        pole_width = 0.5
        pole_depth = 0.5
        pole_node = app.make_box('pole', pole_width, pole_depth, pole_length, (0.3, 0.3, 0.3, 1))
        pole_node.reparentTo(self.model)
        pole_node.setPos(0, 0, 0) # Base of pole at model's origin

        # Light Housing (rectangular box, horizontal)
        housing_length = 8 # Length along Y axis (road direction)
        housing_width = 3 # Width along X axis
        housing_height = 2.5 # Height along Z axis
        housing_node = app.make_box('housing', housing_width, housing_length, housing_height, (0.1, 0.1, 0.1, 1))
        housing_node.reparentTo(self.model)
        housing_node.setPos(0, 0, pole_length - housing_height/2) # Position at top of pole, centered
        # Rotate housing to be horizontal to the road (along Y axis if pole is along Z)
        housing_node.setHpr(90, 0, 0) # Rotate 90 degrees around Z to make it horizontal to Y-axis

        # Lights (spheres within housing)
        light_radius = 0.7
        light_spacing = 2.5

        self.red_light = self.app.loader.loadModel("models/misc/sphere")
        self.red_light.reparentTo(housing_node)
        self.red_light.setScale(light_radius)
        self.red_light.setPos(0, -light_spacing, housing_height / 2 + 0.1) # Relative to housing_node, arranged along Y
        self.red_light.setColor(LColor(1, 0, 0, 0.3)) # Default off (dim red)

        self.yellow_light = self.app.loader.loadModel("models/misc/sphere")
        self.yellow_light.reparentTo(housing_node)
        self.yellow_light.setScale(light_radius)
        self.yellow_light.setPos(0, 0, housing_height / 2 + 0.1)
        self.yellow_light.setColor(LColor(1, 1, 0, 0.3)) # Default off (dim yellow)

        self.green_light = self.app.loader.loadModel("models/misc/sphere")
        self.green_light.reparentTo(housing_node)
        self.green_light.setScale(light_radius)
        self.green_light.setPos(0, light_spacing, housing_height / 2 + 0.1)
        self.green_light.setColor(LColor(0, 1, 0, 0.3)) # Default off (dim green)

        self.set_light('red') # Initial state

    def set_light(self, color):
        # Turn all lights dim
        self.red_light.setColor(LColor(1, 0, 0, 0.3))
        self.yellow_light.setColor(LColor(1, 1, 0, 0.3))
        self.green_light.setColor(LColor(0, 1, 0, 0.3))

        # Turn on the specified light
        if color == 'red':
            self.red_light.setColor(LColor(1, 0, 0, 1))
        elif color == 'yellow':
            self.yellow_light.setColor(LColor(1, 1, 0, 1))
        elif color == 'green':
            self.green_light.setColor(LColor(0, 1, 0, 1))


class PedestrianSignal:
    def __init__(self, app, pos, hpr=(0, 0, 0)):
        self.app = app
        self.model = NodePath('pedestrian_signal')
        self.model.reparentTo(app.render)
        self.model.setPos(pos)
        self.model.setHpr(hpr)

        # Pole
        pole_length = 5
        pole_width = 0.3
        pole_depth = 0.3
        ped_pole_node = app.make_box('ped_pole', pole_width, pole_depth, pole_length, (0.3, 0.3, 0.3, 1))
        ped_pole_node.reparentTo(self.model)
        ped_pole_node.setPos(0, 0, 0)

        # Signal Housing (rectangular box, vertical)
        housing_width = 1.5 # X-dim
        housing_height = 4 # Z-dim
        housing_depth = 0.5 # Y-dim
        ped_housing_node = app.make_box('ped_housing', housing_width, housing_depth, housing_height, (0.1, 0.1, 0.1, 1))
        ped_housing_node.reparentTo(self.model)
        ped_housing_node.setPos(0, 0, pole_length) # At top of pole

        # WALK/DONT WALK panels (simple quads)
        panel_width = 1.2
        panel_height = 1.5
        panel_z_spacing = 2

        # DONT WALK (Red hand or text)
        cm_dont_walk = CardMaker('dont_walk_panel')
        cm_dont_walk.setFrame(-panel_width/2, panel_width/2, -panel_height/2, panel_height/2)
        self.dont_walk_panel = ped_housing_node.attachNewNode(cm_dont_walk.generate())
        self.dont_walk_panel.setPos(0, housing_depth/2 + 0.05, housing_height - 1.5) # Relative to housing
        self.dont_walk_panel.setColor(LColor(1, 0, 0, 0.5)) # Dim red
        self.dont_walk_panel.setHpr(0, -90, 0) # Face forward

        # WALK (Green person or text)
        cm_walk = CardMaker('walk_panel')
        cm_walk.setFrame(-panel_width/2, panel_width/2, -panel_height/2, panel_height/2)
        self.walk_panel = ped_housing_node.attachNewNode(cm_walk.generate())
        self.walk_panel.setPos(0, housing_depth/2 + 0.05, housing_height - 3.5) # Relative to housing
        self.walk_panel.setColor(LColor(0, 1, 0, 0.5)) # Dim green
        self.walk_panel.setHpr(0, -90, 0) # Face forward

        self.set_signal('dont_walk') # Initial state

    def set_signal(self, state):
        if state == 'walk':
            self.walk_panel.setColor(LColor(0, 1, 0, 1)) # Bright green
            self.dont_walk_panel.setColor(LColor(1, 0, 0, 0.2)) # Dim red
        elif state == 'dont_walk':
            self.walk_panel.setColor(LColor(0, 1, 0, 0.2)) # Dim green
            self.dont_walk_panel.setColor(LColor(1, 0, 0, 1)) # Bright red


class Car:
    def __init__(self, app, car_id, start_y, lane_x):
        self.app = app
        self.car_id = car_id
        self.speed = 0.5 # Units per frame, adjust as needed for simulation speed
        self.length = 5
        self.width = 2.5
        self.height = 2
        self.lane_x = lane_x
        self.current_y = start_y
        self.color = (random.random(), random.random(), random.random(), 1) # Random color for diversity

        # Create a simple 3D box model for the car
        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('car_data', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        # Define vertices for a box
        # Front face
        vertex.addData3f(-self.width/2, self.length/2, 0)
        vertex.addData3f(self.width/2, self.length/2, 0)
        vertex.addData3f(self.width/2, self.length/2, self.height)
        vertex.addData3f(-self.width/2, self.length/2, self.height)
        # Back face
        vertex.addData3f(self.width/2, -self.length/2, 0)
        vertex.addData3f(-self.width/2, -self.length/2, 0)
        vertex.addData3f(-self.width/2, -self.length/2, self.height)
        vertex.addData3f(self.width/2, -self.length/2, self.height)
        # ... and so on for other faces (left, right, top, bottom)
        # For simplicity, let's just define the top and bottom for now for the rectangular shape
        # In a real scenario, all 6 faces would be defined with normals and colors.

        # Top face
        vertex.addData3f(-self.width/2, self.length/2, self.height)
        vertex.addData3f(self.width/2, self.length/2, self.height)
        vertex.addData3f(self.width/2, -self.length/2, self.height)
        vertex.addData3f(-self.width/2, -self.length/2, self.height)
        # Bottom face
        vertex.addData3f(-self.width/2, -self.length/2, 0)
        vertex.addData3f(self.width/2, -self.length/2, 0)
        vertex.addData3f(self.width/2, self.length/2, 0)
        vertex.addData3f(-self.width/2, self.length/2, 0)
        
        # Add more vertices for a full box
        # Right face
        vertex.addData3f(self.width/2, self.length/2, 0)
        vertex.addData3f(self.width/2, -self.length/2, 0)
        vertex.addData3f(self.width/2, -self.length/2, self.height)
        vertex.addData3f(self.width/2, self.length/2, self.height)
        # Left face
        vertex.addData3f(-self.width/2, -self.length/2, 0)
        vertex.addData3f(-self.width/2, self.length/2, 0)
        vertex.addData3f(-self.width/2, self.length/2, self.height)
        vertex.addData3f(-self.width/2, -self.length/2, self.height)


        # Add colors for all vertices
        for _ in range(24): # 6 faces * 4 vertices per face
            color.addData4f(*self.color)
        
        # Define triangles for top and bottom faces (using quad definition)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Top face
        prim.addVertices(8, 9, 10)
        prim.addVertices(8, 10, 11)
        # Bottom face
        prim.addVertices(12, 13, 14)
        prim.addVertices(12, 14, 15)
        # Front Face (0,1,2,3)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)
        # Back Face (4,5,6,7)
        prim.addVertices(4, 5, 6)
        prim.addVertices(4, 6, 7)
        # Right Face (16,17,18,19)
        prim.addVertices(16, 17, 18)
        prim.addVertices(16, 18, 19)
        # Left Face (20,21,22,23)
        prim.addVertices(20, 21, 22)
        prim.addVertices(20, 22, 23)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode('car_node')
        node.addGeom(geom)
        self.model = app.render.attachNewNode(node)

        self.model.setPos(self.lane_x, self.current_y, self.height / 2) # Center of the car model

    def update(self):
        self.current_y += self.speed
        self.model.setY(self.current_y)

class Pedestrian:
    def __init__(self, app, pedestrian_id, start_pos, target_pos, current_crosswalk_idx):
        self.app = app
        self.pedestrian_id = pedestrian_id
        self.speed = 0.2 # Slower than cars
        self.radius = 0.5 # Approximate size
        self.height = 1.8
        self.current_pos = start_pos
        self.target_pos = target_pos
        self.current_crosswalk_idx = current_crosswalk_idx # 0 for first, 1 for second
        self.is_crossing = False
        self.color = (random.random(), random.random(), random.random(), 1)

        # Create a simple humanoid-like model for the pedestrian
        self.model = NodePath('pedestrian_{}'.format(self.pedestrian_id))
        self.model.reparentTo(app.render)
        self.model.setPos(self.current_pos)

        # Body (box)
        body_width = 0.6
        body_depth = 0.4
        body_height = 1.2
        body_node = self.app.make_box('pedestrian_body', body_width, body_depth, body_height, self.color)
        body_node.reparentTo(self.model)
        body_node.setPos(0, 0, 0) # Base of body at pedestrian model's origin (which is at ground level)

        # Head (sphere)
        head_radius = 0.3
        head_node = self.app.loader.loadModel("models/misc/sphere")
        head_node.reparentTo(self.model)
        head_node.setScale(head_radius)
        head_node.setPos(0, 0, body_height + head_radius * 0.5) # Position on top of body
        head_node.setColor(self.color)

        # Adjust the overall pedestrian model position slightly for proper ground alignment
        self.model.setZ(self.model.getZ() - 0.9) # Adjust to account for model origin at feet

    def update(self):
        if self.is_crossing:
            direction = self.target_pos - self.current_pos
            if direction.length() > self.speed:
                direction.normalize()
                self.current_pos += direction * self.speed
                self.model.setPos(self.current_pos)
            else:
                self.current_pos = self.target_pos
                self.model.setPos(self.current_pos)
                self.is_crossing = False # Finished crossing
                # This pedestrian will be marked for removal and respawn by the main loop
        else:
            # Pedestrian is waiting. No movement until crossing flag is set.
            pass


class Panda3DSimulation(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.accept('escape', self.userExit) # Allow closing with Escape key

        # Set up the camera
        self.cam.setPos(0, -100, 50)  # Position the camera
        self.cam.lookAt(0, 0, 0)     # Look at the origin

        # Adjust camera for an isometric-like view, similar to the reference image
        self.cam.setPos(0, -60, 45) # Adjusted position: further back, higher, but less steep than default
        self.cam.lookAt(0, 0, 0)    # Still look at the origin/intersection center
        self.camLens.setFov(70) # Adjust field of view slightly

        # Define core simulation dimensions early
        self.road_length = 150 # Make sure this matches the road_length in create_environment
        self.lane_positions = [-7.5, 7.5] # Example lane positions (adjust based on road_width)

        # Set up ambient light
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(LVector4(0.6, 0.6, 0.6, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        # Set up directional light
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(0, 45, -45))
        directionalLight.setColor(LVector4(0.8, 0.8, 0.8, 1))
        directionalLightNP = self.render.attachNewNode(directionalLight)
        self.render.setLight(directionalLightNP)

        # Create a basic ground plane
        self.create_ground()
        self.create_environment()

        self.cars = []
        self.next_car_id = 0
        self.spawn_interval = 2 # How often to try and spawn a car (in seconds)
        self.time_since_last_spawn = 0

        self.pedestrians = []
        self.next_pedestrian_id = 0
        # Define crosswalk coordinates based on create_environment
        # Crosswalk 1 (south)
        self.crosswalk_coords = [
            {'center_y': -self.road_length / 4, 'x_range': (-5, 5), 'z': 0.01},
            # Crosswalk 2 (north)
            {'center_y': self.road_length / 4, 'x_range': (-5, 5), 'z': 0.01}
        ]
        self.wait_area_x_offset = (30 / 2 + (30 + 10) / 2) # road_width/2 + wait_area_width/2
        self.pedestrian_spawn_interval = 3
        self.time_since_last_ped_spawn = 0

        # Traffic and Pedestrian Signals
        # Assuming one intersection for now, with signals for both directions.
        # Position traffic light to the right of the road, facing cars moving along Y axis
        # Position pedestrian signal next to the crosswalk

        # Traffic Light for the first crosswalk (south)
        traffic_light_pos = Vec3(10, -self.road_length / 4 - 15, 0) # Position to the right, slightly behind crosswalk
        traffic_light_hpr = (0, 0, 0) # Facing down the road
        self.traffic_light = TrafficLight(self, traffic_light_pos, traffic_light_hpr)

        # Pedestrian Signal for the first crosswalk (south)
        ped_signal_pos = Vec3(-self.wait_area_x_offset + 5, -self.road_length / 4 - 5, 0) # Near west wait area
        ped_signal_hpr = (90, 0, 0) # Facing the pedestrians
        self.pedestrian_signal = PedestrianSignal(self, ped_signal_pos, ped_signal_hpr)

        self.signal_cycle_duration = 10 # seconds for a full cycle (red+green for car)
        self.red_light_duration = 5
        self.green_light_duration = 5
        self.current_signal_time = 0
        self.current_traffic_state = 'red' # Initial traffic state
        self.current_ped_state = 'dont_walk' # Initial pedestrian state

        self.spawn_initial_cars()
        self.spawn_initial_pedestrians()

        # Setup the main simulation update task
        self.taskMgr.add(self.update_simulation, "updateSimulation")
        self.taskMgr.add(self.cycle_traffic_lights, "cycleTrafficLights")

    def create_ground(self):
        # Create a simple plane for the ground
        # For simplicity, we'll use a CardMaker to create a flat quad
        cm = CardMaker('ground')
        cm.setFrame(-50, 50, -50, 50) # Adjust size as needed
        ground = self.render.attachNewNode(cm.generate())
        ground.setPos(0, 0, -0.1) # Slightly below z=0 to avoid z-fighting with future objects
        ground.setColor(0.3, 0.6, 0.3, 1) # Green ground

    def make_box(self, name, lx, ly, lz, color=(1,1,1,1)):
        # Creates a box of size (lx, ly, lz) with its origin at (0,0,0) (bottom center)
        from panda3d.core import GeomVertexFormat, GeomVertexData, GeomTriangles, Geom, GeomNode, GeomVertexWriter
        from panda3d.core import Point3

        format = GeomVertexFormat.getV3n3c4() # position, normal, color
        vdata = GeomVertexData(name, format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color_writer = GeomVertexWriter(vdata, 'color')

        # Vertices for a box of size (lx, ly, lz) with origin at bottom center
        # x: -lx/2 to lx/2, y: -ly/2 to ly/2, z: 0 to lz

        # Bottom face (z=0)
        p0 = Point3(-lx/2, -ly/2, 0)
        p1 = Point3( lx/2, -ly/2, 0)
        p2 = Point3( lx/2,  ly/2, 0)
        p3 = Point3(-lx/2,  ly/2, 0)
        # Top face (z=lz)
        p4 = Point3(-lx/2, -ly/2, lz)
        p5 = Point3( lx/2, -ly/2, lz)
        p6 = Point3( lx/2,  ly/2, lz)
        p7 = Point3(-lx/2,  ly/2, lz)

        # Back face (y = -ly/2)
        vertex.addData3f(p0) ; normal.addData3f(0,-1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p1) ; normal.addData3f(0,-1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p5) ; normal.addData3f(0,-1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p4) ; normal.addData3f(0,-1,0) ; color_writer.addData4f(*color)
        # Front face (y = ly/2)
        vertex.addData3f(p3) ; normal.addData3f(0,1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p2) ; normal.addData3f(0,1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p6) ; normal.addData3f(0,1,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p7) ; normal.addData3f(0,1,0) ; color_writer.addData4f(*color)
        # Left face (x = -lx/2)
        vertex.addData3f(p0) ; normal.addData3f(-1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p3) ; normal.addData3f(-1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p7) ; normal.addData3f(-1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p4) ; normal.addData3f(-1,0,0) ; color_writer.addData4f(*color)
        # Right face (x = lx/2)
        vertex.addData3f(p1) ; normal.addData3f(1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p5) ; normal.addData3f(1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p6) ; normal.addData3f(1,0,0) ; color_writer.addData4f(*color)
        vertex.addData3f(p2) ; normal.addData3f(1,0,0) ; color_writer.addData4f(*color)
        # Bottom face (z = 0)
        vertex.addData3f(p0) ; normal.addData3f(0,0,-1) ; color_writer.addData4f(*color)
        vertex.addData3f(p1) ; normal.addData3f(0,0,-1) ; color_writer.addData4f(*color)
        vertex.addData3f(p2) ; normal.addData3f(0,0,-1) ; color_writer.addData4f(*color)
        vertex.addData3f(p3) ; normal.addData3f(0,0,-1) ; color_writer.addData4f(*color)
        # Top face (z = lz)
        vertex.addData3f(p4) ; normal.addData3f(0,0,1) ; color_writer.addData4f(*color)
        vertex.addData3f(p5) ; normal.addData3f(0,0,1) ; color_writer.addData4f(*color)
        vertex.addData3f(p6) ; normal.addData3f(0,0,1) ; color_writer.addData4f(*color)
        vertex.addData3f(p7) ; normal.addData3f(0,0,1) ; color_writer.addData4f(*color)

        prim = GeomTriangles(Geom.UHStatic)

        # Indices for each face (using 4 vertices per face to create 2 triangles)
        # Each quad (v0, v1, v2, v3) becomes two triangles (v0, v1, v2) and (v0, v2, v3)
        indices = [
            # Back
            0,1,2,  0,2,3,
            # Front
            4,5,6,  4,6,7,
            # Left
            8,9,10, 8,10,11,
            # Right
            12,13,14, 12,14,15,
            # Bottom
            16,17,18, 16,18,19,
            # Top
            20,21,22, 20,22,23
        ]

        for i in indices:
            prim.addVertex(i)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode(name)
        node.addGeom(geom)
        
        return NodePath(node)

    def create_environment(self):
        # Define dimensions and positions based on common simulation layouts
        road_width = 30
        road_length = 150 # Make it longer to see cars moving off screen
        crosswalk_width = 10
        crosswalk_length = road_width + 10 # Wider than road
        wait_area_depth = 15
        wait_area_width = road_width + 10 # Same width as crosswalk

        # Create Road
        cm_road = CardMaker('road')
        cm_road.setFrame(-road_width / 2, road_width / 2, -road_length / 2, road_length / 2)
        road = self.render.attachNewNode(cm_road.generate())
        road.setPos(0, 0, 0) # On the ground plane
        road.setColor(0.2, 0.2, 0.2, 1) # Dark grey for road

        # Add a yellow lane line down the center of the road
        lane_line_width = 0.5
        lane_line_length = road_length
        num_dashes = 15
        dash_length = 5
        gap_length = (lane_line_length - num_dashes * dash_length) / (num_dashes - 1)

        for i in range(num_dashes):
            cm_dash = CardMaker('lane_dash_{}'.format(i))
            cm_dash.setFrame(-lane_line_width / 2, lane_line_width / 2, -dash_length / 2, dash_length / 2)
            dash = self.render.attachNewNode(cm_dash.generate())
            dash.setHpr(90, 0, 0) # Rotate to lay flat on road
            # Position dashes along the Y-axis
            dash_y_pos = -lane_line_length / 2 + (i * (dash_length + gap_length)) + dash_length / 2
            dash.setPos(0, dash_y_pos, 0.02) # Slightly above road to avoid z-fighting
            dash.setColor(1, 1, 0, 1) # Yellow


        # Create Crosswalks (assuming two, one on each side of the intersection)
        # Instead of solid blocks, create stripes
        crosswalk_width = 10
        crosswalk_length = road_width + 10 # Wider than road
        stripe_width = 1 # Width of each white stripe
        stripe_spacing = 1 # Space between stripes
        num_stripes = int(crosswalk_length / (stripe_width + stripe_spacing))
        total_stripe_area_width = num_stripes * stripe_width + (num_stripes - 1) * stripe_spacing

        # Ensure the stripes are centered on the crosswalk area
        start_x_stripe = -(total_stripe_area_width / 2)

        # First crosswalk (south)
        crosswalk1_center_y = -self.road_length / 4
        for i in range(num_stripes):
            cm_stripe = CardMaker('crosswalk1_stripe_{}'.format(i))
            cm_stripe.setFrame(-stripe_width / 2, stripe_width / 2, -crosswalk_width / 2, crosswalk_width / 2)
            stripe = self.render.attachNewNode(cm_stripe.generate())
            stripe.setHpr(90, 0, 0)
            stripe_x_pos = start_x_stripe + i * (stripe_width + stripe_spacing) + stripe_width / 2
            stripe.setPos(stripe_x_pos, crosswalk1_center_y, 0.01)
            stripe.setColor(0.8, 0.8, 0.8, 1) # White

        # Second crosswalk (north)
        crosswalk2_center_y = self.road_length / 4
        for i in range(num_stripes):
            cm_stripe = CardMaker('crosswalk2_stripe_{}'.format(i))
            cm_stripe.setFrame(-stripe_width / 2, stripe_width / 2, -crosswalk_width / 2, crosswalk_width / 2)
            stripe = self.render.attachNewNode(cm_stripe.generate())
            stripe.setHpr(90, 0, 0)
            stripe_x_pos = start_x_stripe + i * (stripe_width + stripe_spacing) + stripe_width / 2
            stripe.setPos(stripe_x_pos, crosswalk2_center_y, 0.01)
            stripe.setColor(0.8, 0.8, 0.8, 1) # White


        # Create Wait Areas (two for each crosswalk, one on each side of the road)
        # West side, first crosswalk
        cm_wait_area_w1 = CardMaker('wait_area_w1')
        cm_wait_area_w1.setFrame(-wait_area_width / 2, wait_area_width / 2, 0, wait_area_depth)
        wait_area_w1 = self.render.attachNewNode(cm_wait_area_w1.generate())
        wait_area_w1.setHpr(0, 0, 0) # No rotation, assume aligned with road at its edge
        wait_area_w1.setPos(-(road_width / 2 + wait_area_width / 2), -road_length / 4, 0.01) # To the left of the road, aligned with crosswalk1
        wait_area_w1.setColor(0.4, 0.4, 0.4, 1) # Darker grey for waiting areas

        # East side, first crosswalk
        cm_wait_area_e1 = CardMaker('wait_area_e1')
        cm_wait_area_e1.setFrame(-wait_area_width / 2, wait_area_width / 2, 0, wait_area_depth)
        wait_area_e1 = self.render.attachNewNode(cm_wait_area_e1.generate())
        wait_area_e1.setHpr(0, 0, 0)
        wait_area_e1.setPos((road_width / 2 + wait_area_width / 2), -road_length / 4, 0.01) # To the right of the road, aligned with crosswalk1
        wait_area_e1.setColor(0.4, 0.4, 0.4, 1)

        # West side, second crosswalk
        cm_wait_area_w2 = CardMaker('wait_area_w2')
        cm_wait_area_w2.setFrame(-wait_area_width / 2, wait_area_width / 2, 0, wait_area_depth)
        wait_area_w2 = self.render.attachNewNode(cm_wait_area_w2.generate())
        wait_area_w2.setHpr(0, 0, 0)
        wait_area_w2.setPos(-(road_width / 2 + wait_area_width / 2), road_length / 4, 0.01) # To the left of the road, aligned with crosswalk2
        wait_area_w2.setColor(0.4, 0.4, 0.4, 1)

        # East side, second crosswalk
        cm_wait_area_e2 = CardMaker('wait_area_e2')
        cm_wait_area_e2.setFrame(-wait_area_width / 2, wait_area_width / 2, 0, wait_area_depth)
        wait_area_e2 = self.render.attachNewNode(cm_wait_area_e2.generate())
        wait_area_e2.setHpr(0, 0, 0)
        wait_area_e2.setPos((road_width / 2 + wait_area_width / 2), road_length / 4, 0.01) # To the right of the road, aligned with crosswalk2
        wait_area_e2.setColor(0.4, 0.4, 0.4, 1)

    def spawn_car(self, start_y):
        lane_x = random.choice(self.lane_positions)
        new_car = Car(self, self.next_car_id, start_y, lane_x)
        self.cars.append(new_car)
        self.next_car_id += 1
        print(f"Spawned Car {new_car.car_id} at ({lane_x}, {start_y})")

    def spawn_initial_cars(self):
        # Spawn a few cars at different positions to start
        for i in range(3):
            self.spawn_car(-self.road_length / 2 + i * 20)

    def spawn_pedestrian(self):
        crosswalk_idx = random.randint(0, 1) # Choose one of the two crosswalks
        crosswalk_info = self.crosswalk_coords[crosswalk_idx]
        center_y = crosswalk_info['center_y']
        crosswalk_x_range = crosswalk_info['x_range']
        z_pos = crosswalk_info['z']

        # Decide which side the pedestrian spawns on (west or east wait area)
        spawn_side = random.choice(['west', 'east'])
        
        if spawn_side == 'west':
            start_x = -self.wait_area_x_offset # X position for west wait area
            # Target will be on the east side of the road, on the same crosswalk
            target_x = self.wait_area_x_offset
        else: # east side
            start_x = self.wait_area_x_offset
            target_x = -self.wait_area_x_offset
        
        # Initial Y position should be near the crosswalk, within the wait area's depth
        # We need to consider the depth of the wait area (15 units)
        # The wait area extends from 0 to wait_area_depth in its local frame
        # For crosswalk at -road_length/4, the wait area starts at -road_length/4
        # So a random y within (center_y - wait_area_depth/2, center_y + wait_area_depth/2) relative to road.
        # This makes the pedestrian start inside the wait area, near the crosswalk.
        wait_area_y_start = center_y
        wait_area_y_end = center_y + 15 # Wait area depth is 15. Assuming it extends 'forward' from center_y

        # Adjust starting Y for the pedestrian to be within the wait area rectangle
        # and ensure they are ready to cross at the crosswalk entrance.
        start_y = random.uniform(wait_area_y_start - 5, wait_area_y_start + 5) # Small range near crosswalk edge

        start_pos = Vec3(start_x, start_y, z_pos + 0.9) # Pedestrian height offset for model center
        target_pos = Vec3(target_x, start_y, z_pos + 0.9) # Target on the other side of the crosswalk

        new_pedestrian = Pedestrian(self, self.next_pedestrian_id, start_pos, target_pos, crosswalk_idx)
        self.pedestrians.append(new_pedestrian)
        self.next_pedestrian_id += 1
        print(f"Spawned Pedestrian {new_pedestrian.pedestrian_id} at {start_pos}")

    def spawn_initial_pedestrians(self):
        for _ in range(2):
            self.spawn_pedestrian()

    def cycle_traffic_lights(self, task):
        dt = globalClock.getDt()
        self.current_signal_time += dt

        if self.current_traffic_state == 'red':
            self.traffic_light.set_light('red')
            self.pedestrian_signal.set_signal('walk') # Pedestrians walk when car light is red
            if self.current_signal_time >= self.red_light_duration:
                self.current_traffic_state = 'green'
                self.current_ped_state = 'dont_walk'
                self.current_signal_time = 0
        elif self.current_traffic_state == 'green':
            self.traffic_light.set_light('green')
            self.pedestrian_signal.set_signal('dont_walk') # Pedestrians wait when car light is green
            if self.current_signal_time >= self.green_light_duration:
                self.current_traffic_state = 'red'
                self.current_ped_state = 'walk'
                self.current_signal_time = 0

        return task.cont

    def update_simulation(self, task):
        dt = globalClock.getDt() # Delta time since last frame
        self.time_since_last_spawn += dt
        self.time_since_last_ped_spawn += dt

        # Update existing cars
        cars_to_remove = []
        for car in self.cars:
            # Cars should stop at red light if before crosswalk
            crosswalk_y_start = self.crosswalk_coords[0]['center_y'] - (30 + 10) / 2 # crosswalk_length / 2
            crosswalk_y_end = self.crosswalk_coords[0]['center_y'] + (30 + 10) / 2

            # Adjust this logic based on traffic light position and lane
            # For now, let's assume the first crosswalk (south) is controlled by this light
            if self.current_traffic_state == 'red' and \
               car.current_y + car.length / 2 > crosswalk_y_start and \
               car.current_y - car.length / 2 < crosswalk_y_end:
                # Car is within the crosswalk and light is red, stop it if it's approaching
                # This is a very basic stop. More advanced logic would involve a stop line.
                pass # Car stops, do not update position
            else:
                car.update()

            # If car is off screen, mark for removal and respawn
            if car.current_y > self.road_length / 2:
                cars_to_remove.append(car)

        for car in cars_to_remove:
            car.model.removeNode() # Remove 3D model from scene
            self.cars.remove(car)
            self.spawn_car(-self.road_length / 2) # Respawn at the start

        # Potentially spawn new cars (simple timing for now)
        if self.time_since_last_spawn > self.spawn_interval:
            # Only spawn if there's space (basic check)
            # For a more robust solution, we'd need to check for overlaps
            if not any(car.current_y < -self.road_length / 2 + car.length + 5 for car in self.cars):
                 self.spawn_car(-self.road_length / 2)
            self.time_since_last_spawn = 0

        # Update pedestrians
        pedestrians_to_remove = []
        for ped in self.pedestrians:
            # Pedestrians cross only when signal is 'walk'
            if self.current_ped_state == 'walk' and not ped.is_crossing:
                # Trigger crossing for pedestrians at the correct crosswalk
                # Assuming only one controlled crosswalk for now (crosswalk_coords[0])
                # Check if pedestrian is in the vicinity of the first crosswalk
                if ped.current_crosswalk_idx == 0 and abs(ped.current_pos.getY() - self.crosswalk_coords[0]['center_y']) < 10:
                    ped.is_crossing = True

            ped.update()
            # If pedestrian has crossed and is off the designated crosswalk/wait area
            # For now, let's assume they disappear after reaching target
            if not ped.is_crossing and abs(ped.current_pos.getX()) >= abs(ped.target_pos.getX()) - ped.speed:
                pedestrians_to_remove.append(ped)

        for ped in pedestrians_to_remove:
            ped.model.removeNode()
            self.pedestrians.remove(ped)
            # Respawn pedestrian at a new random location
            self.spawn_pedestrian()

        # Potentially spawn new pedestrians
        if self.time_since_last_ped_spawn > self.pedestrian_spawn_interval:
            self.spawn_pedestrian()
            self.time_since_last_ped_spawn = 0

        return task.cont

if __name__ == "__main__":
    app = Panda3DSimulation()
    app.run() 