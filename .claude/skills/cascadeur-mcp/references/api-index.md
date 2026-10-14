# Mục lục API Cascadeur (csc / pycsc)

Sinh tự động từ Cascadeur đang chạy (pycsc VERSION (0, 6, 0), bản cài 2026.2.3) ngày 2026-10-14,
bằng cách duyệt `dir()` + docstring qua MCP. Chỉ liệt kê lớp/hàm cấp module; tra chi tiết phương thức bằng
`help(<đối tượng>)` qua `casc.py run`, hoặc đọc `G:/cascadeur/resources/scripts/python/samples/api_document.py`.

## `csc.additive_layers`

- `Debug` (class)
- `DebugSource` (class) — Members:
- `Manager` (class)
- `create_debug` (fn)
- `get_manager` (fn)

## `csc.app`

- `ActionManager` (class) — ActionManager class
- `Application` (class) — Application class.
- `CascadeurTool` (class) — CascadeurTool class.
- `DataSourceManager` (class) — DataSourceManager class.
- `ProjectLoader` (class) — ProjectLoader class
- `SceneManager` (class) — SceneManager class.
- `SceneTool` (class) — SceneTool class provides utility methods and properties to work with scenes.
- `SettingsHandler` (class) — SettingsHandler class
- `SettingsManager` (class) — SettingsManager class provides methods to get various settings values.
- `SimpleStatusInformer` (class) — SimpleStatusInformer class
- `StatusInformer` (class) — StatusInformer class
- `StatusManager` (class) — StatusManager class
- `ToolsManager` (class) — ToolsManager class provides access to various tools within the application.
- `get_application` (fn) — Get the application instance

## `csc.app.topology_controller`

- `CommandInfo` (class) — CommandInfo class

## `csc.domain`

- `Asset` (class) — Asset class
- `AssetId` (class)
- `FrameActionOnChange` (class) — FrameActionOnChange enum
- `IMessageHandler` (class) — IMessageHandler interface
- `IntervalActionOnChange` (class) — IntervalActionOnChange enum
- `LocalInterpolator` (class) — LocalInterpolator class
- `Pivot` (class) — Pivot class
- `ProcessorsStorage` (class) — ProcessorsStorage class
- `Scene` (class) — Scene class
- `SceneUpdater` (class) — SceneUpdater class
- `Select` (class) — Select class
- `Selection` (class) — Selection class
- `SelectionChanger` (class) — SelectionChanger class
- `Selector` (class) — Selector class
- `SelectorFilter` (class) — SelectorFilter enumerable
- `SelectorMode` (class) — SelectorMode enumerable
- `Session` (class) — Session class
- `SkinnedMeshCalcResult` (class) — skinned_mesh_calc::Result class
- `StatePivot` (class) — StatePivot enum
- `Tool_object_id` (class)
- `calc_skinned_mesh` (fn)
- `delete_entity_3d_processor` (fn)
- `find_actual_rig_info_id` (fn)
- `get_all_visible_ids_by_proc` (fn)
- `get_tool_name` (fn)
- `get_tool_names` (fn)

## `csc.domain.assets`

- `AssetsManager` (class) — AssetsManager class
- `Mesh` (class) — Mesh class
- `MeshBlendshape` (class) — MeshBlendshape class
- `MeshDependency` (class) — MeshDependency class
- `Texture` (class) — Texture class
- `Vertex` (class) — Vertex class
- `VertexWeight` (class) — VertexWeight class

## `csc.external`

- `ExtraDatas` (class) — ExtraDatas class
- `FbxDatas` (class) — FbxDatas class

## `csc.fbx`

- `FbxLoader` (class) — FbxLoader class.
- `FbxSceneLoader` (class) — FbxSceneLoader class.
- `FbxSettings` (class) — FbxSettings class.
- `FbxSettingsAxis` (class) — FbxSettingsAxis enumeration
- `FbxSettingsMode` (class) — FbxSettingsMode enumeration

## `csc.glb`

- `CommonOptions` (class)
- `ExportOptions` (class)
- `ImportOptions` (class)
- `process_export` (fn)
- `process_import` (fn)

## `csc.layers`

- `Cycle` (class) — Cycle class.
- `CyclesEditor` (class) — Cycle editor class.
- `CyclesViewer` (class) — Cycle viewer class.
- `Editor` (class) — Editor class
- `Folder` (class) — Folder class
- `Header` (class) — Header class
- `ItemVariant` (class) — ItemVariant class
- `Layer` (class) — Layer class
- `Layers` (class) — Layers class
- `LayersContainer` (class) — LayersContainer class
- `LayersSelectionChanger` (class) — Layer SelectionChanger class
- `Selector` (class) — Selector class
- `UserLabelData` (class) — UserLabelData class
- `UserLabels` (class) — UserLabels class
- `Viewer` (class) — Viewer class

## `csc.layers.index`

- `CellIndex` (class) — CellIndex class
- `FramesIndices` (class) — FramesIndices class
- `FramesInterval` (class) — FramesInterval class
- `IndicesContainer` (class) — IndicesContainer class
- `ItemIndices` (class) — ItemIndices handle
- `RectIndicesContainer` (class) — RectIndicesContainer class

## `csc.layers.layer`

- `Cell` (class) — Cell class
- `Common` (class) — Common class
- `Fixation` (class) — Layer Frame Fixation enumerable
- `IkFk` (class) — Layer Frame IkFk enumerable
- `Interpolation` (class) — Interpolation enumerable
- `Interval` (class) — Interval class
- `Key` (class) — Key class
- `Section` (class) — Section class
- `Tangents` (class) — Layer Frame Tangents enumerable
- `copy_frames_from_src_layer_to_dst_layer` (fn)

## `csc.math`

