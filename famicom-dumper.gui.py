import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os  # Importar módulo para manejar archivos y directorios

# Función para seleccionar un archivo
def select_file():
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo ROM",
        filetypes=[("Archivos NES", "*.nes"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
        update_generated_command()  # Actualizar el comando al seleccionar una ROM

# Función para actualizar el comando generado
def update_generated_command(mapper_option=None, submapper_option=None):
    # Obtener el comando actual del campo de texto
    current_command = generated_command_text.get().split()

    selected_command = command_var.get()
    file_path = file_entry.get() or "nikita.nes"  # Usar "nikita.nes" como valor por defecto si no hay ROM seleccionada

    # Construir el comando base
    command = [
        ".\\famicom-dumper.exe",
        selected_command  # Usar el comando seleccionado
    ]

    # Agregar mapper o submapper, pero no ambos
    if mapper_option:
        command.append(mapper_option)  # Agregar el mapper seleccionado
    elif submapper_option or "--coolboy-submapper" in current_command:
        # Mantener el submapper actual o agregar el nuevo
        submapper_value = submapper_option or current_command[current_command.index("--coolboy-submapper") + 1]
        command.extend(["--coolboy-submapper", submapper_value])

    # Agregar opciones adicionales seleccionadas
    additional_options = [opt for opt in current_command if opt in additional_options_list]
    command.extend(additional_options)

    # Agregar --file al final del comando
    if "--file" in current_command:
        # Reemplazar el valor de --file con la nueva ROM seleccionada, entre comillas si contiene espacios
        command.extend(["--file", f' "{file_path}"' if " " in file_path else f' {file_path}'])
    else:
        # Agregar --file si no está presente, con la ROM seleccionada entre comillas si contiene espacios
        command.extend(["--file", f' "{file_path}"' if " " in file_path else f' {file_path}'])

    # Mostrar el comando generado en el campo de texto
    generated_command_text.delete(0, tk.END)
    generated_command_text.insert(0, " ".join(command))

# Función para restablecer el comando al valor por defecto
def reset_to_default():
    default_command = ".\\famicom-dumper.exe write-coolboy --coolboy-submapper 1 --file nikita.nes"
    generated_command_text.delete(0, tk.END)
    generated_command_text.insert(0, default_command)

# Modificar la función para usar el comando del campo de texto
def execute_command():
    command = generated_command_text.get()

    # Función para ejecutar el comando en un hilo separado
    def run_command():
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True  # Usar shell=True para ejecutar el comando completo como una cadena
            )
            # Leer la salida en tiempo real
            for line in process.stdout:
                output_text.insert(tk.END, line)
                output_text.see(tk.END)  # Desplazar automáticamente hacia abajo
            for line in process.stderr:
                output_text.insert(tk.END, "[ERROR] " + line)
                output_text.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el comando: {e}")

    # Limpiar el área de texto de salida antes de ejecutar
    output_text.delete(1.0, tk.END)
    # Crear un hilo para no bloquear la interfaz
    threading.Thread(target=run_command).start()

# Lista de mappers con sus números
mappers_list = [
    "0", "1", "2", "3", "4", "5", "7", "9", "10", "11", "19", "21", "22", "23", "24", "25", "26",
    "30", "57", "58", "69", "73", "85", "87", "114", "202", "203", "210", "268", "268.1", "268.2", "268.3", "342"
]

# Función para mostrar la ventana de selección de mappers
def select_mapper():
    def on_mapper_select(event=None):
        selected_mapper = mapper_listbox.get(tk.ACTIVE)
        if selected_mapper:
            # Actualizar el comando generado con el número del mapper seleccionado
            mapper_option = f"--mapper {selected_mapper}"
            update_generated_command(mapper_option=mapper_option, submapper_option=None)  # Eliminar submapper si se selecciona mapper
        mapper_window.destroy()  # Cerrar la ventana después de seleccionar el mapper

    mapper_window = tk.Toplevel(root)
    mapper_window.title("Seleccionar Mapper")
    mapper_window.geometry("400x300")

    mapper_label = tk.Label(mapper_window, text="Selecciona un mapper (solo números):")
    mapper_label.pack(pady=10)

    mapper_listbox = tk.Listbox(mapper_window, height=15, width=20)
    for mapper in mappers_list:
        mapper_listbox.insert(tk.END, mapper)
    mapper_listbox.pack(pady=10)
    mapper_listbox.bind("<Double-Button-1>", on_mapper_select)  # Seleccionar con doble clic

    select_button = tk.Button(mapper_window, text="Seleccionar", command=on_mapper_select)
    select_button.pack(pady=10)

# Función para manejar cambios en el comando seleccionado
def on_command_change(*args):
    selected_command = command_var.get()
    if (selected_command == "list-mappers"):
        select_mapper()
    update_generated_command()

# Crear la ventana principal
root = tk.Tk()
root.title("Famicom Dumper GUI COOLBOY- By TipitoChen")  # Actualizar el título de la ventana

# Campo para seleccionar archivo
file_frame = tk.Frame(root)
file_frame.pack(pady=10)
file_label = tk.Label(file_frame, text="Archivo ROM:")
file_label.pack(side=tk.LEFT, padx=5)
file_entry = tk.Entry(file_frame, width=50)
file_entry.insert(0, "nikita.nes")  # Valor inicial por defecto cambiado a "nikita.nes"
file_entry.pack(side=tk.LEFT, padx=5)
file_button = tk.Button(file_frame, text="Seleccionar", command=select_file)
file_button.pack(side=tk.LEFT, padx=5)

# Menú desplegable para comandos, botón de seleccionar mapper y submapper
command_frame = tk.Frame(root)
command_frame.pack(pady=10)
command_label = tk.Label(command_frame, text="Comando:")
command_label.pack(side=tk.LEFT, padx=5)
command_var = tk.StringVar(value="write-coolboy")  # Comando por defecto
command_menu = tk.OptionMenu(
    command_frame,
    command_var,
    "list-mappers",
    "dump",
    "server",
    "script",
    "reset",
    "dump-fds",
    "write-fds",
    "read-prg-ram",
    "write-prg-ram",
    "write-coolboy",
    "write-coolboy-gpio",
    "write-coolgirl",
    "write-unrom512",
    "info-coolboy",
    "info-coolboy-gpio",
    "info-coolgirl",
    "info-unrom512"
)
command_menu.pack(side=tk.LEFT, padx=5)

mapper_button = tk.Button(command_frame, text="Seleccionar Mapper", command=select_mapper)
mapper_button.pack(side=tk.LEFT, padx=5)

submapper_label = tk.Label(command_frame, text="Submapper:")
submapper_label.pack(side=tk.LEFT, padx=5)
submapper_var = tk.StringVar(value="1")  # Submapper por defecto cambiado a "1"
submapper_menu = tk.OptionMenu(
    command_frame,
    submapper_var,
    "0",  # Volver a incluir el submapper "0"
    "1",
    "2",
    "3"
)
submapper_menu.pack(side=tk.LEFT, padx=5)

# Actualizar el comando al cambiar el submapper
submapper_var.trace("w", lambda *args: update_generated_command(mapper_option=None, submapper_option=submapper_var.get()))

# Opciones adicionales disponibles (sin mapper ni submapper)
additional_options_list = [
    "--prg-size <size>",
    "--chr-size <size>",
    "--prg-ram-size <size>",
    "--chr-ram-size <size>",
    "--prg-nvram-size <size>",
    "--chr-nvram-size <size>",
    "--battery",
    "--unif-name <name>",
    "--unif-author <name>",
    "--fds-sides <sides>",
    "--fds-skip-sides <sides>",
    "--fds-no-header",
    "--fds-dump-hidden",
    "--reset",
    "--cs-file <C#_file>",
    "--bad-sectors <bad_sectors>",
    "--ignore-bad-sectors",
    "--verify",
    "--lock",
    "--sound"
]

# Campo para seleccionar opciones adicionales (selección única)
options_frame = tk.Frame(root)
options_frame.pack(pady=10)
options_label = tk.Label(options_frame, text="Opciones adicionales:")
options_label.pack(side=tk.LEFT, padx=5)

options_listbox = tk.Listbox(options_frame, selectmode=tk.SINGLE, height=10, width=50)  # Selección única
for option in additional_options_list:
    options_listbox.insert(tk.END, option)
options_listbox.pack(side=tk.LEFT, padx=5)

# Función para agregar una opción adicional al comando al hacer clic
def add_additional_option(event):
    selected_option = options_listbox.get(tk.ACTIVE)
    if selected_option:
        current_command = generated_command_text.get().split()
        if selected_option not in current_command:
            current_command.insert(-2, selected_option)  # Insertar antes de "--file"
            generated_command_text.delete(0, tk.END)
            generated_command_text.insert(0, " ".join(current_command))

# Agregar opción adicional al comando al hacer clic
options_listbox.bind("<<ListboxSelect>>", add_additional_option)

# Botón para ejecutar el comando
execute_button = tk.Button(root, text="Ejecutar", command=execute_command)
execute_button.pack(pady=10)

# Campo para mostrar y editar el comando generado (movido debajo del botón "Ejecutar")
generated_command_frame = tk.Frame(root)
generated_command_frame.pack(pady=10)
generated_command_label = tk.Label(generated_command_frame, text="Comando generado:")
generated_command_label.pack(side=tk.LEFT, padx=5)

generated_command_text = tk.Entry(generated_command_frame, width=80)
generated_command_text.insert(0, ".\\famicom-dumper.exe write-coolboy --coolboy-submapper 1 --file nikita.nes")  # Comando por defecto
generated_command_text.pack(side=tk.LEFT, padx=5)

# Botón para restablecer el comando al valor por defecto
default_button = tk.Button(generated_command_frame, text="Default", command=reset_to_default)
default_button.pack(side=tk.LEFT, padx=5)

# Área de texto para mostrar la salida de ejecución (debajo de la caja de comandos)
output_frame = tk.Frame(root)
output_frame.pack(pady=10)
output_label = tk.Label(output_frame, text="Salida de ejecución:")
output_label.pack()
output_text = tk.Text(output_frame, height=15, width=80)
output_text.pack()

# Vincular cambios en el comando seleccionado
command_var.trace("w", on_command_change)

# Actualizar el comando inicial al iniciar el programa
update_generated_command(submapper_option="1")  # Configurar submapper por defecto como "1"

# Iniciar el bucle principal de la interfaz
root.mainloop()