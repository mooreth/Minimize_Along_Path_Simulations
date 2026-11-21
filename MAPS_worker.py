
#!/usr/bin/env python3

import sys
from pathlib import Path
from lammps import lammps


# --------------------------------------------------
# MAPS configuration
# --------------------------------------------------

MAPS_DIR = Path("/home/tom/Desktop/MAPS")
POTENTIAL = MAPS_DIR / "CH.airebo"

# Minimization settings
FORCE_TOL = 1.0e-3

# Development settings
MAX_ITER = 500
MAX_EVAL = 500

# Production settings:
# MAX_ITER = 2000
# MAX_EVAL = 2000


# --------------------------------------------------
# LAMMPS minimization
# --------------------------------------------------

def run_minimization(input_file, frame_number):

    input_file = Path(input_file).resolve()

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input data file not found: {input_file}"
        )

    if not POTENTIAL.exists():
        raise FileNotFoundError(
            f"AIREBO potential not found: {POTENTIAL}"
        )

    log_file = MAPS_DIR / f"MAPS_frame_{frame_number}.log"
    output_data = MAPS_DIR / f"minimized_at_frame_{frame_number}.data"
    output_trj = MAPS_DIR / f"minimized_at_frame_{frame_number}.lammpstrj"

    lmp = None

    try:

        print(f"MAPS: Starting frame {frame_number}")
        print(f"MAPS: Input file: {input_file}")
        print(f"MAPS: Max iterations: {MAX_ITER}")
        print(f"MAPS: Max evaluations: {MAX_EVAL}")

        lmp = lammps()

        # Initialize system
        lmp.commands_string("""
units metal
atom_style molecular
boundary s s s
""")

        lmp.command(f"log {log_file}")
        lmp.command(f"read_data {input_file}")

        # Atom groups
        lmp.command("group lonsfree type 1 2")
        lmp.command("group anchor type 3 4")
        lmp.command("group transz type 5 6")

        # AIREBO potential
        lmp.command("pair_style airebo 3.0 1 0")
        lmp.command(
            f"pair_coeff * * {POTENTIAL} C H C H C H"
        )

        # Minimization
        lmp.command("min_style cg")

        lmp.command(
            "fix anchorbase anchor setforce 0.0 0.0 0.0"
        )

        lmp.command("thermo 10")
        lmp.command(
            "thermo_style custom step pe fmax fnorm"
        )

        minimize_command = (
            f"minimize 0.0 {FORCE_TOL} "
            f"{MAX_ITER} {MAX_EVAL}"
        )

        lmp.command(minimize_command)

        # Final diagnostics
        pe = lmp.get_thermo("pe")
        fmax = lmp.get_thermo("fmax")
        fnorm = lmp.get_thermo("fnorm")

        # Write minimized structure
        lmp.command(
            f"write_dump all custom {output_trj} id type x y z"
        )

        lmp.command(f"write_data {output_data}")

        # Verify outputs
        if not output_data.exists():
            raise RuntimeError("LAMMPS did not create output data file")

        if not output_trj.exists():
            raise RuntimeError("LAMMPS did not create trajectory file")

        # Report results
        print(f"MAPS_FRAME={frame_number}")
        print(f"PE={pe}")
        print(f"FMAX={fmax}")
        print(f"FNORM={fnorm}")
        print(f"FORCE_TOL={FORCE_TOL}")
        print(f"MAX_ITER={MAX_ITER}")
        print(f"MAX_EVAL={MAX_EVAL}")
        print(f"OUTPUT_DATA={output_data}")
        print(f"OUTPUT_TRAJ={output_trj}")
        print("MAPS_STATUS=SUCCESS")

    finally:

        if lmp is not None:
            lmp.close()


# --------------------------------------------------
# Command-line entry point
# --------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage: python3 MAPS_worker.py "
            "<frame_number> <input_data_file>",
            file=sys.stderr
        )
        sys.exit(1)

    frame = int(sys.argv[1])
    input_path = sys.argv[2]

    try:

        run_minimization(input_path, frame)

    except Exception as exc:

        print(
            f"MAPS_WORKER_ERROR: {exc}",
            file=sys.stderr
        )

        sys.exit(1)
