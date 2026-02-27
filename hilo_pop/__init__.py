bl_info = {
    "name": "HiLo Pop",
    "author": "Kyrivane",
    "version": (0, 7, 1),
    "blender": (4, 5, 0),
    "location": "View3D > Add > Mesh (+ Pie Hotkey)",
    "description": "Popup naming for _high or derive _low from source. Pie menu hotkey can be recorded in preferences.",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Menu
from bpy.props import StringProperty, PointerProperty, IntProperty, BoolProperty, EnumProperty

_addon_keymaps = []

# Keymap helpers


def _clear_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def _apply_keymap():
    """Recreate addon keymap based on stored prefs."""
    _clear_keymaps()

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if not kc:
        return

    prefs = bpy.context.preferences.addons[__name__].preferences
    if not prefs.hotkey_enabled:
        return

    if not prefs.hotkey_key or prefs.hotkey_key == 'NONE':
        return

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        type=prefs.hotkey_key,
        value="PRESS",
        ctrl=prefs.hotkey_ctrl,
        alt=prefs.hotkey_alt,
        shift=prefs.hotkey_shift,
    )
    kmi.properties.name = "VIEW3D_MT_hilop_pie"
    _addon_keymaps.append((km, kmi))


def _hotkey_string(prefs) -> str:
    if not prefs.hotkey_key or prefs.hotkey_key == 'NONE':
        return "Not set"
    mods = []
    if prefs.hotkey_ctrl:
        mods.append("Ctrl")
    if prefs.hotkey_alt:
        mods.append("Alt")
    if prefs.hotkey_shift:
        mods.append("Shift")
    mods.append(prefs.hotkey_key.title())
    return " ".join(mods)


def _prefs():
    return bpy.context.preferences.addons[__name__].preferences

# Addon Preferences


class HILOP_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    popup_width: IntProperty(
        name="Popup Width",
        description="Width of the naming popup (height is automatic)",
        default=300,
        min=200,
        max=10000,
    )

    hotkey_enabled: BoolProperty(
        name="Enable Pie Hotkey",
        default=True,
        update=lambda self, ctx: _apply_keymap(),
    )

    hotkey_key: EnumProperty(
        name="Key",
        items=[('NONE', "None", "No key assigned")] + [(k, k, "") for k in [
            # letters
            "A","B","C","D","E","F","G","H","I","J","K","L","M",
            "N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
            # numbers
            "ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","ZERO",
            # function keys
            "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
            # misc
            "SPACE","TAB","RET","ESC","BACK_SPACE",
        ]],
        default="Q",
        update=lambda self, ctx: _apply_keymap(),
    )

    hotkey_ctrl: BoolProperty(name="Ctrl", default=False, update=lambda self, ctx: _apply_keymap())
    hotkey_alt: BoolProperty(name="Alt", default=True, update=lambda self, ctx: _apply_keymap())
    hotkey_shift: BoolProperty(name="Shift", default=False, update=lambda self, ctx: _apply_keymap())

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "popup_width")

        layout.separator()
        layout.label(text="Pie Menu Hotkey")

        layout.prop(self, "hotkey_enabled")

        row = layout.row(align=True)
        row.enabled = self.hotkey_enabled
        row.operator("hilop.record_hotkey", text=_hotkey_string(self), icon='REC')
        row.operator("hilop.clear_hotkey", text="Reset", icon='LOOP_BACK')

# Record/Clear hotkey operators


class HILOP_OT_record_hotkey(bpy.types.Operator):
    """Press the desired hotkey combination"""
    bl_idname = "hilop.record_hotkey"
    bl_label = "Record HiLo Pop Hotkey"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, "Press desired hotkey (Esc to cancel).")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            return {'CANCELLED'}
        if event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_SHIFT', 'RIGHT_SHIFT', 'LEFT_ALT', 'RIGHT_ALT'}:
            return {'RUNNING_MODAL'}
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'RUNNING_MODAL'}
        if event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}:
            return {'RUNNING_MODAL'}
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        prefs = _prefs()

        prefs.hotkey_ctrl = bool(event.ctrl)
        prefs.hotkey_alt = bool(event.alt)
        prefs.hotkey_shift = bool(event.shift)

        try:
            prefs.hotkey_key = event.type
        except Exception:
            prefs.hotkey_key = 'NONE'

        _apply_keymap()
        self.report({'INFO'}, f"Hotkey set to: {_hotkey_string(prefs)}")
        return {'FINISHED'}

