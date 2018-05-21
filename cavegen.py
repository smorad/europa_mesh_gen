import bpy
import bmesh
import random
import operator

# Parameters
# Description: Domain: Recommended Domain
ZONES = 3       # Number of cave segments. Length = ZONES * SIZE: (1,n): (1,50)
SIZE = 5        # Size in m per cave segment: (1,n): (1,10)
YCURVE = 0.5
ZCURVE = 5      # How much the cave turns in the Y and Z planes, 
                # inf would mean a straight level cave: (0.0, n): (1.0, 5.0)
RESOLUTION = 8  # Surface resolution of cave tube: (0, n): (3, 8)
SCALLOP_DIAM = random.uniform(0.25, 1.25)   # Diameter scale factor of scallops, 
                                            # 0.25 approaches 20cm and 1.25 approaches 2m:
                                            # (0.01, n): (0.25, 1.25)
PENITENTES = False      # Enable for penitente field: (True, False): (True, False)


def flip_normals():
    '''Flip normal direction, we care about inside of cave'''
    old_mode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode = 'OBJECT')
    scn = bpy.context.scene
    sel = bpy.context.selected_objects
    meshes = [o for o in sel if o.type == 'MESH']

    for obj in meshes:
        scn.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT') # SELECT

        bpy.ops.mesh.flip_normals() # just flip normals

    # Pop mode before return
    bpy.ops.object.mode_set(mode=old_mode)

    

def spawn_frame():
    '''Spawn the cubes that will eventually form the cave'''
    # Create box frame

    bpy.data.objects['Cube'].select = True # Select the default Blender Cube
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.delete() # Delete the selected objects (default blender Cube)

    #Define vertices, faces, edges
    verts = [(0,0,0),(0,SIZE,0),(SIZE,SIZE,0),(SIZE,0,0),(0,0,SIZE),(0,SIZE,SIZE),(SIZE,SIZE,SIZE),(SIZE,0,SIZE)]
    faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]

    #Define mesh and object
    mesh = bpy.data.meshes.new("Cube")
    object = bpy.data.objects.new("Cube", mesh)

    #Set location and scene of object
    object.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(object)

    #Create mesh
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)

    bpy.data.objects['Cube'].select = True
    bpy.context.scene.objects.active = bpy.context.scene.objects['Cube'] # Select the default Blender Cube

    #Enter edit mode to extrude
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)

    bm = bmesh.from_edit_mesh(mesh)
    for face in bm.faces:
        face.select = False
    bm.faces[4].select = True

    # Show the updates in the viewport
    bmesh.update_edit_mesh(mesh, True)



    for i in range(ZONES):
        x = SIZE
        y = random.uniform(-SIZE, SIZE) / YCURVE
        z = random.uniform(-SIZE, SIZE) / ZCURVE
        
        bpy.ops.mesh.extrude_faces_move(
            MESH_OT_extrude_faces_indiv={"mirror":False}, 
            TRANSFORM_OT_shrink_fatten={
                "value":-x, 
                "use_even_offset":True, 
                "mirror":False, 
                "proportional":'DISABLED', 
                "proportional_edit_falloff":'SMOOTH', 
                "proportional_size":1, 
                "snap":False, 
                "snap_target":'CLOSEST', 
                "snap_point":(0, 0, 0), 
                "snap_align":False, 
                "snap_normal":(0, 0, 0), 
                "release_confirm":False}
    )
        bpy.ops.transform.translate(
            value=(0, y, z), 
            constraint_axis=(False, False, False), 
            constraint_orientation='GLOBAL', 
            mirror=False, 
            proportional='DISABLED', 
            proportional_edit_falloff='SMOOTH',
            proportional_size=1
        )


    # Remove entry face
    faces_select = [f for f in bm.faces if f.select] 
    bmesh.ops.delete(bm, geom=faces_select, context=5)  
     
    # Show the updates in the viewport
    bmesh.update_edit_mesh(mesh, True)

    return bpy.data.objects['Cube']

def circularize():
    '''Convert cubes to tubes'''
    context = bpy.context
    obj = context.edit_object
    me = obj.data
    obj.modifiers.new("subd", type='SUBSURF')
    obj.modifiers['subd'].levels = RESOLUTION
    me.update()

def archize():
    '''Convert tubes to arch'''
    for i in range(100):
        try:
            bpy.ops.mesh.loopcut_slide(
                MESH_OT_loopcut={
                    "number_cuts":1, 
                    "smoothness":0, 
                    "falloff":'INVERSE_SQUARE', 
                    "edge_index":i, 
                    "mesh_select_mode_init":(True, False, False)
                }, 
                TRANSFORM_OT_edge_slide={
                    "value":-0.763176, 
                    "single_side":False, 
                    "use_even":False, 
                    "flipped":False, 
                    "use_clamp":True, 
                    "mirror":False, 
                    "snap":False, 
                    "snap_target":'CLOSEST', 
                    "snap_point":(0, 0, 0), 
                    "snap_align":False, 
                    "snap_normal":(0, 0, 0), 
                    "correct_uv":False, 
                    "release_confirm":False, 
                    "use_accurate":False
                }
            )
            print('Archized structure')
            break
        except:
            pass

#   old_type = bpy.context.area.type
#   bpy.ops.object.mode_set(mode='EDIT')
#   bpy.context.area.type = 'VIEW_3D'
#
#   # Forgive me
#   for i in range(100):
#       try:
#           bpy.ops.mesh.loopcut_slide(
#               MESH_OT_loopcut={
#                       "number_cuts":1, 
#                       "smoothness":0, 
#                       "falloff":'ROOT', 
#                       "edge_index":i
#               }, 
#               TRANSFORM_OT_edge_slide={"value":-0.75}
#           )
#           break
#       except:
#           pass
#   #bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'ROOT', "edge_index":0})
#   bpy.context.area.type = old_type 


