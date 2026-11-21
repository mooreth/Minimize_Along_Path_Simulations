import bpy
import os
import math
import mathutils

import sys
import os


sys.path.insert(0, r"C:\MAPS")

from MAPS_remote_updated import MAPSRemote


# --------------------------------------------------
# MAPS configuration
# --------------------------------------------------

remote_connection = True

MAPS_DIR = r"C:\MAPS"

remote = None

def add_atom(atom_index,  atom_type,  x_cor, y_cor, z_cor):   
    if atom_type in ("1", "3", "5"):
        atom_radius = 0.9
        atom_prefix = "C_atom"

    elif atom_type in ("2", "4", "6"):
        atom_radius = 0.5
        atom_prefix = "H_atom"

    else:
        print(f"WARNING: Unknown atom type '{atom_type}' "
              f"for atom {atom_index}")
        return
   
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=atom_radius, location=(float(x_cor), float(y_cor), float(z_cor)), rotation=(0.0, 0.0, 0.0))
    for obj in bpy.context.selected_objects:
        obj.name = atom_prefix + "_" + atom_index + "_"+ atom_type
        if "C" in obj.name:
            mat = bpy.data.materials.get('carbon')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "Ge" in obj.name:
            mat = bpy.data.materials.get('germanium')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "H" in obj.name:
            mat = bpy.data.materials.get('hydrogen')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "O" in obj.name:
            mat = bpy.data.materials.get('oxygen')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "Si" in obj.name:
            mat = bpy.data.materials.get('silicon')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "B" in obj.name:
            mat = bpy.data.materials.get('boron')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "N" in obj.name:
            mat = bpy.data.materials.get('nitrogen')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat 
        elif "F" in obj.name:
            mat = bpy.data.materials.get('flourine')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat 
        elif "P" in obj.name:
            mat = bpy.data.materials.get('phosphorus')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "S" in obj.name:
            mat = bpy.data.materials.get('sulfur')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "I" in obj.name:
            mat = bpy.data.materials.get('iodine')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        elif "Au" in obj.name:
            mat = bpy.data.materials.get('gold')
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat        

def load_datafile(name):
    out_dir='C:/MAPS/' 
    datafile=os.path.join(out_dir,name)
    
    with open(datafile , 'r') as file:
                igot = file.readlines()
                for atom_line_num, line in enumerate(igot, 1):
                    atom_info = line.split()
                    if len(atom_info) == 6:
                        
                        atom_index = atom_info[0]
                        part_num = atom_info[1]
                        atom_type = atom_info[2]
                        x_cor = atom_info[3]
                        y_cor = atom_info[4]
                        z_cor = atom_info[5]
                        add_atom(atom_index,  atom_type,  x_cor, y_cor, z_cor)
 
def Parent2Empty(part_collection, empty_name):
    #this could be updated for mutiple parts where for each collection, get the collection name, create the empty, and parent those there
    
    x_cordinate_sum = 0
    y_cordinate_sum = 0
    z_cordinate_sum = 0
    number_atoms = 0

    for obj in bpy.data.collections[part_collection].all_objects:
        obj.select_set(True)
        string_obj = str(obj)

        if "atom" in string_obj: 
            #print(string_obj)
            coords = obj.location

            x_cordinate = coords[0]
            x_cordinate_sum = x_cordinate_sum + x_cordinate
           
            y_cordinate = coords[1]
            y_cordinate_sum = y_cordinate_sum + y_cordinate  
            
            z_cordinate = coords[2]
            z_cordinate_sum = z_cordinate_sum + z_cordinate         
            
            number_atoms = number_atoms + 1

    X_mean = x_cordinate_sum/number_atoms
    Y_mean = y_cordinate_sum/number_atoms
    Z_mean = z_cordinate_sum/number_atoms
    
    #print(X_mean, Y_mean, Z_mean)
    
    bpy.ops.object.empty_add(location=(X_mean,Y_mean,Z_mean))
    
    empty = bpy.context.object
    
    ###############

    for obj in bpy.data.collections[part_collection].all_objects:   
        string_obj = str(obj)

        if "Empty" not in string_obj and "atom" in string_obj:    
            
            obj.select_set(True)
            obj.parent = empty
            # After both parent and child have been link()ed to the scene reset the child offset
            obj.parent = empty
            obj.matrix_parent_inverse = empty.matrix_world.inverted()  
            print(obj.name)

    empty.name = empty_name+"_Empty"
    print("created", empty.name)
    

