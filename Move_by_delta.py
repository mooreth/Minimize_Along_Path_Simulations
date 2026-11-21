import math
import bpy
from mathutils import Vector


def generate_linear_keyframes(
        object_name,
        start_frame,
        end_frame,
        start_location=None,
        end_location=None,
        max_delta=1.7
    ):

    obj = bpy.data.objects.get(object_name)

    if obj is None:
        raise ValueError(f"Object '{object_name}' not found.")

    if end_frame <= start_frame:
        raise ValueError("End frame must be greater than start frame.")

    if max_delta <= 0:
        raise ValueError("max_delta must be positive.")

    # Get endpoint locations.
    if start_location is None:
        bpy.context.scene.frame_set(start_frame)
        start_location = obj.location.copy()
    else:
        start_location = Vector(start_location)

    if end_location is None:
        bpy.context.scene.frame_set(end_frame)
        end_location = obj.location.copy()
    else:
        end_location = Vector(end_location)

    total_delta = end_location - start_location
    total_distance = total_delta.length

    # Calculate number of increments needed.
    increments = max(1, math.ceil(total_distance / max_delta))

    # Calculate actual displacement per increment.
    delta_per_step = total_delta / increments

    print(f"\nMAPS keyframe generation: {object_name}")
    print(f"Total displacement: {total_distance:.4f} Å")
    print(f"Maximum displacement: {max_delta:.4f} Å")
    print(f"Number of increments: {increments}")
    print(f"Actual displacement per increment: {delta_per_step.length:.4f} Å")

    # Generate evenly spaced keyframes.
    for i in range(increments + 1):

        frame = round(
            start_frame + (end_frame - start_frame) * i / increments
        )

        location = start_location + delta_per_step * i

        obj.location = location
        obj.keyframe_insert(
            data_path="location",
            frame=frame,
            group="MAPS Rack Motion"
        )

        print(f"Frame {frame}: {location}")

    print("Keyframe generation complete.")

generate_linear_keyframes(
    object_name="rack_Empty",
    start_frame=1,
    end_frame=20,
    max_delta=.85
    )