- `Affine` (class)
- `AngleAxis` (class) — AngleAxis class
- `Circle` (class) — Circle3d class
- `OrthogonalTransform` (class) — OrthogonalTransform class
- `ParametrizedLine` (class) — ParametrizedLine class
- `Plane` (class) — Hyperplane class
- `Quaternion` (class) — Quaternion class
- `Rotation` (class) — Rotation class
- `ScaledTransform` (class) — ScaledTransform class
- `SizesInterval` (class) — SizesInterval class
- `Sphere` (class) — Sphere class
- `Triangle` (class) — Triangle class
- `basic_transform_from_triangle` (fn) — -> csc.math.OrthogonalTransform
- `combine_transforms` (fn) — -> csc.math.OrthogonalTransform
- `decompose_matrix` (fn)
- `euler_angles_to_quaternion_x_y_z` (fn) — -> Quaternionf
- `euler_flip` (fn)
- `get_m3f_diag` (fn) — -> Vector3f
- `ik_spline` (fn) — -> Tuple<vector<Vector3f>, vector<Quaternion>>
- `ik_spline_3` (fn) — -> Tuple<vector<Vector3f>, vector<Quaternion>>
- `inverse_transform_point` (fn) — -> Vector3f
- `line_on_intersection_planes` (fn)
- `modify_position_by_matrix` (fn) — -> Vector3f
- `point_on_intersection_planes` (fn)
- `project_point_on_basic_line` (fn) — -> Vector3f
- `quaternion_to_euler_angles_x_y_z` (fn) — -> Vector3f
- `simple_bezier_closest_point` (fn) — -> double
- `spheres_intersection` (fn)
- `spheres_intersection_extended` (fn)
- `step_linear_func` (fn)
- `transform_point` (fn) — Overloaded function.
- `transforms_difference` (fn) — -> csc.math.OrthogonalTransform
- `untwist` (fn) — parentMatrix:Matrix4f,objectMatrix:Matrix4f) -> Matrix4f

## `csc.model`

- `BehaviourEditor` (class) — BehaviourEditor class
- `BehaviourId` (class)
- `BehaviourViewer` (class) — BehaviourViewer class
- `ClusterEditor` (class) — ClusterEditor class
- `ClusterViewer` (class) — ClusterViewer class
- `ClustersEdge` (class) — ClustersEdge class
- `CustomSelectionPolicy` (class) — CustomSelectionPolicy enumerable
- `Data` (class) — Data class
- `DataEditor` (class) — DataEditor class
- `DataId` (class)
- `DataMode` (class) — Data::Mode enum
- `DataViewer` (class) — DataViewer class
- `DescriptionId` (class)
- `DescriptionTerm` (class)
- `HyperedgeId` (class)
- `LerpMode` (class) — LerpMode enumerable
- `ModelEditor` (class) — ModelEditor class
- `ModelViewer` (class) — ModelViewer class
- `ObjectId` (class)
- `PathName` (class)
- `PropertyType` (class) — PropertyType enumerable
- `Setting` (class) — Setting class
- `SettingFunctionId` (class)
- `SettingId` (class)
- `SettingMode` (class) — Setting::Mode enum
- `get_path_without_namespace` (fn) — -> PathName

## `csc.parts`

- `Buffer` (class) — Buffer class
- `GroupInfo` (class) — GroupInfo class
- `Info` (class) — Info class
- `SceneClipboard` (class) — SceneClipboard class
- `Type` (class) — Type of the parts, enum

## `csc.physics`

- `PosMass` (class) — PosMass class
- `inertia_tensor` (fn) — -> Matrix3f

## `csc.rig`

- `AddElementData` (class) — AddElementData
- `BoneProperty` (class)
- `QrtData` (class)
- `QuadrupedBoneProperty` (class)
- `TwistBoneProperty` (class)
- `TwistProperty` (class)
- `UntwistBoneProperty` (class)

## `csc.sf3`

- `export_animation` (fn) — Exports Sf3 animation data to a .bytes file.
- `import_animation` (fn) — Imports Sf3 animation data from a .bytes file into a scene.
- `load_bones_id` (fn) — Loads Sf3 bones id data into a scene.

## `csc.tools`

- `ActivateDeactivate` (class) — ActivateDeactivate class
- `AnimationPointsTypes` (class) — AnimationPointsTypes
- `AnimationUnbakingTool` (class) — AnimationUnbakingTool class
- `AttractorTool` (class) — Attractor tool class
- `AutoPhysicTool` (class) — Auto physics tool class
- `AutoPosingTool` (class) — AutoPosingTool class
- `BallisticTrajectory` (class) — BallisticTrajectory class
- `CollisionInfoForObject` (class) — CollisionInfoForObject
- `CollisionShapeStorage` (class)
- `ControlPicker` (class) — ControlPicker class
- `DataKey` (class) — DataKey
- `FulcrumCollisionInfo` (class) — FulcrumCollisionInfo
- `InbetweeningTool` (class) — InbetweeningTool class
- `JointData` (class) — JointData
- `MirrorTool` (class) — Mirror tool class.
- `ObjectKey` (class) — ObjectKey
- `RenderParameters` (class) — Parameters for rendering
- `RenderToFile` (class) — Render to file tool class
- `RiggingModeTool` (class) — Rigging mode tool class
- `RiggingWindow` (class) — SelectionGroups class
- `SelectionGroups` (class) — SelectionGroups class
- `StaticPointsTypes` (class) — StaticPointsTypes
- `Trajectory` (class) — Trajectory class
- `generate_acd_meshes` (fn) — generate_acd_meshes
- `generate_convex_hull_mesh` (fn) — generate_convex_hull_mesh
- `generate_convex_hull_mesh_from_rb` (fn) — generate_convex_hull_mesh_from_rb
- `get_all_collision_for_object` (fn) — get_all_collision_for_object
- `get_collision_shape_storage` (fn) — get_collision_shape_storage

## `csc.tools.attractor`

- `Args` (class) — Arguments for configuring attractor operations.
- `ArgsMode` (class) — attractor::Mode enum
- `AttractorGeneralSettings` (class)
- `GSAxisFlag` (class) — GeneralSettings::RotationAxis enum
- `GSAxisIndex` (class) — GeneralSettings::RotationAxis enum
- `GSPhysicsType` (class) — GeneralSettings::RotationAxis enum
- `GSRotationAxis` (class) — GeneralSettings::RotationAxis enum
- `SpaceMode` (class) — attractor::Mode enum
- `attract` (fn)

## `csc.tools.mirror`

- `Core` (class) — Mirror tool core class

## `csc.tools.selection`

- `Core` (class) — Core class
- `Group` (class) — Group class
- `Mode` (class) — Mode enumeration

## `csc.update`