def get_empty_keyframes(empty_name):   
        keyframes = []
        target_object = bpy.data.objects.get(empty_name)
        
        anim = target_object.animation_data
        if anim is not None and anim.action is not None:
            for fcu in anim.action.fcurves:
                for keyframe in fcu.keyframe_points:
                    x, y = keyframe.co
                    if x not in keyframes:
                        keyframes.append((math.ceil(x)))
        return keyframes

def write_data_file(part_num, frame):

    out_dir = "C:/MAPS/"
    data_file_name = "b4min_at_frame_" + str(frame) + ".data"
    data_file_locname = os.path.join(out_dir, data_file_name)

    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()

    # Masses for the six LAMMPS atom types
    atom_masses = {
        1: 12.0109997,
        2: 1.00796998,
        3: 12.0109997,
        4: 1.00796998,
        5: 12.0109997,
        6: 1.00796998
    }

    atom_records = []
    atom_types_found = set()

    Xs = []
    Ys = []
    Zs = []

    # -------------------------------------------------
    # Stage 1: Collect atom records and coordinates
    # -------------------------------------------------

    for obj in bpy.data.objects:

        if "atom" not in obj.name.lower():
            continue

        # Remove Blender duplicate-name suffix (.001, .002, etc.)
        clean_name = obj.name.rsplit(".", 1)[0] if (
            obj.name.rsplit(".", 1)[-1].isdigit()
        ) else obj.name

        # Parse object name: C_atom_541_1
        atom_name = clean_name.split("_")

        if len(atom_name) < 4:
            print("WARNING: Unexpected atom name:", obj.name)
            continue

        element = atom_name[0]
        atom_index = int(atom_name[2])
        atom_type = int(atom_name[3])

        if atom_type not in atom_masses:
            raise ValueError(
                f"Unknown LAMMPS atom type {atom_type}: {obj.name}"
            )

        # Check that the element agrees with the atom type
        expected_element = "C" if atom_type in (1, 3, 5) else "H"

        if element != expected_element:
            raise ValueError(
                f"Element mismatch in {obj.name}: "
                f"expected {expected_element}, found {element}"
            )

        atom_types_found.add(atom_type)

        # Get world coordinates
        world_location = obj.matrix_world.translation

        x = world_location.x
        y = world_location.y
        z = world_location.z

        Xs.append(x)
        Ys.append(y)
        Zs.append(z)

        # Store LAMMPS molecular atom record
        atom_records.append(
            f"{atom_index} {part_num} {atom_type} "
            f"{x:.6f} {y:.6f} {z:.6f}\n"
        )

    atom_count = len(atom_records)

    if atom_count == 0:
        raise ValueError("No Blender atom objects found!")

    print("Number of atoms found:", atom_count)
    print("Atom types found:", sorted(atom_types_found))

    # -------------------------------------------------
    # Stage 2: Calculate simulation box boundaries
    # -------------------------------------------------

    padding = 5.0

    X_low_pad = math.floor(min(Xs) - padding)
    X_high_pad = math.ceil(max(Xs) + padding)

    Y_low_pad = math.floor(min(Ys) - padding)
    Y_high_pad = math.ceil(max(Ys) + padding)

    Z_low_pad = math.floor(min(Zs) - padding)
    Z_high_pad = math.ceil(max(Zs) + padding)

    print("LAMMPS simulation box:")
    print(f"X: {X_low_pad} to {X_high_pad}")
    print(f"Y: {Y_low_pad} to {Y_high_pad}")
    print(f"Z: {Z_low_pad} to {Z_high_pad}")

    # LAMMPS requires the atom type count to accommodate
    # the largest atom type ID, even if some types are absent.
    max_atom_type = max(atom_types_found)

    # -------------------------------------------------
    # Stage 3: Write final LAMMPS data file
    # -------------------------------------------------

    with open(data_file_locname, "w") as f:

        f.write(data_file_name + "\n\n")

        f.write(f"{atom_count} atoms\n")
        f.write(f"{max_atom_type} atom types\n\n")

        f.write(f"{X_low_pad} {X_high_pad} xlo xhi\n")
        f.write(f"{Y_low_pad} {Y_high_pad} ylo yhi\n")
        f.write(f"{Z_low_pad} {Z_high_pad} zlo zhi\n\n")

        # Masses section
        f.write("Masses\n\n")

        for atom_type in range(1, max_atom_type + 1):
            f.write(
                f"{atom_type} {atom_masses[atom_type]:.8f}\n"
            )

        # Atoms section
        f.write("\nAtoms # molecular\n\n")

        for record in atom_records:
            f.write(record)

    print("LAMMPS data file written:", data_file_locname)
    print("Number of atom records written:", len(atom_records))

    

