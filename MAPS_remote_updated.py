import shlex
from pathlib import Path
import paramiko


class MAPSRemote:

    def __init__(
        self,
        host="192.168.68.86",
        username="tom",
        remote_directory="~/Desktop/MAPS",
        worker_filename="MAPS_worker.py",
    ):
        self.host = host
        self.username = username
        self.remote_directory = remote_directory
        self.worker_filename = worker_filename
        self.ssh = None
        self.sftp = None

    def connect(self):
        print(f"Connecting to {self.host}...")

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(
            hostname=self.host,
            username=self.username,
            look_for_keys=True,
            allow_agent=True,
            timeout=10
        )

        self.sftp = self.ssh.open_sftp()

        home = self.sftp.normalize(".")
        self.remote_directory = home + "/Desktop/MAPS"

        stdin, stdout, stderr = self.ssh.exec_command(
            f"mkdir -p {shlex.quote(self.remote_directory)}"
        )
        exit_code = stdout.channel.recv_exit_status()

        if exit_code != 0:
            error = stderr.read().decode(errors="replace")
            raise RuntimeError(
                f"Could not create remote MAPS directory: {error}"
            )

        print("Connected to Atlantis.")
        print(f"Remote directory: {self.remote_directory}")

    def execute(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        output = stdout.read().decode(errors="replace")
        error = stderr.read().decode(errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, output, error

    def upload_file(self, local_file, remote_filename=None):
        local_file = Path(local_file)

        if not local_file.is_file():
            raise FileNotFoundError(f"Local file not found: {local_file}")

        if remote_filename is None:
            remote_filename = local_file.name

        remote_path = self.remote_directory + "/" + remote_filename

        print(f"Uploading {local_file.name}...")
        self.sftp.put(str(local_file), remote_path)
        print("Upload complete.")
        return remote_path

    def download_file(self, remote_filename, local_file):
        remote_path = self.remote_directory + "/" + remote_filename
        local_file = Path(local_file)
        local_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {remote_filename}...")
        self.sftp.get(remote_path, str(local_file))
        print("Download complete.")
        return str(local_file)

    def run_remote_maps_step(
        self,
        local_input_file,
        frame_number,
        local_output_dir=None,
    ):
        """
        Upload one MAPS input frame, run MAPS_worker.py on Atlantis,
        and download the minimized data and trajectory files.

        Returns a dictionary containing output paths and diagnostics.
        """
        if self.ssh is None or self.sftp is None:
            raise RuntimeError("Not connected. Call connect() first.")

        local_input_file = Path(local_input_file)
        if not local_input_file.is_file():
            raise FileNotFoundError(
                f"MAPS input file not found: {local_input_file}"
            )

        if local_output_dir is None:
            local_output_dir = local_input_file.parent

        local_output_dir = Path(local_output_dir)
        local_output_dir.mkdir(parents=True, exist_ok=True)
        frame_number = int(frame_number)

        remote_input_name = f"b4min_at_frame_{frame_number}.data"
        remote_input_path = self.upload_file(
            local_input_file, remote_input_name
        )

        worker_path = (
            self.remote_directory + "/" + self.worker_filename
        )

        command = (
            f"cd {shlex.quote(self.remote_directory)} && "
            "export LD_LIBRARY_PATH=/home/tom/.local/lib:$LD_LIBRARY_PATH && "
            f"python3 {shlex.quote(worker_path)} "
            f"{frame_number} {shlex.quote(remote_input_path)}"
        )

        print(
            f"Running remote MAPS minimization for frame {frame_number}..."
        )
        exit_code, output, error = self.execute(command)

        print(output, end="")
        if error:
            print("REMOTE STDERR:")
            print(error)

        if exit_code != 0:
            raise RuntimeError(
                f"Remote MAPS worker failed for frame {frame_number} "
                f"(exit code {exit_code}).\n"
                f"STDOUT:\n{output}\nSTDERR:\n{error}"
            )

        if "MAPS_STATUS=SUCCESS" not in output:
            raise RuntimeError(
                "Worker exited without MAPS_STATUS=SUCCESS.\n"
                f"STDOUT:\n{output}\nSTDERR:\n{error}"
            )

        data_name = f"minimized_at_frame_{frame_number}.data"
        trj_name = f"minimized_at_frame_{frame_number}.lammpstrj"

        local_data = local_output_dir / data_name
        local_trj = local_output_dir / trj_name

        self.download_file(data_name, local_data)
        self.download_file(trj_name, local_trj)

        diagnostic_keys = (
            "MAPS_FRAME",
            "PE",
            "FMAX",
            "FNORM",
            "FORCE_TOL",
            "MAX_ITER",
            "MAX_EVAL",
            "OUTPUT_DATA",
            "OUTPUT_TRAJ",
            "MAPS_STATUS",
        )
        
        diagnostics = {}
        
        for line in output.splitlines():
            for key in diagnostic_keys:
                if line.startswith(key + "="):
                    diagnostics[key] = line.split("=", 1)[1].strip()
                    break

        result = {
            "frame": frame_number,
            "data_file": str(local_data),
            "trajectory_file": str(local_trj),
            "diagnostics": diagnostics,
            "stdout": output,
            "stderr": error,
            "exit_code": exit_code,
        }

        print(f"MAPS frame {frame_number} returned to local machine.")
        return result

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
            self.sftp = None

        if self.ssh:
            self.ssh.close()
            self.ssh = None

        print("Disconnected from Atlantis.")

        
if __name__ == "__main__":

    remote = MAPSRemote()

    try:
        remote.connect()

        result = remote.run_remote_maps_step(
            local_input_file=r"C:\MAPS\b4min_at_frame_1.data",
            frame_number=1,
            local_output_dir=r"C:\MAPS"
        )

        print("\nMAPS RESULTS")
        print("------------------------------")
        print("Data file:", result["data_file"])
        print("Trajectory:", result["trajectory_file"])
        print("Diagnostics:", result["diagnostics"])

    except Exception as e:
        print("\nMAPS REMOTE ERROR:")
        print(e)

    finally:
        remote.disconnect()