- `ActivityAttribute` (class) — ActivityAttribute represents the activity of the data function.
- `ActualityAttribute` (class) — ActualityAttribute shows whether data is actual at the start of the graphs update.
- `ActualityAttributeId` (class) — ActualityAttributeId is defined by the data id. It's an output only attribute.
- `Connection` (class) — Connection class
- `ConstantDataAttribute` (class) — ConstantDataAttribute represents an attribute of a constant regular data.
- `ConstantDataAttributeId` (class) — ConstantDataAttributeId is defined by the ConstantDatasId and the data id of the constant
- `ConstantDatas` (class) — ConstantDatas represents a node of constant datas. It is present in any place.
- `ConstantDatasId` (class) — ConstantDatasId is a guid based id.
- `ConstantSettingAttribute` (class) — ConstantSettingAttribute represents an attribute of a constant setting.
- `ConstantSettingAttributeId` (class) — ConstantSettingAttributeId  is defined by the ConstantSettingId and the setting id of the constant
- `ConstantSettings` (class) — ConstantSettings represents a node of constant settings. It is present in any place.
- `ConstantSettingsId` (class) — ConstantSettingsId  is a guid based id.
- `ExternalProperties` (class) — ExternalProperties represents a node of external properties.
- `ExternalPropertiesId` (class) — ExternalPropertiesId is a guid based id.
- `ExternalProperty` (class) — ExternalProperty enum
- `ExternalPropertyAttribute` (class) — ExternalPropertyAttribute represents an attribute of the external properties of the update.
- `ExternalPropertyAttributeId` (class) — ExternalPropertyAttributeId is defined by the ExternalPropertiesId and the value of the ExternalProperty enum
- `Group` (class) — Group class
- `GroupAttributeId` (class) — GroupAttributeId is defined by the GroupId and the guid-based id of the attribute.
- `GroupId` (class)
- `HierarchyUpdate` (class) — HierarchyUpdate class provides concrete operations with connections
- `InterfaceAttribute` (class) — InterfaceAttribute represents a group attribute.
- `InterfaceAttributeSide` (class) — InterfaceAttributeSide enumerable
- `InterfaceId` (class) — InterfaceId is defined by the GroupId and the direction type of the node - input or output connection node.
- `InterfaceNode` (class) — InterfaceNode is a node inside the group that represents its connections with the ouside nodes.
- `Node` (class) — Node class represents a generic Node and implements methods that are common for all nodes
- `NodeAttribute` (class) — NodeAttribute represents a generic node attribute and the standard operations you can do with such an attribut
- `Object` (class) — Object class represents an object node. Functionality is limited - it's better to use update group node instea
- `ObjectGroup` (class) — ObjectGroup class represents object group node
- `RegularData` (class) — RegularData class represents a node of a data.
- `RegularDataAttribute` (class) — RegularDataAttribute represents an attribute of a regular data.
- `RegularDataAttributeId` (class) — RegularDataAttributeId is defined by the data id.
- `RegularFunction` (class) — RegularFunction class represents a node that calculates same operation, done with datas.
- `RegularFunctionAttribute` (class) — RegularFunctionAttribute represents an attribute of a data function.
- `RegularFunctionAttributeId` (class) — RegularFunctionAttributeId is defined by the RegularFunctionId and the name of the attribute
- `SettingData` (class) — SettingData class represents a node that calculates same operation, done with settings.
- `SettingDataAttribute` (class) — SettingDataAttribute represents an attribute of a setting.
- `SettingFunction` (class) — SettingFunction class
- `SettingFunctionAttribute` (class) — SettingFunctionAttribute represents an attribute of a setting function.
- `SettingFunctionAttributeId` (class) — SettingFunctionAttributeId is defined by the SettingFunctionId and the index of the attribute
- `Update` (class) — Update class represents the whole update editor
- `UpdateGroup` (class) — UpdateGroup class represents update group node

## `csc.view`

- `AnimationBoundary` (class) — AnimationBoundary class
- `Camera` (class) — Represents a spherical camera class in the view domain.
- `CameraType` (class) — CameraType enumerable
- `DialogButton` (class) — DialogButton class
- `DialogManager` (class) — DialogManager class
- `FileDialogManager` (class) — FileDialogManager class
- `PythonModelsManager` (class) — PythonModelsManager class
- `Scene` (class) — SceneView class
- `SphericalCameraStruct` (class) — SphericalCameraStruct class
- `StandardButton` (class) — StandardButton enum
- `Viewport` (class) — Viewport class
- `ViewportDomain` (class) — Domain Viewport class.
- `ViewportMode` (class) — ViewportMode enumerable

## `csc.view.camera_utils`

- `CameraData` (class) — CameraData class
- `get_cameras` (fn)
- `is_camera_active` (fn)
- `reset_camera` (fn)
- `set_camera_active` (fn)

## `pycsc.attr`

- `Attr` (class)
- `SettingFuncAttr` (class)
- `TypeVar` (class)
- `Iterable` (fn) — A generic version of collections.abc.Iterable.
- `List` (fn) — A generic version of list.
- `Set` (fn) — A generic version of set.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `Union` (fn)
- `get_full_type_name` (fn)

## `pycsc.attr.common`

- `EditorError` (class) — Thrown when someone attempts to access and editor at an invalid time
- `InternalSceneElement` (class) — Used for classes that need to override methods of the class it wraps
- `IterSceneElement` (class)
- `NodeGuid` (class)
- `PyGuid` (class) — Base class for wrappping csc.Guid and all Ids
- `SceneElement` (class) — Base class used to represent any wrapped data existing/related to a scene
- `ViewersEditors` (class)

## `pycsc.attr.common.mappings`

- `WrapperStatics` (class)
- `WrappingError` (class) — Thrown when the mapping is retrieved before being initialized.
- `create_asset` (fn)
- `create_behaviour` (fn)
- `create_object` (fn)
- `get_wrappers` (fn)
- `register_behaviour` (fn)
- `register_wrapper` (fn)
- `set_default_behaviour_class` (fn)
- `set_default_object_class` (fn)

## `pycsc.attr.common.wrapper`

- `CscWrapper` (class)

## `pycsc.attr.scenes`

- `DomainScene` (class) — A Wrapper around a domain scene
- `LayersAccess` (class) — Provides access to layer operations and queries.
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `Timeline` (class) — High-level operations for frame manipulation in the timeline.
- `ViewScene` (class) — A Wrapper around a view scene
- `Union` (fn)

## `pycsc.attr_definitions`

- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `BaseSubnodesDef` (class) — Base class for defining subnodes using auto().
- `StrEnum` (class)

## `pycsc.attr_interface`

- `Attr` (class)
- `AttrInterface` (class)
- `List` (fn) — A generic version of list.
- `get_full_type_name` (fn)

## `pycsc.attributes`

- `Attr` (class)
- `AttrInterface` (class)

## `pycsc.behaviours`

