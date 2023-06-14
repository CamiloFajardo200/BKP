import bpy


class MyPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_my_panel"
    bl_label = "My Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Connect Animation"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="First Armature name:")
        row.prop(context.scene, "first_armature_name", text="")
        row = layout.row()
        row.label(text="Second Armature name:")
        row.prop(context.scene, "second_armature_name", text="")
        row = layout.row()
        row.label(text="Root bone name:")
        row.prop(context.scene, "root_bone_name", text="")
        row = layout.row()
        row.operator("my_script.run_script")


class MyScriptOperator(bpy.types.Operator):
    bl_idname = "my_script.run_script"
    bl_label = "Run Script"

    def execute(self, context):
        first_armature_name = context.scene.first_armature_name
        second_armature_name = context.scene.second_armature_name
        root_bone_name = context.scene.root_bone_name

        # Get the armatures
        model = bpy.data.objects[first_armature_name]
        model1 = bpy.data.objects[second_armature_name]
        bone_name = root_bone_name

        # Rename the actions
        model.animation_data.action.name = "action"
        model1.animation_data.action.name = "action1"

        # Push down the actions in the nonlinear animation editor
        bpy.context.area.type = 'NLA_EDITOR'
        bpy.ops.nla.action_pushdown(channel_index=1)
        bpy.ops.nla.action_pushdown(channel_index=4)

        # Delete the model1 object
        bpy.data.objects.remove(model1, do_unlink=True)

        # Add "action1" as an action strip on a new NLA track
        bpy.context.view_layer.objects.active = model
        bpy.context.object.animation_data_create()
        bpy.context.object.animation_data.action = bpy.data.actions.new("action1")
        nla_track = bpy.context.object.animation_data.nla_tracks.new()
        nla_track.name = "Track 2"

        # Get the end frame of "action"
        action_track = bpy.context.object.animation_data.nla_tracks[0]
        end_frame = int(action_track.strips[-1].frame_end)

        # Switch to pose mode
        bpy.ops.object.mode_set(mode='POSE')

        # Set the active bone to "root_bone_name"
        bone = bpy.context.object.pose.bones[bone_name]
        bpy.context.object.data.bones.active = bone.bone

        # Go to the second to last frame of "action"
        frame = int(end_frame) - 2
        bpy.context.scene.frame_set(frame)

        # Add "action1" to the new NLA track and set its start and end frames
        action_strip = nla_track.strips.new("action1", end_frame - 1, bpy.data.actions["action1"])
        action_strip.use_sync_length = True

        # Set the 3D cursor to the selected bone
        scene = bpy.context.scene
        scene.cursor.location = bone.location

        # Select the NLA track
        for track in bpy.context.object.animation_data.nla_tracks:
            track.select = False
            if track.name == "Track 2":
                track.select = True

        # Get the end frame of "action"
        action_track = bpy.context.object.animation_data.nla_tracks[0]
        end_frame = int(action_track.strips[-1].frame_end)

        # Save the frame where "action" ends
        action_end_frame = end_frame

        # Go to the first frame of "action1"
        bpy.context.scene.frame_set(end_frame)

        # Enter "Start Tweaking Strip Actions" mode
        bpy.ops.nla.tweakmode_enter()

        # Move one frame forward and set the bone location to the 3D cursor location
        bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)
        bone.location = scene.cursor.location

        # Add another keyframe
        bone.keyframe_insert(data_path='location', frame=bpy.context.scene.frame_current)

        # Get the end frame of "action"
        action_track1 = bpy.context.object.animation_data.nla_tracks[1]
        end_frame1 = int(action_track1.strips[-1].frame_end)

        # Switch to pose mode
        bpy.ops.object.mode_set(mode='POSE')

        # Set the active bone to "root_bone_name"
        bone = bpy.context.object.pose.bones[bone_name]
        bpy.context.object.data.bones.active = bone.bone

        # Check the Z-axis value of the keyframe one frame after the end of "action"
        frame = action_end_frame + 1
        bpy.context.scene.frame_set(frame)
        z_value = bone.location[2]

        # Check the X-axis value of the keyframe one frame after the end of "action"
        frame = action_end_frame + 1
        bpy.context.scene.frame_set(frame)
        x_value = bone.location[0]

        # Check the Y-axis value of the keyframe one frame after the end of "action"
        frame = action_end_frame + 1
        bpy.context.scene.frame_set(frame)
        y_value = bone.location[1]

        save_value = bone.location
        print(save_value)
        print(x_value)
        print(y_value)
        print(z_value)

        # Add the Z-axis value to the following keyframes
        for i in range(action_end_frame + 2, end_frame1 + 1):
            bpy.context.scene.frame_set(i)
            bone.location[0] += x_value
            bone.location[1] += y_value
            bone.location[2] += z_value
            print(bone.location[2])
            bone.keyframe_insert(data_path='location', index=2)

        # Set the extrapolation and blending values for each strip
        for strip in bpy.context.object.animation_data.nla_tracks:
            for sub_strip in strip.strips:
                sub_strip.blend_type = 'COMBINE'
                sub_strip.extrapolation = 'NOTHING'

        action_track2 = bpy.context.object.animation_data.nla_tracks[1]
        end_frame2 = int(action_track2.strips[-1].frame_end)
        bpy.context.scene.frame_end = end_frame2

        return {'FINISHED'}


def register():
    bpy.types.Scene.first_armature_name = bpy.props.StringProperty(name="First Armature name")
    bpy.types.Scene.second_armature_name = bpy.props.StringProperty(name="Second Armature name")
    bpy.types.Scene.root_bone_name = bpy.props.StringProperty(name="Root bone name")

    bpy.utils.register_class(MyPanel)
    bpy.utils.register_class(MyScriptOperator)


def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(MyScriptOperator)


if __name__ == "__main__":
    register()


