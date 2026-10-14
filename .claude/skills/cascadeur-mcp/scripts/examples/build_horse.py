"""Blender 4.5 (background): Rigify horse metarig -> crude skinned mesh -> FBX + preview render.

Run: blender-launcher.exe --background --factory-startup --python build_horse.py -- <out_dir>
"""
import json, math, sys
from pathlib import Path
import addon_utils, bmesh, bpy
from mathutils import Vector

out = Path(sys.argv[sys.argv.index("--") + 1]); out.mkdir(parents=True, exist_ok=True)
log = {}
addon_utils.enable("rigify", default_set=False)

# empty scene (in memory only)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.armature_horse_metarig_add()
rig = bpy.context.active_object
rig.name = "Horse"
bones = rig.data.bones
log["bones"] = len(bones)
log["dims"] = [round(v, 3) for v in rig.dimensions]

# --- crude body: one vertex per bone end, edges along bones, Skin modifier gives volume ---
mesh = bpy.data.meshes.new("HorseBody")
body = bpy.data.objects.new("HorseBody", mesh)
bpy.context.collection.objects.link(body)
bm = bmesh.new()
index = {}
def vert(p):
    key = tuple(round(c, 4) for c in p)
    if key not in index:
        index[key] = bm.verts.new(p)
    return index[key]
scale = max(rig.dimensions)            # overall size, metres
radius_of = {}
for b in bones:
    h = rig.matrix_world @ b.head_local; t = rig.matrix_world @ b.tail_local
    if (t - h).length < 1e-4:
        continue
    v1, v2 = vert(h), vert(t)
    if v1 is not v2 and not bm.edges.get((v1, v2)):
        bm.edges.new((v1, v2))
    n = b.name.lower()
    r = (0.11 if any(k in n for k in ("spine", "pelvis", "torso", "chest", "hips")) else
         0.05 if any(k in n for k in ("neck",)) else
         0.06 if any(k in n for k in ("head", "skull")) else
         0.035 if any(k in n for k in ("thigh", "upper_arm", "shoulder", "shin", "forearm")) else
         0.022 if any(k in n for k in ("tail",)) else 0.025) * scale
    for p in (h, t):
        key = tuple(round(c, 4) for c in p)
        radius_of[key] = max(radius_of.get(key, 0), r)
# Rigify bones are often disconnected (legs, tail float next to the spine): link every bone
# head to the nearer end of its parent so the Skin modifier sees ONE connected skeleton.
for b in bones:
    if not b.parent:
        continue
    h = rig.matrix_world @ b.head_local
    ph = rig.matrix_world @ b.parent.head_local; pt = rig.matrix_world @ b.parent.tail_local
    anchor = pt if (pt - h).length <= (ph - h).length else ph
    if (anchor - h).length < 1e-4:
        continue
    va, vb = vert(anchor), vert(h)
    if va is not vb and not bm.edges.get((va, vb)):
        bm.edges.new((va, vb))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bm.to_mesh(mesh)
bm.free()

skin = body.modifiers.new("Skin", "SKIN")
for i, v in enumerate(mesh.vertices):
    sv = mesh.skin_vertices[0].data[i]
    r = radius_of.get(tuple(round(c, 4) for c in v.co), 0.03 * scale)
    sv.radius = (r, r)
mesh.skin_vertices[0].data[0].use_root = True
body.modifiers.new("Subsurf", "SUBSURF").levels = 1
bpy.context.view_layer.objects.active = body
body.select_set(True)
for m in list(body.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.shade_smooth()
log["mesh_verts"] = len(body.data.vertices)

# --- bind mesh to skeleton with automatic weights ---
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
log["vertex_groups"] = len(body.vertex_groups)

bpy.ops.wm.save_as_mainfile(filepath=str(out / "horse_crude.blend"))
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); rig.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out / "horse_crude.fbx"), use_selection=True,
                         object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=False)

# --- preview render (workbench), camera framing the horse from the side-front ---
cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
center = sum((body.matrix_world @ Vector(c) for c in body.bound_box), Vector()) / 8
size = max(body.dimensions)
cam.location = center + Vector((size * 1.5, -size * 1.6, size * 0.6))
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.display.shading.show_xray = True
sc.render.filepath = str(out / "horse_crude_preview_v2.png")
bpy.ops.render.render(write_still=True)
log["outputs"] = sorted(p.name for p in out.iterdir())
(out / "build_log.json").write_text(json.dumps(log, indent=1))
