# Quick Rigging (quadruped) driven from code: map Cascadeur's QRT field names to Rigify horse bones.
import csc
import prototypes.qrt_prototypes.create as qrt_create

MAP = {
    "trunk": [("pelvis", "spine.001"), ("spine_1", "spine.002"), ("spine_2", "spine.003"),
              ("spine_3", "spine.004"), ("neck_1", "spine.005"), ("neck_2", "spine.006"),
              ("head", "head"), ("head_end", "skull"),
              ("tail_1", "tail.001"), ("tail_2", "tail.002"), ("tail_3", "tail.003"),
              ("tail_4", "tail.004"), ("tail_end", "tail.005")],
    "left_fore_paw": [("scapula_l", "shoulder.L"), ("humerus_l", "upper_arm.L"), ("radius_l", "forearm.L"),
                      ("carpals_l", "forefoot.L"), ("paw_f_l", "f_toe.L")],
    "right_fore_paw": [("scapula_r", "shoulder.R"), ("humerus_r", "upper_arm.R"), ("radius_r", "forearm.R"),
                       ("carpals_r", "forefoot.R"), ("paw_f_r", "f_toe.R")],
    "left_hind_paw": [("femur_l", "thigh.L"), ("tibia_l", "lower_leg.L"), ("tarsals_l", "hind_foot.L"),
                      ("paw_h_l", "r_toe.L")],
    "right_hind_paw": [("femur_r", "thigh.R"), ("tibia_r", "lower_leg.R"), ("tarsals_r", "hind_foot.R"),
                       ("paw_h_r", "r_toe.R")],
}
mv = scene.model_viewer()
by_name = {mv.get_object_name(o): o for o in mv.get_objects()}
missing = [j for sec in MAP.values() for _, j in sec if j not in by_name]
if missing:
    raise RuntimeError(f"joints not found: {missing}")

qp = csc.rig.QuadrupedBoneProperty()
for section, pairs in MAP.items():
    props = []
    for field, joint in pairs:
        bp = csc.rig.BoneProperty()
        bp.bone_name = field
        bp.object_id = by_name[joint]
        bp.joint_path_name = csc.model.PathName.get_path_name(by_name[joint], mv)
        props.append(bp)
    # Each section is list[list[BoneProperty]]; tail gets its own sub-list inside trunk.
    if section == "trunk":
        groups = [[b for b in props if not b.bone_name.startswith("tail")],
                  [b for b in props if b.bone_name.startswith("tail")]]
    else:
        groups = [props]
    setattr(qp, section, groups)
    print(section, "→", len(getattr(qp, section)))

q = csc.rig.QrtData()
q.is_create_layers = True
q.is_replace_existing = True
q.quadruped = [qp]
print("quadruped sections set:", len(q.quadruped))
qrt_create.create_quadruped_rig(scene, q, 15.0, 30.0, [0.0, 0.5, 0.0], "")
bv = mv.behaviour_viewer()
print("RigInfo:", len(bv.get_behaviours("RigInfo")), "Point:", len(bv.get_behaviours("Point")),
      "objects:", len(mv.get_objects()))
