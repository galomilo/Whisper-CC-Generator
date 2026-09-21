import json
import subprocess
import os
import threading
from datetime import timedelta
from tkinter import *
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES


# ---------------- UTIL ----------------

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((seconds - total_seconds) * 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def dividir_segmento(segmento, palabras_por_linea):
    palabras = segmento["text"].strip().split()
    if not palabras:
        return []

    inicio = segmento["start"]
    fin = segmento["end"]
    duracion_total = fin - inicio
    duracion_por_palabra = duracion_total / len(palabras)

    bloques = []
    for i in range(0, len(palabras), palabras_por_linea):
        bloque_palabras = palabras[i:i + palabras_por_linea]
        bloque_inicio = inicio + (i * duracion_por_palabra)
        bloque_fin = bloque_inicio + (len(bloque_palabras) * duracion_por_palabra)

        bloques.append({
            "start": bloque_inicio,
            "end": bloque_fin,
            "text": " ".join(bloque_palabras)
        })

    return bloques


def generar_srt_desde_json(json_path, palabras_por_linea, output_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    contador = 1
    with open(output_path, "w", encoding="utf-8") as srt:
        for segmento in data["segments"]:
            bloques = dividir_segmento(segmento, palabras_por_linea)
            for bloque in bloques:
                srt.write(f"{contador}\n")
                srt.write(f"{format_timestamp(bloque['start'])} --> {format_timestamp(bloque['end'])}\n")
                srt.write(f"{bloque['text']}\n\n")
                contador += 1


# ---------------- UI ----------------

class WhisperApp:

    def __init__(self, root):
        self.root = root
        self.video_path = None
        self.loading = False
        self.loading_dots = 0

        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Variables
        self.dividir_var = BooleanVar()

        # ---------------- SETTINGS ----------------

        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(fill="x")

        self.model = ttk.Combobox(
            grid_frame,
            values=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        )
        self.model.set("base")

        self.language = ttk.Combobox(grid_frame, values=["auto", "es", "en", "fr", "de"])
        self.language.set("auto")

        self.output = ttk.Combobox(grid_frame, values=["txt", "srt", "json"])
        self.output.set("srt")
        self.output.bind("<<ComboboxSelected>>", self.toggle_division)

        self.temperature = ttk.Combobox(grid_frame, values=["0", "0.2", "0.5", "0.8", "1"])
        self.temperature.set("0")

        ttk.Label(grid_frame, text="Modelo").grid(row=0, column=0, sticky="w")
        self.model.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(grid_frame, text="Idioma").grid(row=0, column=1, sticky="w")
        self.language.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(grid_frame, text="Output").grid(row=2, column=0, sticky="w")
        self.output.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(grid_frame, text="Temperatura").grid(row=2, column=1, sticky="w")
        self.temperature.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # ---------------- OPCIONES AVANZADAS ----------------

        advanced_frame = ttk.LabelFrame(main_frame, text="Opciones avanzadas", padding=10)
        advanced_frame.pack(fill="x", pady=10)

        # max_line_width
        ttk.Label(advanced_frame, text="max_line_width").grid(row=0, column=0, sticky="w")
        self.max_line_width = ttk.Entry(advanced_frame, width=6)
        self.max_line_width.insert(0, "40")
        self.max_line_width.grid(row=0, column=1, padx=5)
        ttk.Label(
            advanced_frame,
            text="Máximo caracteres por línea en SRT"
        ).grid(row=0, column=2, sticky="w")

        # max_line_count
        ttk.Label(advanced_frame, text="max_line_count").grid(row=1, column=0, sticky="w")
        self.max_line_count = ttk.Entry(advanced_frame, width=6)
        self.max_line_count.insert(0, "2")
        self.max_line_count.grid(row=1, column=1, padx=5)
        ttk.Label(
            advanced_frame,
            text="Máximo líneas por subtítulo"
        ).grid(row=1, column=2, sticky="w")

        # word_timestamps
        self.word_timestamps_var = BooleanVar(value=True)
        self.word_timestamps_check = ttk.Checkbutton(
            advanced_frame,
            text="word_timestamps",
            variable=self.word_timestamps_var
        )
        self.word_timestamps_check.grid(row=2, column=0, sticky="w")

        ttk.Label(
            advanced_frame,
            text="Genera timestamps por palabra (más preciso)"
        ).grid(row=2, column=1, columnspan=2, sticky="w")

        # fp16
        self.fp16_var = BooleanVar(value=False)
        self.fp16_check = ttk.Checkbutton(
            advanced_frame,
            text="fp16",
            variable=self.fp16_var
        )
        self.fp16_check.grid(row=3, column=0, sticky="w")

        ttk.Label(
            advanced_frame,
            text="Usar precisión FP16 (más rápido en GPU)"
        ).grid(row=3, column=1, columnspan=2, sticky="w")

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # ---------------- DRAG & DROP ----------------

        drop_frame = ttk.Frame(main_frame, padding=20)
        drop_frame.pack(fill="x", pady=10)

        self.canvas = Canvas(drop_frame, height=120, bg="#f0f2f5", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(
            10, 10, 580, 110,
            outline="#3b82f6",
            width=2,
            dash=(6, 4)
        )

        self.canvas.create_text(
            300, 60,
            text="Arrastra el video aquí",
            font=("Segoe UI", 12),
            fill="#374151"
        )

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind("<<Drop>>", self.drop)

        # ---------------- STATUS ----------------

        self.video_status = ttk.Label(main_frame, text="✔ Video cargado: Ninguno")
        self.video_status.pack(anchor="w", pady=5)

        ttk.Separator(main_frame).pack(fill="x", pady=10)

        # ---------------- DIVISION ----------------

        self.division_frame = ttk.Frame(main_frame)
        self.division_frame.pack(fill="x", pady=10)

        self.check_dividir = ttk.Checkbutton(
            self.division_frame,
            text="Dividir por palabras",
            variable=self.dividir_var
        )
        self.check_dividir.pack(anchor="w")

        palabras_frame = ttk.Frame(self.division_frame)
        palabras_frame.pack(anchor="w")

        ttk.Label(palabras_frame, text="Palabras por línea:").pack(side="left")

        self.entry_palabras = ttk.Entry(palabras_frame, width=5)
        self.entry_palabras.pack(side="left", padx=5)

        # ---------------- PROCESS BUTTON ----------------

        self.process_button = ttk.Button(
            main_frame,
            text="Procesar",
            command=self.start_processing
        )
        self.process_button.pack(fill="x", pady=10)

        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack()

        # Ajustar visibilidad inicial
        self.toggle_division()

    # ---------------- FUNCIONES ----------------

    def toggle_division(self, event=None):
        if self.output.get() == "json":
            self.division_frame.pack(fill="x", pady=10)
        else:
            self.division_frame.pack_forget()

    def drop(self, event):
        self.video_path = event.data.strip("{}")
        self.video_status.config(text=f"✔ Video cargado: {os.path.basename(self.video_path)}")

    def animate_loading(self):
        if self.loading:
            dots = "." * self.loading_dots
            self.status_label.config(text=f"Cargando{dots}")
            self.loading_dots = (self.loading_dots + 1) % 4
            self.root.after(500, self.animate_loading)

    def start_processing(self):
        if not self.video_path:
            messagebox.showerror("Error", "Arrastrá un video primero.")
            return

        thread = threading.Thread(target=self.procesar)
        thread.start()

    def procesar(self):
        try:
            self.loading = True
            self.loading_dots = 0
            self.root.after(0, self.animate_loading)

            output_directory = os.path.dirname(self.video_path)
            base_name = os.path.splitext(os.path.basename(self.video_path))[0]

            cmd = [
                "whisper",
                self.video_path,
                "--model", self.model.get(),
                "--output_format", self.output.get(),
                "--temperature", self.temperature.get(),
                "--output_dir", output_directory
            ]

            # max_line_width
            if self.max_line_width.get().isdigit():
                cmd += ["--max_line_width", self.max_line_width.get()]

            # max_line_count
            if self.max_line_count.get().isdigit():
                cmd += ["--max_line_count", self.max_line_count.get()]

            # word_timestamps
            cmd += ["--word_timestamps", str(self.word_timestamps_var.get())]

            # fp16
            cmd += ["--fp16", str(self.fp16_var.get())]

            if self.language.get() != "auto":
                cmd += ["--language", self.language.get()]

            subprocess.run(cmd, check=True)

            json_path = os.path.join(output_directory, base_name + ".json")
            final_srt_path = os.path.join(output_directory, base_name + "_dividido.srt")

            if self.output.get() == "json" and self.dividir_var.get():

                palabras_text = self.entry_palabras.get()

                if not palabras_text.isdigit():
                    raise Exception("Ingresá un número válido de palabras por línea.")

                palabras = int(palabras_text)

                generar_srt_desde_json(json_path, palabras, final_srt_path)

                if os.path.exists(json_path):
                    os.remove(json_path)

            self.loading = False
            self.root.after(0, lambda: self.status_label.config(text="✅ Finalizado"))

        except Exception as e:
            self.loading = False
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))


# ---------------- MAIN ----------------

root = TkinterDnD.Tk()
root.title("Whisper Transcriber")
root.geometry("700x600")

app = WhisperApp(root)
root.mainloop()