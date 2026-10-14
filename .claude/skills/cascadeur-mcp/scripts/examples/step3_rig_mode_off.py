import rig_mode.off as rm_off
rm_off.run(scene, True)
mv = scene.model_viewer(); bv = mv.behaviour_viewer()
print("RigInfo:", len(bv.get_behaviours("RigInfo")), "Point:", len(bv.get_behaviours("Point")),
      "AutoPosing-ish:", sum(1 for n in ("AutoPosing", "FulcrumPoint") for _ in bv.get_behaviours(n)),
      "objects:", len(mv.get_objects()))