- `AngleConstraints` (class)
- `AnimationInfo` (class)
- `AttractionPoint` (class)
- `AutoPhysics` (class)
- `AutoPhysicsApply` (class)
- `AutoPosingInfo` (class)
- `AutoPosingLink` (class)
- `BaseDynamic` (class)
- `Basic` (class)
- `BehaviourName` (class)
- `BoxCollision` (class)
- `BoxView` (class)
- `Camera` (class)
- `CameraParams` (class)
- `CapsuleCollision` (class)
- `CenterOfMass` (class)
- `Clone` (class)
- `CollisionMaterial` (class)
- `CompensationMotion` (class)
- `ConnectionPointTwoBody` (class)
- `Constraint` (class)
- `ConstraintView` (class)
- `ConvexMeshCollision` (class)
- `CustomCamera` (class)
- `CustomTransformData` (class)
- `Dynamic` (class)
- `DynamicBehaviour` (class)
- `EdgeView` (class)
- `EnforceLocalCopy` (class)
- `EnforceSaveData` (class)
- `ExtendedHierarchy` (class)
- `FbxExport` (class)
- `Fixation` (class)
- `FloorCollisionRelaxationPoint` (class)
- `FulcrumGroup` (class)
- `FulcrumPoint` (class)
- `GraphChannelsData` (class)
- `HingeSettings` (class)
- `InterpolationController` (class)
- `Joint` (class)
- `JointExtraAttributes` (class)
- `KinematicMeshCollision` (class)
- `LimbDirection` (class)
- `Locator` (class)
- `ManipulatorLocker` (class)
- `MeshCollision` (class)
- `MeshObject` (class)
- `Mirror` (class)
- `NamedObjectDynamicEnum` (class)
- `Node3d` (class)
- `ObjectsContainer` (class)
- `PhysicsBody` (class)
- `PhysicsCorrector` (class)
- `PhysicsPoint` (class)
- `PhysicsSettings` (class)
- `PivotCustomization` (class)
- `Point` (class)
- `PointBall` (class)
- `PointHinge` (class)
- `PointLocalController` (class)
- `PointsUpdateSettings` (class)
- `PreservedData` (class)
- `ProtoBox` (class)
- `ProtoCenterOfMass` (class)
- `ProtoEdgeGroup` (class)
- `ProtoFulcrumGroup` (class)
- `ProtoInnerUnionBehaviour` (class)
- `ProtoPoint` (class)
- `ProtoProperties` (class)
- `ProtoRootConstraint` (class)
- `ProtoSplineIk` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `QrtInfo` (class)
- `Ragdoll` (class)
- `RigAdditionalInfo` (class)
- `RigInfo` (class)
- `RigidBody` (class)
- `RigidBodyView` (class)
- `SecondaryMotion` (class)
- `SeparationMotion` (class)
- `SeparationOfMotion` (class)
- `Sf3Joint` (class)
- `SplineIk` (class)
- `SpringSecondaryMotion` (class)
- `TechnicalLinks` (class)
- `TextureContainer` (class)
- `ToolFixation` (class)
- `TrajectoryCustomization` (class)
- `Transform` (class)
- `Twist` (class)
- `Untwist` (class)

## `pycsc.behaviours.core`

- `BaseDynamic` (class)
- `BehaviourName` (class)
- `PropertyError` (class) — Thrown when a PyBehaviour doesn't have a property of a given name
- `PropertySupportError` (class) — Thrown when pycsc needs updating to support a specific property type
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `defaultdict` (class) — The default factory is called without arguments to produce

## `pycsc.behaviours.core.properties`

- `AssetProperty` (class)
- `AssetRange` (class)
- `DataId` (class)
- `DataProperty` (class) — Represents behaviour.properties that are assigned csc.model.DataId
- `DataRange` (class)
- `MemoryId` (class)
- `MemoryProperty` (class)
- `ObjectProperty` (class) — Represents behaviour.properties that maps to object(s)
- `ObjectRange` (class)
- `Property` (class) — Base class for any Behaviour properties
- `PropertyRange` (class) — Base class for any propeties that store an list of properties
- `PropertyValueError` (class) — The value being set is incompatible with the expected property type
- `ReferenceProperty` (class) — Represents behaviour.properties that map to other behaviour(s)
- `ReferenceRange` (class)
- `SettingId` (class)
- `SettingProperty` (class) — Represents behaviour.properties that are assigned csc.model.SettingId
- `SettingRange` (class)
- `StringProperty` (class)

## `pycsc.behaviours.custom_transform_data`

- `CustomTransformData` (class)

## `pycsc.behaviours.dynamic`

- `Dynamic` (class)

## `pycsc.behaviours.dynamic_behaviour`

- `DynamicBehaviour` (class)
- `NamedObjectDynamicEnum` (class)
- `StrEnum` (class)
- `Optional` (fn)

## `pycsc.behaviours.mesh_object`

- `MeshObject` (class)
- `defaultdict` (class) — The default factory is called without arguments to produce
- `TypeAlias` (fn)

## `pycsc.behaviours.mesh_object.utils`

- `benchmark` (fn)
- `benchmark_end` (fn)
- `benchmark_start` (fn)
- `time_it` (fn) — Decorator that times a function call and prints the execution time.

## `pycsc.behaviours.technical_links`

- `TechnicalLinks` (class)

## `pycsc.behaviours.transform`

- `BaseDynamic` (class)
- `BehaviourName` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `Transform` (class)

## `pycsc.box_update`

- `AttrInterface` (class)
- `BoxUpdate` (class)
- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `DomainScene` (class) — A Wrapper around a domain scene
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `ObjectNode` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `TransformUpdate` (class)
- `Optional` (fn)
- `Union` (fn)

## `pycsc.box_view`

- `BoxView` (class)
- `Node3d` (class)

## `pycsc.character`

- `JointMeshesInfo` (class)
- `get_joint_meshes_info` (fn) — Given a joint return a JointMeshesInfo instance

## `pycsc.creation`

- `create_transform` (fn)

## `pycsc.custom_enum_description`

- `CustomEnumDescription` (class)
- `List` (fn) — A generic version of list.

## `pycsc.data_node`

- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `TypeVar` (class)
- `Iterable` (fn) — A generic version of collections.abc.Iterable.
- `List` (fn) — A generic version of list.
- `Set` (fn) — A generic version of set.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `Union` (fn)
- `compose_matrix` (fn) — compose a matrix from a rotation and position
- `connect_attributes` (fn)
- `get_full_type_name` (fn)
- `increment_name` (fn)
- `reload_module_and_submodules` (fn)
- `split_path` (fn)
- `split_path2` (fn) — split a path into a list of strings
- `split_path_first` (fn) — split a path into a list of strings
- `split_word_and_digits` (fn)

## `pycsc.data_node.data_types`

- `OrthoTransform` (class) — OrthogonalTransform class
- `Quaternion` (class) — Quaternion class
- `Rotation` (class) — Rotation class
- `Matrix` (fn) — Built-in mutable sequence.
- `RegularDataValue` (fn)
- `SettingDataValue` (fn)
- `Union` (fn)
- `Vector3` (fn)

