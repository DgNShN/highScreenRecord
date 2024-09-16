import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import time

class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")

        # Initialize recording variables
        self.recording = False
        self.process = None
        self.recording_thread = None

        # GUI Elements
        tk.Label(root, text="Recording Duration (minutes):").pack(pady=10)
        self.duration_entry = tk.Entry(root)
        self.duration_entry.pack(pady=5)

        tk.Label(root, text="Save Location:").pack(pady=10)
        self.save_location_label = tk.Label(root, text="Not selected")
        self.save_location_label.pack(pady=5)
        self.select_save_location_button = tk.Button(root, text="Select Save Location", command=self.select_save_location)
        self.select_save_location_button.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=20)

        self.pause_button = tk.Button(root, text="Pause Recording", command=self.pause_recording, state=tk.DISABLED)
        self.pause_button.pack(pady=5)

        self.resume_button = tk.Button(root, text="Resume Recording", command=self.resume_recording, state=tk.DISABLED)
        self.resume_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

    def select_save_location(self):
        self.save_location = filedialog.asksaveasfilename(
            defaultextension=".mkv",
            filetypes=[("Matroska Video", "*.mkv")],
            title="Select Save Location"
        )
        if self.save_location:
            self.save_location_label.config(text=f"Save Location: {self.save_location}")
        else:
            messagebox.showwarning("Warning", "Save location not selected")

    def start_recording(self):
        if not self.recording:
            duration = self.duration_entry.get()
            try:
                duration = int(duration) * 60  # Convert minutes to seconds
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
                return

            if not hasattr(self, 'save_location') or not self.save_location:
                messagebox.showerror("Error", "Please select a save location")
                return

            self.recording = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start recording process
            self.process = subprocess.Popen([
                'ffmpeg', '-f', 'gdigrab', '-framerate', '60', '-i', 'desktop',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', self.save_location
            ])

            # Start a thread to stop recording after the specified duration
            self.recording_thread = threading.Thread(target=self.stop_after_duration, args=(duration,))
            self.recording_thread.start()

            messagebox.showinfo("Info", "Recording started")

    def stop_after_duration(self, duration):
        time.sleep(duration)
        if self.recording:
            self.stop_recording()

    def pause_recording(self):
        if self.recording and self.process:
            self.process.terminate()  # Terminate current process
            self.recording = False
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
            messagebox.showinfo("Info", "Recording paused")

    def resume_recording(self):
        if not self.recording:
            self.recording = True
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Restart recording process
            self.process = subprocess.Popen([
                'ffmpeg', '-f', 'gdigrab', '-framerate', '60', '-i', 'desktop',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', self.save_location
            ])
            messagebox.showinfo("Info", "Recording resumed")

    def stop_recording(self):
        if self.recording:
            self.process.terminate()  # Terminate current process
            self.recording = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showinfo("Info", "Recording stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.mainloop()