def run_min_local(frame2min):
    import lammps
    # 1. Initialize the LAMMPS instance
    # Use "serial" or "mpi" depending on how you want to run (e.g., mpirun -np 4 python script.py)
    lmp = lammps.lammps()
    
    # 2. Setup the simulation 
    lmp.commands_string("""
    units metal
    atom_style molecular
    boundary s s s    #non-periodic
    """)
    lmp.command("log C:/Users/moore/OneDrive/Desktop/maps_lammps.log")
    # System definition
 
    print("running minimzation on", "b4min_at_frame_" + str(frame2min)+ ".data")
    read_data_cmd = "read_data C:\MAPS/b4min_at_frame_" + str(frame2min)+ ".data" 
    
    lmp.command(read_data_cmd) 
    
    # set groups
    lmp.command("group lonsfree type 1 2")
    lmp.command("group anchor type 3 4")
    lmp.command("group transz type 5 6")
    
    # Pair Coefficients
    lmp.command("pair_style	airebo 3.0 1 0")# run 1 cutoff 3.0
    #lmp.command("pair_style	airebo 1.0 1 0")# run 1 cutoff 1.0
    #lmp.command("pair_style	airebo 0.25 1 0")# run 1 cutoff .025
    lmp.command("pair_coeff * * CH.airebo C H C H C H ")
    
    
    ## 3. Specify the minimization style
    ## Conjugate gradient (cg) is often more efficient than steepest descent (sd)
    lmp.command("min_style cg")
    
    # Keep anchor atoms fixed during minimization
    lmp.command("fix anchorbase anchor setforce 0.0 0.0 0.0") 
    
    ## 4. Run the energy minimization
    print("Running energy minimization...")
    
    # Output diagnostics
    lmp.command("thermo 10")
    lmp.command("thermo_style custom step pe fmax fnorm")
    
    # Minimize until force tolerance is reachedchatGPTThis
    lmp.command("minimize 0.0 1.0e-3 2000 2000")
    
    ### The 'minimize' command parameters are:
    ### etol (energy tolerance), ftol (force tolerance), maxiter (max iterations), maxeval (max force evaluations)
    #lmp.command("minimize 1.0e-4 1.0e-6 1000 1000")
    
    ## 5. Retrieve results and clean up
    
    fmax_min = lmp.get_thermo("fmax") # Get max force component
    
    
    print(f"Minimization finished.")
    
    print(f"Max Force Component (fmax) = {fmax_min:.4e}")
    
    ## Optional: Output minimized structure to a dump file
    
    write_trjcmd = "write_dump all custom C:/MAPS/minimized_at_frame_" + str(frame2min)+".lammpstrj id type x y z"
    lmp.command(write_trjcmd) 
    
    write_datacmd = "write_data C:/MAPS/minimized_at_frame_"+ str(frame2min)+".data"
    lmp.command(write_datacmd)  
    
    
    # Close the LAMMPS instance
    lmp.close()    
    lmp.finalize()
    
def run_min(frame2min): #this runs on a remote machine

    input_file = os.path.join(
        MAPS_DIR,
        f"b4min_at_frame_{frame2min}.data"
    )

    if remote_connection:

        print(f"MAPS: Running frame {frame2min} remotely")

        result = remote.run_remote_maps_step(
            local_input_file=input_file,
            frame_number=frame2min,
            local_output_dir=MAPS_DIR
        )

        diagnostics = result["diagnostics"]

        print("Remote minimization complete.")
        print("PE:", diagnostics.get("PE"))
        print("FMAX:", diagnostics.get("FMAX"))
        print("FNORM:", diagnostics.get("FNORM"))

        return result

    else:

        print(f"MAPS: Running frame {frame2min} locally")

        return run_min_local(frame2min)

