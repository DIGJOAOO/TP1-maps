import tkinter as tk
import customtkinter as ctk
from maps import mostrar_mapa
from gitAPI import gitAPI

root = tk.Tk()
root.title("Menu")
root.geometry("1280x720")
root.resizable(False, False)


top_frame = ctk.CTkFrame(root, height=60)
top_frame.pack(fill="x")

main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True)


def Exit():
    root.destroy()

def gitapi():
    gitAPI()

def open_maps():
    mostrar_mapa(main_frame)


git_button = ctk.CTkButton(
    top_frame,
    text="API",
    width=80,
    height=40,
    fg_color="#181818",
    hover_color="#181818",
    corner_radius=20,
    font=("ThisAppeal-FreeDemo", 12),
    command=gitapi
)

map_button = ctk.CTkButton(
    top_frame,
    text="Mapa",
    width=80,
    height=40,
    fg_color="#181818",
    hover_color="#181818",
    corner_radius=20,
    font=("ThisAppeal-FreeDemo", 12),
    command=open_maps
)

exit_button = ctk.CTkButton(
    top_frame,
    text="Salir",
    width=80,
    height=40,
    fg_color="#181818",
    hover_color="#181818",
    corner_radius=20,
    font=("ThisAppeal-FreeDemo", 12),
    command=Exit
)

git_button.pack(side="left", padx=10, pady=10)
map_button.pack(side="left", padx=10, pady=10)
exit_button.pack(side="left", padx=10, pady=10)

root.mainloop()