## `pycsc.data_node.memory`

- `DataId` (class)
- `MemoryId` (class)
- `SettingId` (class)

## `pycsc.datatypes`

- `AngleConstraints` (class)
- `AnimationInfo` (class)
- `AssetProperty` (class)
- `AssetRange` (class)
- `Attr` (class)
- `AttrInterface` (class)
- `AttractionPoint` (class)
- `AutoPhysics` (class)
- `AutoPhysicsApply` (class)
- `AutoPosingInfo` (class)
- `AutoPosingLink` (class)
- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `BaseDynamic` (class)
- `BaseSubnodesDef` (class) — Base class for defining subnodes using auto().
- `Basic` (class)
- `BehaviourEditor` (class)
- `BehaviourError` (class) — Thrown when a PyObject doesn't have a behaviour of a given name
- `BehaviourName` (class)
- `BehaviourSizeError` (class) — Thrown when only one behaviour of a given type should exist
- `BoxCollision` (class)
- `BoxUpdate` (class)
- `BoxView` (class)
- `Camera` (class)
- `CameraParams` (class)
- `CapsuleCollision` (class)
- `CenterOfMass` (class)
- `Clone` (class)
- `CollisionMaterial` (class)
- `CompensationMotion` (class)
- `ConnectionPointTwoBody` (class)
- `Constraint` (class)
- `ConstraintView` (class)
- `ConvexMeshCollision` (class)
- `CscWrapper` (class)
- `CustomCamera` (class)
- `CustomEnumDescription` (class)
- `CustomTransformData` (class)
- `DataEditor` (class)
- `DataId` (class)
- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `DataProperty` (class) — Represents behaviour.properties that are assigned csc.model.DataId
- `DataRange` (class)
- `DomainScene` (class) — A Wrapper around a domain scene
- `Dynamic` (class)
- `DynamicBehaviour` (class)
- `EdgeView` (class)
- `EditorError` (class) — Thrown when someone attempts to access and editor at an invalid time
- `EnforceLocalCopy` (class)
- `EnforceSaveData` (class)
- `ExtendedHierarchy` (class)
- `FbxExport` (class)
- `Fixation` (class)
- `FloorCollisionRelaxationPoint` (class)
- `Folder` (class) — Wrapper for csc.layers.Folder class.
- `FulcrumGroup` (class)
- `FulcrumPoint` (class)
- `FuncNode` (class)
- `GraphChannelsData` (class)
- `GroupNode` (class) — Wrapper for csc.update.UpdateGroup
- `HingeSettings` (class)
- `InternalSceneElement` (class) — Used for classes that need to override methods of the class it wraps
- `InterpolationController` (class)
- `IterSceneElement` (class)
- `Joint` (class)
- `JointExtraAttributes` (class)
- `JointUpdate` (class)
- `KinematicMeshCollision` (class)
- `Layer` (class)
- `LayersAccess` (class) — Provides access to layer operations and queries.
- `LimbDirection` (class)
- `Locator` (class)
- `ManipulatorLocker` (class)
- `MemoryId` (class)
- `MemoryProperty` (class)
- `MeshCollision` (class)
- `MeshObject` (class)
- `Mirror` (class)
- `MissingGroupError` (class)
- `ModelEditor` (class)
- `NamedObjectDynamicEnum` (class)
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `Node3d` (class)
- `NodeGuid` (class)
- `ObjectNode` (class)
- `ObjectProperty` (class) — Represents behaviour.properties that maps to object(s)
- `ObjectRange` (class)
- `ObjectsContainer` (class)
- `PathName` (class)
- `PhysicsBody` (class)
- `PhysicsCorrector` (class)
- `PhysicsPoint` (class)
- `PhysicsSettings` (class)
- `PivotCustomization` (class)
- `Point` (class)
- `PointBall` (class)
- `PointHinge` (class)
- `PointLocalController` (class)
- `PointsUpdateSettings` (class)
- `PreservedData` (class)
- `Property` (class) — Base class for any Behaviour properties
- `PropertyRange` (class) — Base class for any propeties that store an list of properties
- `PropertyValueError` (class) — The value being set is incompatible with the expected property type
- `ProtoBox` (class)
- `ProtoCenterOfMass` (class)
- `ProtoEdgeGroup` (class)
- `ProtoFulcrumGroup` (class)
- `ProtoInnerUnionBehaviour` (class)
- `ProtoPoint` (class)
- `ProtoProperties` (class)
- `ProtoRootConstraint` (class)
- `ProtoSplineIk` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyGuid` (class) — Base class for wrappping csc.Guid and all Ids
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `QrtInfo` (class)
- `Ragdoll` (class)
- `ReferenceProperty` (class) — Represents behaviour.properties that map to other behaviour(s)
- `ReferenceRange` (class)
- `RigAdditionalInfo` (class)
- `RigInfo` (class)
- `RigidBody` (class)
- `RigidBodyView` (class)
- `SceneElement` (class) — Base class used to represent any wrapped data existing/related to a scene
- `SceneUpdater` (class)
- `SecondaryMotion` (class)
- `SeparationMotion` (class)
- `SeparationOfMotion` (class)
- `SettingId` (class)
- `SettingProperty` (class) — Represents behaviour.properties that are assigned csc.model.SettingId
- `SettingRange` (class)
- `Sf3Joint` (class)
- `SplineIk` (class)
- `SpringSecondaryMotion` (class)
- `StringProperty` (class)
- `TechnicalLinks` (class)
- `TextureContainer` (class)
- `Timeline` (class) — High-level operations for frame manipulation in the timeline.
- `TimelineNode` (class) — Base class for nodes in the timeline hierarchy (layers and folders).
- `ToolFixation` (class)
- `TrajectoryCustomization` (class)
- `Transform` (class)
- `TransformUpdate` (class)
- `Twist` (class)
- `Untwist` (class)
- `UpdateEditor` (class)
- `ViewScene` (class) — A Wrapper around a view scene
- `ViewersEditors` (class)
- `Optional` (fn)
- `Type` (fn) — A special construct usable to annotate class objects.
- `run_edit_update` (fn) — start editing the given csc.domain.Scene as first argument
- `run_generate_update` (fn) — start editing the current scene
- `run_update_session` (fn) — start editing the current scene
- `total_ordering` (fn)

## `pycsc.datatypes.descriptors`

- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `BaseSubnodesDef` (class) — Base class for defining subnodes using auto().

## `pycsc.datatypes.descriptors.node_descriptors`

- `Any` (class)
- `Generic` (class)
- `TypeVar` (class)
- `definitions_proxy` (fn) — Return a proxy for Inputs/Outputs/Subnodes that supports `.get` resolution.

## `pycsc.datatypes.domain`

- `AngleConstraints` (class)
- `AnimationInfo` (class)
- `AssetProperty` (class)
- `AssetRange` (class)
- `AttractionPoint` (class)
- `AutoPhysics` (class)
- `AutoPhysicsApply` (class)
- `AutoPosingInfo` (class)
- `AutoPosingLink` (class)
- `BaseDynamic` (class)
- `Basic` (class)
- `BehaviourEditor` (class)
- `BehaviourError` (class) — Thrown when a PyObject doesn't have a behaviour of a given name
- `BehaviourName` (class)
- `BehaviourSizeError` (class) — Thrown when only one behaviour of a given type should exist
- `BoxCollision` (class)
- `BoxView` (class)
- `Camera` (class)
- `CameraParams` (class)
- `CapsuleCollision` (class)
- `CenterOfMass` (class)
- `Clone` (class)
- `CollisionMaterial` (class)
- `CompensationMotion` (class)
- `ConnectionPointTwoBody` (class)
- `Constraint` (class)
- `ConstraintView` (class)
- `ConvexMeshCollision` (class)
- `CustomCamera` (class)
- `CustomEnumDescription` (class)
- `CustomTransformData` (class)
- `DataEditor` (class)
- `DataId` (class)
- `DataProperty` (class) — Represents behaviour.properties that are assigned csc.model.DataId
- `DataRange` (class)
- `DomainScene` (class) — A Wrapper around a domain scene
- `Dynamic` (class)
- `DynamicBehaviour` (class)
- `EdgeView` (class)
- `EditorError` (class) — Thrown when someone attempts to access and editor at an invalid time
- `EnforceLocalCopy` (class)
- `EnforceSaveData` (class)
- `ExtendedHierarchy` (class)
- `FbxExport` (class)
- `Fixation` (class)
- `FloorCollisionRelaxationPoint` (class)
- `Folder` (class) — Wrapper for csc.layers.Folder class.
- `FulcrumGroup` (class)
- `FulcrumPoint` (class)
- `GraphChannelsData` (class)
- `HingeSettings` (class)
- `InternalSceneElement` (class) — Used for classes that need to override methods of the class it wraps
- `InterpolationController` (class)
- `IterSceneElement` (class)
- `Joint` (class)
- `JointExtraAttributes` (class)
- `KinematicMeshCollision` (class)
- `Layer` (class)
- `LayersAccess` (class) — Provides access to layer operations and queries.
- `LimbDirection` (class)
- `Locator` (class)
- `ManipulatorLocker` (class)
- `MemoryId` (class)
- `MemoryProperty` (class)
- `MeshCollision` (class)
- `MeshObject` (class)
- `Mirror` (class)
- `MissingGroupError` (class)
- `ModelEditor` (class)
- `NamedObjectDynamicEnum` (class)
- `Node3d` (class)
- `NodeGuid` (class)
- `ObjectProperty` (class) — Represents behaviour.properties that maps to object(s)
- `ObjectRange` (class)
- `ObjectsContainer` (class)
- `PathName` (class)
- `PhysicsBody` (class)
- `PhysicsCorrector` (class)
- `PhysicsPoint` (class)
- `PhysicsSettings` (class)
- `PivotCustomization` (class)
- `Point` (class)
- `PointBall` (class)
- `PointHinge` (class)
- `PointLocalController` (class)
- `PointsUpdateSettings` (class)
- `PreservedData` (class)
- `Property` (class) — Base class for any Behaviour properties
- `PropertyRange` (class) — Base class for any propeties that store an list of properties
- `PropertyValueError` (class) — The value being set is incompatible with the expected property type
- `ProtoBox` (class)
- `ProtoCenterOfMass` (class)
- `ProtoEdgeGroup` (class)
- `ProtoFulcrumGroup` (class)
- `ProtoInnerUnionBehaviour` (class)
- `ProtoPoint` (class)
- `ProtoProperties` (class)
- `ProtoRootConstraint` (class)
- `ProtoSplineIk` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyGuid` (class) — Base class for wrappping csc.Guid and all Ids
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `QrtInfo` (class)
- `Ragdoll` (class)
- `ReferenceProperty` (class) — Represents behaviour.properties that map to other behaviour(s)
- `ReferenceRange` (class)
- `RigAdditionalInfo` (class)
- `RigInfo` (class)
- `RigidBody` (class)
- `RigidBodyView` (class)
- `SceneElement` (class) — Base class used to represent any wrapped data existing/related to a scene
- `SceneUpdater` (class)
- `SecondaryMotion` (class)
- `SeparationMotion` (class)
- `SeparationOfMotion` (class)
- `SettingId` (class)
- `SettingProperty` (class) — Represents behaviour.properties that are assigned csc.model.SettingId
- `SettingRange` (class)
- `Sf3Joint` (class)
- `SplineIk` (class)
- `SpringSecondaryMotion` (class)
- `StringProperty` (class)
- `TechnicalLinks` (class)
- `TextureContainer` (class)
- `Timeline` (class) — High-level operations for frame manipulation in the timeline.
- `TimelineNode` (class) — Base class for nodes in the timeline hierarchy (layers and folders).
- `ToolFixation` (class)
- `TrajectoryCustomization` (class)
- `Transform` (class)
- `Twist` (class)
- `Untwist` (class)
- `UpdateEditor` (class)
- `ViewScene` (class) — A Wrapper around a view scene
- `ViewersEditors` (class)
- `Optional` (fn)
- `Type` (fn) — A special construct usable to annotate class objects.
- `total_ordering` (fn)

