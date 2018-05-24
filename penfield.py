# PYTHONPATH hook to load cavegen
import os
import sys
libpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(libpath)

import bpy
from cavegen import penitentes

PLANE_SIZE = 10 # x and y max of penitente field: (0,n): (0, 100)
dRHO = 0.01     # infintesimal thickness of surface
PLANE_RES = 8   # Resolution of planar surface: (0, n): (0,10)

def create_field():
    # Delete initial cube
    bpy.data.objects['Cube'].select = True # Select the default Blender Cube
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.delete() # Delete the selected objects (default blender Cube)

    #Define vertices, faces, edges
    verts = [(0,0,0),(0,PLANE_SIZE,0),(PLANE_SIZE,PLANE_SIZE,0),(PLANE_SIZE,0,0),(0,0,dRHO),(0,PLANE_SIZE,dRHO),(PLANE_SIZE,PLANE_SIZE,dRHO),(PLANE_SIZE,0,dRHO)]
    faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]

    #Define mesh and object
    mesh = bpy.data.meshes.new("Cube")
    object = bpy.data.objects.new("Cube", mesh)

    #Set location and scene of object
    #object.location = bpy.context.scene.cursor_location
    object.location.x = -PLANE_SIZE/2
    object.location.y = -PLANE_SIZE/2
    object.location.z = 0
    bpy.context.scene.objects.link(object)

    #Create mesh
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)

    bpy.data.objects['Cube'].select = True
    bpy.context.scene.objects.active = bpy.context.scene.objects['Cube'] # Select the default Blender Cube

    context = bpy.context
    object.modifiers.new('subd', type='SUBSURF')
    object.modifiers['subd'].levels = PLANE_RES
#    obj = context.edit_object
#    me = obj.data
#    obj.modifiers.new("subd", type='SUBSURF')
#    obj.modifiers['subd'].levels = PLANE_RES
    return object

def create_field2():
    #bpy.ops.mesh.primitive_plane_add(radius=10, view_align=False, enter_editmode=False, location=(-PLANE_SIZE/2, -PLANE_SIZE/2, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    mesh = bpy.data.meshes.new('Plane')
    object = bpy.data.objects.new('Plane', mesh)
    object.location.x = -PLANE_SIZE/2
    object.location.y = -PLANE_SIZE/2
    return object


if __name__ == '__main__':
    field = create_field()
    penitentes(field)
    save(field, 'penfield')

