# Walk-in-place, 40 frames, without AutoPosing: key 4 hoof controllers + head controller.
# Gait order (lateral walk): left hind -> left fore -> right hind -> right fore, 10 frames each.
import numpy as np
LEGS = ["toe.L_MainPoint_r", "f_toe.L_MainPoint", "toe.R_MainPoint_r", "f_toe.R_MainPoint"]
TAIL = "tail.004_MainPoint"
HEAD = "head_MainPoint"
UP, FWD = 25.0, 10.0                     # cm; forward = +Z for this model (front hooves at z ~ +52)
KEYS = list(range(0, 41, 5))
mv = scene.model_viewer()
ids = {mv.get_object_name(o): o for o in mv.get_objects()}
log = {}

def mod(model, update, scene_updater):
    le = model.layers_editor()
    layers = list(model.layers_selector().all_included_layer_ids())
    for f in KEYS:
        for layer in layers:
            le.set_fixed_interpolation_or_key_if_need(layer, f, True)
    model.fit_animation_size_by_layers()
    nodes = {n: update.get_object_by_id(ids[n]).root_group().node_deep("Position") for n in LEGS + [HEAD, TAIL]}
    rest = {n: np.array(nodes[n].value(0), dtype=float).reshape(3) for n in nodes}
    # frame 10 of f_toe.L was lifted by the earlier test: rest pose comes from frame 0
    for f in KEYS:
        for i, n in enumerate(LEGS):
            v = rest[n].copy()
            if f == i * 10 + 5:                   # middle of this leg's 10-frame window
                v += np.array([0.0, UP, FWD])
            nodes[n].set_value(v, f)
        h = rest[HEAD].copy()
        if f % 10 == 5:
            h += np.array([0.0, -6.0, 3.0])        # head dips while a leg swings
        nodes[HEAD].set_value(h, f)
        t = rest[TAIL].copy()
        t += np.array([(-12.0 if (f // 10) % 2 else 12.0) if f % 10 == 5 else 0.0, 0.0, 0.0])  # swish
        nodes[TAIL].set_value(t, f)
    le.normalize_sections(scene)
    actual = {nodes[n].data_id() for n in nodes}
    for f in range(0, KEYS[-1] + 1):
        scene_updater.run_update(actual, f)
    log["frames"] = scene.model_viewer().data_viewer().get_animation_size()

ok = scene.modify_update("Walk in place", mod)
print("modify ok:", ok, log)
