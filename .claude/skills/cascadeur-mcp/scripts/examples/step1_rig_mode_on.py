import rig_mode.on as rm_on
print("scene:", app.get_scene_manager().current_scene().name())
rm_on.run_raw(scene, [0.0, 0.5, 0.0])
ed = app.get_tools_manager().get_tool('RiggingModeTool').editor(app.current_scene())
print("rig mode joints:", len(ed.get_joints_data()))
