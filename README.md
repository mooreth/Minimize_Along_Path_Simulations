# MAPS — Minimizations Along Path Simulations

**Atomistic simulation of slow mechanical systems using incremental energy minimization.**

MAPS (Minimizations Along Path Simulations) is a Python- and Blender-based workflow for investigating the mechanical behavior of atomically precise machines. It couples Blender-based molecular models and prescribed mechanical motion with LAMMPS energy minimization at successive configurations.

Rather than attempting to simulate slow machine motion directly with molecular dynamics (MD), MAPS advances the mechanism through a sequence of small, controlled displacements. At each increment, the structure is relaxed by energy minimization. This makes it possible to investigate quasi-static mechanical behavior on a sequence of atomistic configurations without integrating the physical time required for the corresponding slow motion.

The project is being developed for research in diamondoid machinery, molecular nanotechnology, and atomically precise manufacturing (APM).

## Overview

A MAPS simulation follows this general cycle:

1. **Design and configure the mechanism** in Blender using atomistic parts and machine components.
2. **Prescribe motion** by animating a Blender object (typically an Empty) that controls the driven component.
3. **Generate an atomistic input structure** for the current increment and write a LAMMPS data file.
4. **Minimize the structure** with LAMMPS using the selected interatomic potential and constraints.
5. **Read the minimized coordinates** and update the Blender model.
6. **Advance to the next increment** and repeat.

The motion of driven components is prescribed. Other components are free to respond to the atomistic forces and constraints. For example, in the rack-and-pinion test mechanism, the rack is driven while the pinion's rotation emerges from the mechanical interaction between the atomistic parts.

## Key Capabilities

- Blender-based construction and visualization of atomistic mechanisms.
- Keyframe-driven, incremental mechanical motion.
- LAMMPS energy minimization at each motion increment.
- Updating Blender atom coordinates from minimized LAMMPS structures.
- Local or remote minimization backends.
- Remote computation on a Linux workstation through SSH, with input transfer, remote execution, and result retrieval.
- LAMMPS data and trajectory output for inspection and post-processing.

## Simulation Approach

MAPS is a quasi-static or athermal minimization-based approach. Each increment consists of a prescribed change in configuration followed by energy minimization.

This approach is useful when the mechanical motion of interest is much slower than the timescales that can be directly explored by conventional molecular dynamics. It allows the researcher to study a sequence of relaxed atomistic configurations without treating the number of minimization steps as physical time.

MAPS does **not**, by itself, simulate physical-time dynamics. In particular, a basic minimization sequence does not capture inertial effects, thermal fluctuations, rate-dependent behavior, or dynamical transients. Those effects require additional methods and appropriately designed simulations.

## Architecture

The current workflow has four principal parts:

| Component | Responsibility |
|---|---|
| Blender | Atomistic model, machine geometry, prescribed motion, and visualization |
| MAPS Python controller | Keyframe processing, data-file generation, simulation sequencing, and coordinate updates |
| LAMMPS | Energy evaluation and structural minimization |
| Remote worker (optional) | Runs LAMMPS minimizations on a separate Linux workstation |

### Local computation

With the local backend selected, the MAPS controller invokes the local LAMMPS Python interface to minimize each generated structure.

### Remote computation

With remote computation enabled, the controller uses the `MAPSRemote` client to communicate with a remote Linux workstation over SSH:

1. MAPS writes the input LAMMPS data file on the Windows/Blender machine.
2. The controller uploads the input file to the remote MAPS directory.
3. `MAPS_worker.py` runs LAMMPS on the remote workstation.
4. The worker writes the minimized data file, trajectory, and log/diagnostic output.
5. The controller downloads the results.
6. MAPS updates the Blender model using the returned minimized coordinates.

The remote worker and its LAMMPS installation remain on the Linux workstation. Blender and the MAPS controller remain on the local machine.

## Requirements

The exact requirements depend on the selected backend and the molecular model.

- **Blender** with its bundled Python environment.
- **Python** modules used by the MAPS scripts, including `paramiko` for SSH-based remote execution.
- **LAMMPS** with the Python interface for local minimization.
- **LAMMPS** installed on the remote Linux workstation for remote minimization.
- The interatomic potential file required by the selected LAMMPS input configuration (the current test workflow uses AIREBO and `CH.airebo`).
- SSH access from the local machine to the remote workstation for remote computation.