## `pycsc.datatypes.domain.joint`

- `Joint` (class)
- `Node3d` (class)

## `pycsc.datatypes.domain.layers`

- `Any` (class)
- `Folder` (class) — Wrapper for csc.layers.Folder class.
- `Layer` (class)
- `LayersAccess` (class) — Provides access to layer operations and queries.
- `SceneElement` (class) — Base class used to represent any wrapped data existing/related to a scene
- `TimelineNode` (class) — Base class for nodes in the timeline hierarchy (layers and folders).
- `List` (fn) — A generic version of list.
- `Optional` (fn)
- `Union` (fn)

## `pycsc.datatypes.domain.node_3d`

- `Node3d` (class)

## `pycsc.datatypes.domain.node_3d.core`

- `BehaviourError` (class) — Thrown when a PyObject doesn't have a behaviour of a given name
- `BehaviourSizeError` (class) — Thrown when only one behaviour of a given type should exist
- `MissingGroupError` (class)
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `Optional` (fn)
- `Type` (fn) — A special construct usable to annotate class objects.

## `pycsc.datatypes.domain.objects`

- `BehaviourError` (class) — Thrown when a PyObject doesn't have a behaviour of a given name
- `BehaviourSizeError` (class) — Thrown when only one behaviour of a given type should exist
- `MissingGroupError` (class)
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `Optional` (fn)
- `Type` (fn) — A special construct usable to annotate class objects.