class OBJECT_OT_hilop_add_high_suffix(bpy.types.Operator):
    bl_idname = "object.hilop_add_high_suffix"
    bl_label = "HiLo Pop: High (only name)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(getattr(context, "selected_objects", None))

    def execute(self, context):
        objs = list(context.selected_objects)
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        changed = 0
        for obj in objs:
            if obj is None:
                continue
            new_name = _set_hilo_suffix(obj.name, "high")
            if new_name != obj.name:
                obj.name = new_name
                changed += 1

        self.report({'INFO'}, f"Set _high on {changed} object(s).")
        return {'FINISHED'}

class OBJECT_OT_hilop_rename_multi(bpy.types.Operator):
    bl_idname = "object.hilop_rename_multi"
    bl_label = "HiLo Pop: Rename (Multi)"
    bl_options = {'REGISTER', 'UNDO'}

    base_name: bpy.props.StringProperty(
        name="Base Name",
        default="",
    )

    start_index: bpy.props.IntProperty(
        name="Start",
        default=1,
        min=1,
    )

    digits: bpy.props.IntProperty(
        name="Digits",
        default=3,
        min=1,
        max=6,
    )

    @classmethod
    def poll(cls, context):
        return bool(getattr(context, "selected_objects", None))

    def invoke(self, context, event):
        objs = list(context.selected_objects)
        active = context.view_layer.objects.active
        if objs:
            first = None
            for o in objs:
                if o != active:
                    first = o
                    break
            if first is None:
                first = active if active in objs else objs[0]

            self.base_name = first.name if first else ""
        else:
            self.base_name = ""
        if self.base_name is None:
            self.base_name = ""

        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "base_name")
    def execute(self, context):
        objs = list(context.selected_objects)
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        active = context.view_layer.objects.active
        if active in objs:
            objs = [o for o in objs if o != active] + [active]

        base = (self.base_name or "").strip()
        if not base:
            self.report({'ERROR'}, "Base name is empty.")
            return {'CANCELLED'}

        used = set(bpy.data.objects.keys())

        idx = self.start_index
        changed = 0

        for obj in objs:
            while True:
                suffix = str(idx).zfill(self.digits)
                new_name = f"{base}.{suffix}"
                if new_name not in used or new_name == obj.name:
                    break
                idx += 1

            if obj.name in used:
                used.discard(obj.name)
            obj.name = new_name
            used.add(new_name)

            idx += 1
            changed += 1

        self.report({'INFO'}, f"Renamed {changed} object(s).")
        return {'FINISHED'}

class OBJECT_OT_hilop_add_low_suffix(bpy.types.Operator):
    bl_idname = "object.hilop_add_low_suffix"
    bl_label = "HiLo Pop: Low (only name)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(getattr(context, "selected_objects", None))

    def execute(self, context):
        objs = list(context.selected_objects)
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        changed = 0
        for obj in objs:
            if obj is None:
                continue
            new_name = _set_hilo_suffix(obj.name, "low")
            if new_name != obj.name:
                obj.name = new_name
                changed += 1

        self.report({'INFO'}, f"Set _low on {changed} object(s).")
        return {'FINISHED'}

class HILOP_OT_clear_hotkey(bpy.types.Operator):
    bl_idname = "hilop.clear_hotkey"
    bl_label = "Reset HiLo Pop Hotkey"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = _prefs()

        # Default: Alt + Q
        prefs.hotkey_key = 'Q'
        prefs.hotkey_ctrl = False
        prefs.hotkey_alt = True
        prefs.hotkey_shift = False

        _apply_keymap()
        self.report({'INFO'}, "Hotkey reset to default: Alt Q")
        return {'FINISHED'}

# Naming + creation helpers


def _cursor_loc(context):
    try:
        return context.scene.cursor.location.copy()
    except Exception:
        return (0.0, 0.0, 0.0)

def _set_hilo_suffix(name: str, target: str) -> str:
    """
    target: 'high' or 'low'
    Ensures name ends with exactly one suffix: _high or _low.
    If already ends with _high/_low -> replace, else append.
    """
    name = (name or "").strip()
    if not name:
        name = "Object"

    if name.endswith("_high"):
        return name[:-5] + f"_{target}"
    if name.endswith("_low"):
        return name[:-4] + f"_{target}"

    return name + f"_{target}"


def _ensure_high(name: str) -> str:
    name = (name or "").strip()
    if not name:
        name = "Object"
    return name if name.endswith("_high") else name + "_high"


def _to_low_from_ref(ref_name: str) -> str:
    ref_name = (ref_name or "").strip()
    if not ref_name:
        return "Object_low"
    if ref_name.endswith("_high"):
        return ref_name[:-5] + "_low"
    if ref_name.endswith("_low"):
        return ref_name
    return ref_name + "_low"