For remote operation, the local Python environment must be able to import the remote-controller module, and SSH authentication must be configured for the remote account. The remote worker must be installed in the remote MAPS directory and configured to locate the appropriate LAMMPS library and potential files.

## Configuration

The MAPS controller selects the computation backend through its remote-connection setting. When remote computation is enabled, the controller uses the remote client; otherwise it uses the local LAMMPS implementation.

The remote configuration includes:

- Remote hostname or IP address.
- Remote username.
- Remote MAPS working directory.
- Remote worker script name.
- Local directory used for input and returned output files.

The remote worker also contains minimization settings, including force tolerance and maximum iteration/evaluation limits. These settings affect minimization behavior and should be selected for the system and desired accuracy.

Keep local and remote paths consistent with the actual directory layout on each machine. Do not assume that a path on Windows is valid on Linux, or vice versa.

## Input and Output Files

The MAPS workflow uses LAMMPS data files as the handoff format between Blender and LAMMPS.

Typical per-increment files include:

- `b4min_at_frame_N.data` — atomistic structure exported before minimization.
- `minimized_at_frame_N.data` — structure after minimization.
- `minimized_at_frame_N.lammpstrj` — minimized-coordinate trajectory output.
- `MAPS_frame_N.log` — remote worker log and minimization diagnostics.

Here, `N` is the MAPS frame number. File names and output locations are determined by the current controller and worker configuration.

Trajectory files from successive increments can be combined for visualization or analysis. Ensure that the input files belong to the current run before combining them; stale output from an earlier run can otherwise be mistaken for current simulation data.

## Current Demonstration

The rack-and-pinion mechanism is the current proof-of-concept system.

- The rack's translation is prescribed through Blender keyframes.
- The pinion is not assigned a prescribed rotation; its response arises from the atomistic interaction with the rack.
- The model used in the remote-computation test contains approximately 3,110 atoms.
- The remote workflow successfully transferred input structures to a Linux workstation, ran LAMMPS minimizations, returned minimized structures and trajectories, and updated the Blender model.

This is a working demonstration of the MAPS workflow, not a claim that every mechanism, potential, or simulation regime has been validated.

## Important Scientific and Technical Considerations

- **Minimization convergence:** A worker completing successfully does not necessarily mean that the requested force tolerance was reached. Check the reported stopping criterion, maximum force, force norm, and energy.
- **Potential validity:** The interatomic potential must be appropriate for the elements, bonding, and configurations being simulated. The current AIREBO setup is not a universal potential for arbitrary molecular systems.
- **Constraints:** Fixed and driven groups must be defined consistently with the intended mechanism and the LAMMPS input configuration.
- **Increment size:** Prescribed motion should be divided into sufficiently small increments to avoid invalid configurations or missing important mechanical transitions.
- **Atom identity:** Coordinate updates depend on preserving the correspondence between LAMMPS atom IDs/types and the Blender atom objects.
- **Quasi-static interpretation:** The sequence of minimized configurations is not a physical-time trajectory.

## Development Roadmap

Potential areas for further development include:

- More robust minimization-convergence reporting and handling.
- Adaptive motion increments based on structural response and minimization behavior.
- Improved trajectory analysis and mechanism-motion measurements.
- Faster bulk updates of atom coordinates in Blender.
- More scalable atomistic visualization and representation.
- Expanded examples covering additional atomistic mechanisms and machine components.
- More general remote execution configuration and job management.

## Attribution

**Tom Moore — Project creator and lead developer**

**ChatGPT (OpenAI, GPT-6) — AI development assistant**

MAPS is a collaborative development effort. Tom Moore defines the research goals, project direction, system architecture, simulation requirements, and experimental validation, and directs development and testing of the software. ChatGPT has assisted with software design, code generation, implementation, refactoring, debugging, technical analysis, and documentation.

The project’s scientific direction, research objectives, modeling decisions, and interpretation of results remain the responsibility of the project creator.

For additional information about the AI-assisted development process, see [`AI_ASSISTANCE.md`](AI_ASSISTANCE.md), if included in the repository.

## License

MAPS is released under the [MIT License](LICENSE).

Copyright (c) 2026 Tom Moore