## `pycsc.datatypes.domain.objects.points`

- `Point` (class)
- `ProtoLocker` (class)
- `ProtoPoint` (class)
- `ProxyAdditionalPoint` (class)
- `ProxyDirectionPoint` (class)
- `ProxyEndFinger` (class)
- `ProxyManualPoint` (class)

## `pycsc.datatypes.domain.objects.points.point`

- `Point` (class)
- `ProtoLocker` (class)

## `pycsc.datatypes.domain.objects.points.proto_point`

- `Point` (class)
- `ProtoPoint` (class)

## `pycsc.datatypes.domain.objects.points.proxy_additional_point`

- `ProtoPoint` (class)
- `ProxyAdditionalPoint` (class)

## `pycsc.datatypes.domain.objects.points.proxy_direction_point`

- `ProtoPoint` (class)
- `ProxyDirectionPoint` (class)

## `pycsc.datatypes.domain.objects.points.proxy_end_finger`

- `Point` (class)
- `ProxyEndFinger` (class)

## `pycsc.datatypes.domain.objects.points.proxy_manual_point`

- `ProtoPoint` (class)
- `ProxyManualPoint` (class)

## `pycsc.datatypes.domain.objects.proto_locker`

- `ProtoLocker` (class)
- `ProtoProperties` (class)

## `pycsc.datatypes.domain.objects.proto_properties`

- `Node3d` (class)
- `ProtoProperties` (class)

## `pycsc.datatypes.domain.objects.proxy_additional_box`

- `ProtoProperties` (class)
- `ProxyAdditionalBox` (class)

## `pycsc.datatypes.domain.objects.proxy_box`

- `BoxView` (class)
- `Joint` (class)
- `ProxyBox` (class)
- `PyObject` (class) — Wrapper around ccs.model.ObjectId

## `pycsc.datatypes.domain.objects.proxy_collision`

- `ProtoLocker` (class)
- `ProxyCollision` (class)

## `pycsc.datatypes.domain.objects.proxy_inner`

- `ProtoProperties` (class)
- `ProxyInner` (class)

## `pycsc.datatypes.domain.objects.proxy_rigid_body`

- `ProtoProperties` (class)
- `ProxyRigidBody` (class)

## `pycsc.datatypes.domain.objects.rig_element`

- `Node3d` (class)
- `RigElement` (class)

## `pycsc.datatypes.domain.path_name`

- `PathName` (class)
- `total_ordering` (fn)

## `pycsc.datatypes.domain.timeline`

- `Folder` (class) — Wrapper for csc.layers.Folder class.
- `Layer` (class)
- `SceneElement` (class) — Base class used to represent any wrapped data existing/related to a scene
- `Timeline` (class) — High-level operations for frame manipulation in the timeline.
- `TimelineNode` (class) — Base class for nodes in the timeline hierarchy (layers and folders).
- `List` (fn) — A generic version of list.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.

## `pycsc.datatypes.domain.timeline_nodes`

- `Folder` (class) — Wrapper for csc.layers.Folder class.
- `Layer` (class)
- `PyGuid` (class) — Base class for wrappping csc.Guid and all Ids
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `TimelineNode` (class) — Base class for nodes in the timeline hierarchy (layers and folders).

## `pycsc.datatypes.domain.update_datas`

- `Attr` (class)
- `AttrInterface` (class)
- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `BaseSubnodesDef` (class) — Base class for defining subnodes using auto().
- `BoxUpdate` (class)
- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `FuncNode` (class)
- `GroupNode` (class) — Wrapper for csc.update.UpdateGroup
- `JointUpdate` (class)
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `ObjectNode` (class)
- `TransformUpdate` (class)
- `run_edit_update` (fn) — start editing the given csc.domain.Scene as first argument
- `run_generate_update` (fn) — start editing the current scene
- `run_update_session` (fn) — start editing the current scene

## `pycsc.datatypes.domain.update_datas.extra_nodes`

- `BoxUpdate` (class)
- `JointUpdate` (class)
- `TransformUpdate` (class)

## `pycsc.datatypes.domain.update_datas.extra_nodes.joint_update`

- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `DomainScene` (class) — A Wrapper around a domain scene
- `JointUpdate` (class)
- `ObjectNode` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `TransformUpdate` (class)
- `auto` (class)
- `Optional` (fn)
- `Union` (fn)

## `pycsc.datatypes.domain.update_datas.extra_nodes.transform_update`

- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `DomainScene` (class) — A Wrapper around a domain scene
- `ObjectNode` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `TransformUpdate` (class)
- `Union` (fn)

## `pycsc.datatypes.domain.update_datas.func_node`

- `FuncNode` (class)
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `TypeVar` (class)
- `List` (fn) — A generic version of list.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `Union` (fn)
- `compose_matrix` (fn) — compose a matrix from a rotation and position
- `connect_attributes` (fn)
- `get_full_type_name` (fn)
- `increment_name` (fn)
- `reload_module_and_submodules` (fn)
- `split_path` (fn)
- `split_path2` (fn) — split a path into a list of strings
- `split_path_first` (fn) — split a path into a list of strings
- `split_word_and_digits` (fn)

## `pycsc.datatypes.domain.update_datas.group_nodes`

- `Any` (class)
- `BaseGroupNode` (class)
- `DomainScene` (class) — A Wrapper around a domain scene
- `GroupNode` (class) — Wrapper for csc.update.UpdateGroup
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `ObjectGroupNode` (class)
- `TypeVar` (class)
- `List` (fn) — A generic version of list.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `Union` (fn)
- `compose_matrix` (fn) — compose a matrix from a rotation and position
- `connect_attributes` (fn)
- `get_full_type_name` (fn)
- `increment_name` (fn)
- `reload_module_and_submodules` (fn)
- `split_path` (fn)
- `split_path2` (fn) — split a path into a list of strings
- `split_path_first` (fn) — split a path into a list of strings
- `split_word_and_digits` (fn)

## `pycsc.datatypes.domain.update_datas.node`

