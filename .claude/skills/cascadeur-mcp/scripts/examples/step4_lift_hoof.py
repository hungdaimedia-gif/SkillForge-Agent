# Pose test without AutoPosing: move one rig controller at frame 10 and key it
# (pattern from Cascadeur's own scripts/animation_scripts/go_to_origin.py).
import numpy as np
FRAME, NAME, LIFT = 10, "f_toe.L_MainPoint", np.array([0.0, 40.0, 0.0])
mv = scene.model_viewer()
oid = {mv.get_object_name(o): o for o in mv.get_objects()}[NAME]
log = {}

def mod(model, update, scene_updater):
    # A fresh scene has a 1-frame animation: key the frame on every layer first, then let
    # Cascadeur grow the animation to cover it, THEN read/write values on that frame.
    for layer in model.layers_selector().all_included_layer_ids():
        model.layers_editor().set_fixed_interpolation_or_key_if_need(layer, FRAME, True)
    model.fit_animation_size_by_layers()
    log["animation_size"] = scene.model_viewer().data_viewer().get_animation_size()
    pos = update.get_object_by_id(oid).root_group().node_deep("Position")
    before = np.array(pos.value(FRAME), dtype=float).reshape(3)
    pos.set_value(before + LIFT, FRAME)
    for layer in model.layers_selector().all_included_layer_ids():
        model.layers_editor().set_fixed_interpolation_or_key_if_need(layer, FRAME, True)
    model.layers_editor().normalize_sections(scene)
    scene_updater.run_update({pos.data_id()}, FRAME)
    log["before"] = before.round(1).tolist()
    log["after"] = np.array(pos.value(FRAME), dtype=float).reshape(3).round(1).tolist()

ok = scene.modify_update("Lift front-left hoof", mod)
print("modify ok:", ok, log)