def update_system(frame):
    C_atom_types = []
    H_atom_types = []
    out_dir="C:/MAPS/"
    data_file_2use = "minimized_at_frame_" + str(frame)+ ".data"
    print("updating atom positions with data from ", "minimized_at_frame_" + str(frame)+ ".data")
    datafile= os.path.join(out_dir,data_file_2use)
    
    with open(datafile , 'r') as file:
                igot = file.readlines()
                for line in igot:
                    #lets make a list of the C and H atom types
                    if line.find("12.0109997") > -1:
                        line.split()
                        C_atom_types.append(line[0])
                    if line.find("1.00796998") > -1:
                        line.split()
                        H_atom_types.append(line[0])                        
                    
                    
                    atom_info = line.split()  
                    if len(atom_info) == 9:
                        atom_index = atom_info[0]
                        part_num = atom_info[1]
                        atom_type = atom_info[2]
                        x_cor = atom_info[3]
                        y_cor = atom_info[4]
                        z_cor = atom_info[5]
                    
                        #build the atom's blender name
                        if atom_type in C_atom_types:
                            element = "C"
                        else:
                            element = "H"
                        atom_name = element + "_atom_"+ atom_index +"_" +atom_type
                        #print(atom_name)
                        atom_to_move = obj = bpy.data.objects[atom_name]
                        location = float(x_cor ), float(y_cor ), float(z_cor )                        
                        atom_to_move.matrix_world.translation = mathutils.Vector(location)
                        
                        
                        
    ###key frame objects
    for obj in bpy.data.objects:
        if "_atom" in obj.name:
            obj.select_set(True)
            for obj in bpy.context.selected_objects:
                # Keyframe Location
                obj.keyframe_insert(data_path="location", frame=frame)
                # Keyframe Rotation (using rotation_euler for XYZ Euler angles)
                obj.keyframe_insert(data_path="rotation_euler", frame=frame)            
        
    
    print("C and H atom types", C_atom_types, H_atom_types)                
                        
    
def combine_trjs():
    pass


def Update3DViewPorts():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()



#Step 1
###Initial loading of the system
#load_datafile("MAPS_rack.data")

##Step 2
####parent moving objects
#print("adding empty")
#Parent2Empty("rack","rack") #if these don't match the collection, no empty is created and the atoms are duplicated

#write_data_file(1, 12) #part_num and frame number
#write out the current positions
#write_data_file(1, frame)

#run_min()

#update_system(12)

#write_data_file(1,7) #this writes the positions of the atoms at keyframe 7

#Keyframes are analogous to waypoints in the path. The number of frames between
#keyframes will determine the frequency of minimizations. Or think of the trajectory
#between keyframes to be a single leg of the journey

# --------------------------------------------------
# MAPS simulation
# --------------------------------------------------

part_num = 1
keys = get_empty_keyframes("rack_Empty")

print("Keyframes:", keys)

if len(keys) < 2:
    raise ValueError("At least two keyframes are required.")

legs = len(keys) - 1

# Establish remote connection once
if remote_connection:
    remote = MAPSRemote()
    remote.connect()

try:

    starting_key_index = 0
    next_key_index = 1

    for leg in range(1, legs + 1):

        print("Leg", leg)

        for frame2min in range(
            keys[starting_key_index],
            keys[next_key_index]
        ):

            print("Minimizing frame", frame2min)

            bpy.context.scene.frame_set(frame2min)

            # Write current Blender coordinates
            write_data_file(part_num, frame2min)

            # Run local or remote minimization
            run_min(frame2min)

            # Update Blender with minimized coordinates
            update_system(frame2min)

        starting_key_index += 1
        next_key_index += 1

    # Process final keyframe
    print("Minimizing last frame", keys[-1])

    write_data_file(part_num, keys[-1])

    run_min(keys[-1])

    update_system(keys[-1])

finally:

    # Disconnect once after the entire simulation
    if remote is not None:
        remote.disconnect()

print("MAPS simulation complete.")