def _final_name(base_name: str, ref_obj) -> str:
    if ref_obj is not None:
        return _to_low_from_ref(ref_obj.name)
    return _ensure_high(base_name)


def _add_plane_at_cursor(context):
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, location=_cursor_loc(context))


def _add_uv_sphere_at_cursor(context):
    bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=False, location=_cursor_loc(context))


def _reset_scene_fields(scene):
    scene.hilop_base_name = ""
    scene.hilop_high_obj = None


def _addon_prefs(context):
    return context.preferences.addons[__name__].preferences

# Operators


class MESH_OT_hilop_plane(bpy.types.Operator):
    bl_idname = "mesh.hilop_plane"
    bl_label = "HiLo Pop: N Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        _reset_scene_fields(context.scene)
        w = _addon_prefs(context).popup_width
        return context.window_manager.invoke_props_dialog(self, width=w)

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row()
        row.enabled = (scn.hilop_high_obj is None)
        row.prop(scn, "hilop_base_name", text="Object Name")
        layout.prop(scn, "hilop_high_obj", text="High to Low Source")

        layout.separator()
        preview = _final_name(scn.hilop_base_name, scn.hilop_high_obj)
        layout.label(text=f"Result: {preview}", icon='OUTLINER_OB_MESH')

    def execute(self, context):
        scn = context.scene
        _add_plane_at_cursor(context)
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "Failed to create Plane.")
            return {'CANCELLED'}
        obj.name = _final_name(scn.hilop_base_name, scn.hilop_high_obj)
        return {'FINISHED'}


class MESH_OT_hilop_uv_sphere(bpy.types.Operator):
    bl_idname = "mesh.hilop_uv_sphere"
    bl_label = "HiLo Pop: N UV Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        _reset_scene_fields(context.scene)
        w = _addon_prefs(context).popup_width
        return context.window_manager.invoke_props_dialog(self, width=w)

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row()
        row.enabled = (scn.hilop_high_obj is None)
        row.prop(scn, "hilop_base_name", text="Object Name")
        layout.prop(scn, "hilop_high_obj", text="High to Low Source")

        layout.separator()
        preview = _final_name(scn.hilop_base_name, scn.hilop_high_obj)
        layout.label(text=f"Result: {preview}", icon='OUTLINER_OB_MESH')

    def execute(self, context):
        scn = context.scene
        _add_uv_sphere_at_cursor(context)
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "Failed to create UV Sphere.")
            return {'CANCELLED'}
        obj.name = _final_name(scn.hilop_base_name, scn.hilop_high_obj)
        return {'FINISHED'}

# Pie Menu


class VIEW3D_MT_hilop_pie(Menu):
    bl_label = "HiLo Pop"

    def draw(self, context):
        pie = self.layout.menu_pie()

        pie.operator("object.hilop_add_high_suffix", text="High (only name)", icon='SORTALPHA')
        pie.operator("object.hilop_add_low_suffix", text="Low (only name)", icon='SORTALPHA')

        pie.operator("mesh.hilop_plane", text="N Plane", icon='MESH_PLANE')
        pie.operator("mesh.hilop_uv_sphere", text="N UV Sphere", icon='MESH_UVSPHERE')

        pie.operator("object.hilop_rename_multi", text="Rename (Multi)", icon='OUTLINER_OB_FONT')

# Add > Mesh menu integration (TOP)


def menu_func_mesh_add(self, context):
    layout = self.layout
    layout.operator("mesh.hilop_plane", text="N Plane", icon='MESH_PLANE')
    layout.operator("mesh.hilop_uv_sphere", text="N UV Sphere", icon='MESH_UVSPHERE')
    layout.separator()

# Register / Unregister


classes = (
    HILOP_AddonPreferences,
    HILOP_OT_record_hotkey,
    HILOP_OT_clear_hotkey,
    OBJECT_OT_hilop_add_high_suffix,
    OBJECT_OT_hilop_add_low_suffix,
    OBJECT_OT_hilop_rename_multi,
    MESH_OT_hilop_plane,
    MESH_OT_hilop_uv_sphere,
    VIEW3D_MT_hilop_pie,
)


def register():
    bpy.types.Scene.hilop_base_name = StringProperty(name="Object Name", default="")
    bpy.types.Scene.hilop_high_obj = PointerProperty(name="High to Low Source", type=bpy.types.Object)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func_mesh_add)

    _apply_keymap()


def unregister():
    _clear_keymaps()
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func_mesh_add)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hilop_base_name
    del bpy.types.Scene.hilop_high_obj


if __name__ == "__main__":
    register()