def scallop(cave):
    # Scallop diameter 20cm to 2m
    # depth no more than 20cm, not a fn of diameter
    mod = cave.modifiers.new(name='scallop', type='DISPLACE')
    tex = bpy.data.textures.new('scallop', type='VORONOI')
    bpy.context.object.modifiers["scallop"].texture = tex
    bpy.context.object.modifiers["scallop"].strength = 0.25
    bpy.data.textures["scallop"].noise_intensity = 0.25
    bpy.data.textures["scallop"].noise_scale = SCALLOP_DIAM


def penitentes(cave):
    mod = cave.modifiers.new(name='penitentes', type='DISPLACE')
    tex = bpy.data.textures.new('penitentes', type='MUSGRAVE')
    bpy.context.object.modifiers["penitentes"].direction = 'Z'
    bpy.context.object.modifiers["penitentes"].texture = tex
    bpy.context.object.modifiers["penitentes"].strength = 4
    bpy.data.textures["penitentes"].dimension_max = 1.5
    bpy.data.textures["penitentes"].lacunarity = 2.3
    bpy.data.textures["penitentes"].octaves = 3
    bpy.data.textures["penitentes"].noise_scale = 1
    bpy.data.textures["penitentes"].noise_intensity = 0.4

    # In sim:
    # strength 1
    # intensity 3
    # actual distance
    # noise size 0.4
    

def split_cave(cave):
    '''WARNING: Cannot be undone, once split it's hard to make changes
    to the whole cave instead of per-segment.'''
    # Split faces of cube with Y
    # Move them 0.01 -X
    # Seperate type='LOOSE'
    
    # Faces should be >7 in multiples of 4
    for segment in range(ZONES):
        mesh = cave.data
        print('Mesh is ', mesh)
        bpy.ops.object.mode_set(mode = 'EDIT')
        face_indices = [8, 9, 10, 11]
        # Create list of increments to be added to indices
        increment = 4 * [segment]
        # Compute new indices, which should be the 4 indices following the last 4
        face_indices = list(map(lambda a, b: a + 4 * b, face_indices, increment))
        bm = bmesh.new()
        bm.from_mesh(mesh)
        # Force table generation or will get no faces
        bm.faces.ensure_lookup_table()
        print('Got indices ', face_indices,' out of max ', len(bm.faces))
        faces = bm.faces[face_indices[0]:face_indices[-1]]
        print('Attemping split')
        bmesh.ops.split(bm, geom=faces)
        # Regenerate source mesh for next iteration
        bpy.ops.object.mode_set(mode = 'OBJECT')
        print('Mesh conversion')
        bm.to_mesh(cave.data)
        bpy.ops.mesh.separate(type='LOOSE')
        
    #bpy.ops.mesh.separate(type='LOOSE')


def split_cave2(cave):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_split()
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode = 'OBJECT')    


def split_original_cube(cave):
        mesh = cave.data
        face_indices = [0, 1, 2, 3, 4]
        bm = bmesh.new()
        bm.from_mesh(mesh)
        # Force table generation or will get no faces
        bm.faces.ensure_lookup_table()
        # Select inverse of what we want to separate
        face_indices = sorted(set(range(len(bm.faces))) - set(face_indices))
        faces = bm.faces[face_indices[0]:face_indices[-1]]
        print('Got indices ', face_indices,' out of max ', len(bm.faces) - 1)
        print('Attemping split')
        bmesh.ops.split(bm, geom=faces)
        # Regenerate source mesh for next iteration
        bpy.ops.object.mode_set(mode = 'OBJECT')
        print('Mesh conversion')
        bm.to_mesh(cave.data)
        bpy.ops.mesh.separate(type='LOOSE')


def split_cave3(cave):
    #split_original_cube()
    # The way splitting works is we need to select
    # everything except for the splitted segment
    for segment in range(ZONES):
        mesh = cave.data
        print('Mesh is ', mesh)
        bpy.ops.object.mode_set(mode = 'EDIT')
        face_indices = [5, 6, 7, 8]
        # Create list of increments to be added to indices
        increment = 4 * [segment]
        # Compute new indices, which should be the 4 indices following the last 4
        face_indices = list(map(lambda a, b: a + 4 * b, face_indices, increment))
        bm = bmesh.new()
        bm.from_mesh(mesh)
        # Force table generation or will get no faces
        bm.faces.ensure_lookup_table()
        # Select inverse of what we want to separate
        face_indices = sorted(set(range(len(bm.faces))) - set(face_indices))
        faces = bm.faces[face_indices[0]:face_indices[-1]]
        print('Got indices ', face_indices,' out of max ', len(bm.faces) - 1)
        print('Attemping split')
        bmesh.ops.split(bm, geom=faces)
        # Regenerate source mesh for next iteration
        bpy.ops.object.mode_set(mode = 'OBJECT')
        print('Mesh conversion')
        bm.to_mesh(cave.data)
        bpy.ops.mesh.separate(type='LOOSE')
        
    #bpy.ops.mesh.separate(type='LOOSE')



if __name__ == '__main__':
    print('Initializing')
    cave = spawn_frame()
    flip_normals()
    circularize()
    #archize()
    scallop(cave)
    if PENITENTES:
        penitentes(cave)
    #split_cave3(cave)
    #split_original_cube(cave)
