
from pathlib import Path


def combine_maps_trajectories(
        first_frame,
        last_frame,
        directory,
        output_file
    ):

    directory = Path(directory)
    output_path = directory / output_file

    combined_count = 0
    missing_frames = []

    with open(output_path, "w") as outfile:

        for frame in range(first_frame, last_frame + 1):

            filename = f"minimized_at_frame_{frame}.lammpstrj"
            filepath = directory / filename

            if not filepath.exists():
                print(f"WARNING: Missing {filename}")
                missing_frames.append(frame)
                continue

            print(f"Adding frame {frame}: {filename}")

            with open(filepath, "r") as infile:
                contents = infile.read()

            outfile.write(contents)

            if contents and not contents.endswith("\n"):
                outfile.write("\n")

            combined_count += 1

    print("\nTrajectory combination complete.")
    print(f"Frames combined: {combined_count}")
    print(f"Output file: {output_path}")

    if missing_frames:
        print(f"Missing frames: {missing_frames}")

    return str(output_path)


combine_maps_trajectories(
    1,
    20,
    r"C:\MAPS",
    "output_rack_pinion_run1.lammpstrj"
)