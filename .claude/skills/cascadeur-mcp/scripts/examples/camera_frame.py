# Frame the camera on the character: bbox of JOINTS only (helper objects skew the box),
# then set the spherical camera struct (target + position) of the active viewport.
import numpy as np, pycsc
mv = scene.model_viewer(); bv = mv.behaviour_viewer()
joint_ids = {bv.get_behaviour_owner(b) for b in bv.get_behaviours("Joint")}
pts = []
for o in pycsc.get_scene_objects():
    try:
        if o.object_id not in joint_ids:
            continue
    except Exception:
        pass
    try:
        pts.append(np.array(o.get_behaviour("Transform").global_position.get(), dtype=float).reshape(3))
    except Exception:
        pass
P = np.stack(pts); lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2; size = float((hi - lo).max())
vd = app.get_scene_manager().current_scene().active_viewport().domain_viewport()
cs = vd.camera_struct()
print("before:", np.array(cs.target).round(1).tolist(), np.array(cs.position).round(1).tolist(), cs.type)
cs.target = c.astype(np.float32)
cs.position = (c + np.array([1.3, 0.55, 1.1]) * size).astype(np.float32)
vd.set_camera_struct(cs)
cs2 = vd.camera_struct()
print("n_points", len(pts), "bbox", lo.round(0).tolist(), hi.round(0).tolist())
print("after:", np.array(cs2.target).round(1).tolist(), np.array(cs2.position).round(1).tolist())
