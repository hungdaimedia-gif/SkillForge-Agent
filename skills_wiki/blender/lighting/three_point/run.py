# DRAFT example -- not validated here (needs Blender). Run `skillforge ingest`/validate on a machine with Blender.
import json, os, sys
import bpy

p = json.loads(sys.argv[-1]) if "--" in sys.argv or len(sys.argv) > 1 else {}
key_w, fill_w, rim_w = p.get("key_watts", 1000), p.get("fill_watts", 400), p.get("rim_watts", 600)
color_temp_warm = tuple(p.get("color", [1.0, 0.85, 0.7]))

def add_light(name, loc, watts):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.color = watts, color_temp_warm
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)

add_light("Key", (4, -4, 5), key_w)
add_light("Fill", (-5, -3, 3), fill_w)
add_light("Rim", (0, 6, 4), rim_w)
out = os.path.join(os.environ["SKILL_OUTPUT_DIR"], "scene.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print("three-point lighting saved", out)