- `Attr` (class)
- `AttrInterface` (class)
- `BaseAttrDef` (class) — Base class for defining attributes using auto().
- `BaseSubnodesDef` (class) — Base class for defining subnodes using auto().
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `ClassVar` (fn)
- `List` (fn) — A generic version of list.
- `Set` (fn) — A generic version of set.
- `definitions_proxy` (fn) — Return a proxy for Inputs/Outputs/Subnodes that supports `.get` resolution.
- `get_call_stack` (fn)
- `get_full_type_name` (fn)

## `pycsc.datatypes.domain.update_datas.nodes`

- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `FuncNode` (class)
- `GroupNode` (class) — Wrapper for csc.update.UpdateGroup
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `ObjectNode` (class)

## `pycsc.datatypes.domain.update_datas.nodes.object_node`

- `Attr` (class)
- `AttrInterface` (class)
- `BehaviourName` (class)
- `DataNode` (class) — Wrapper class around csc.update.RegularData
- `DomainScene` (class) — A Wrapper around a domain scene
- `GroupNode` (class) — Wrapper for csc.update.UpdateGroup
- `Node` (class) — Node class is a wrapper for csc.update.Node object. It provides a set of methods to work with the node object.
- `ObjectNode` (class)
- `PyBehaviour` (class) — A wrapper for Cascadeur Behaviours
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `TransformValue` (class)
- `TypeVar` (class)
- `List` (fn) — A generic version of list.
- `Optional` (fn)
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `Type` (fn) — A special construct usable to annotate class objects.
- `Union` (fn)
- `compose_matrix` (fn) — compose a matrix from a rotation and position
- `connect_attributes` (fn)
- `get_full_type_name` (fn)
- `increment_name` (fn)
- `reload_module_and_submodules` (fn)
- `split_path` (fn)
- `split_path2` (fn) — split a path into a list of strings
- `split_path_first` (fn) — split a path into a list of strings
- `split_word_and_digits` (fn)

## `pycsc.datatypes.domain.update_datas.runners`

- `TypeVar` (class)
- `UpdateContext` (class)
- `Dict` (fn) — A generic version of dict.
- `Union` (fn)
- `get_full_type_name` (fn)
- `run_edit_update` (fn) — start editing the given csc.domain.Scene as first argument
- `run_generate_update` (fn) — start editing the current scene
- `run_update_session` (fn) — start editing the current scene
- `run_update_with_session` (fn)

## `pycsc.datatypes.domain.update_datas.utils`

- `TypeVar` (class)
- `List` (fn) — A generic version of list.
- `Tuple` (fn) — Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
- `compose_matrix` (fn) — compose a matrix from a rotation and position
- `connect_attributes` (fn)
- `increment_name` (fn)
- `reload_module_and_submodules` (fn)
- `split_path` (fn)
- `split_path2` (fn) — split a path into a list of strings
- `split_path_first` (fn) — split a path into a list of strings
- `split_word_and_digits` (fn)

## `pycsc.datatypes.domain.viewers_editors`

- `BehaviourEditor` (class)
- `DataEditor` (class)
- `ModelEditor` (class)
- `SceneUpdater` (class)
- `UpdateEditor` (class)

## `pycsc.enums`

- `ConstantData` (class)
- `ConstantSetting` (class)
- `ExternalProperty` (class)
- `Space` (class)

## `pycsc.fbx`

- `FbxFilterType` (class)
- `IntEnum` (class)
- `auto` (class)
- `current_fbx_loader` (fn) — Returns the FbxLoader for the current scene
- `export_fbx` (fn) — Export an fbx file to the target file location
- `import_fbx` (fn) — Import the fbx file into Cascadeur.

## `pycsc.fbx.wrapping`

- `get_current_scene` (fn) — Get the current scene
- `get_scene_objects` (fn) — get objects based on the input filters
- `new_scene` (fn) — Creates a new scene and makes it the active scene
- `wrap` (fn) — Return the wrapped version of a csc object
- `wrap_scene_element` (fn) — wrap the input object with the current scene as the creator

## `pycsc.general`

- `JointMeshesInfo` (class)
- `get_current_scene` (fn) — Get the current scene
- `get_joint_meshes_info` (fn) — Given a joint return a JointMeshesInfo instance
- `get_scene_objects` (fn) — get objects based on the input filters
- `new_scene` (fn) — Creates a new scene and makes it the active scene
- `wrap` (fn) — Return the wrapped version of a csc object
- `wrap_scene_element` (fn) — wrap the input object with the current scene as the creator

## `pycsc.general.rigging`

- `get_rig_elements` (fn)

## `pycsc.hierarchy`

- `InvalidParentError` (class)
- `NewType` (class)
- `ObjectId` (fn)
- `ParentId` (fn)
- `ParentType` (fn)
- `check_relationship_inclusive` (fn) — Check if object_parent_id is a parent of object_child_id.
- `child_scale_compensate` (fn)
- `constant_name` (fn) — Get the constant name for a given attribute name.
- `find_parent_by_type` (fn) — Returns the first parent in the hierarchy that matches the given object type.
- `get_all_related_objects` (fn)
- `get_hierarchy_structure` (fn)
- `get_object_branch_inclusive` (fn)
- `get_parent_list` (fn) — Return a list of parents for the given input obj_id.
- `get_parent_paths` (fn)
- `get_suffix` (fn) — Extract suffix from parent input names like 'Parent Position'.
- `is_standard_3d_obj` (fn)
- `modify_basic` (fn) — Modify the basic behavior and collect actual transform data.
- `object_depth` (fn)
- `set_parent` (fn)
- `set_parent_by_id` (fn)
- `set_parent_in_basic_behaviour` (fn)
- `set_parents` (fn)
- `set_parents_mod` (fn)
- `sort_objects_by_depth` (fn)

## `pycsc.objects`

- `BoxView` (class)
- `Joint` (class)
- `Node3d` (class)
- `Point` (class)
- `ProtoLocker` (class)
- `ProtoPoint` (class)
- `ProtoProperties` (class)
- `ProxyAdditionalBox` (class)
- `ProxyAdditionalPoint` (class)
- `ProxyBox` (class)
- `ProxyCollision` (class)
- `ProxyDirectionPoint` (class)
- `ProxyEndFinger` (class)
- `ProxyInner` (class)
- `ProxyManualPoint` (class)
- `ProxyRigidBody` (class)
- `PyObject` (class) — Wrapper around ccs.model.ObjectId
- `RigElement` (class)

## `pycsc.types_helper`

- `debug_print_call_stack` (fn)
- `get_call_stack` (fn)
- `get_full_type_name` (fn)

