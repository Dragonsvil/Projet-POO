import tkinter as tk
from tkinter import ttk, messagebox #un sous module de tkinter plus moderne et stylé
from PIL import Image, ImageTk
import sqlite3

DB_PATH = r"C:\Users\malak\Documents\POO\POO Projet\AdoptionCenter.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def get_table_columns(table):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    info = cur.fetchall()
    conn.close()
    return info

# fonction d'affichage
def show_data(table, tree):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()

        info = get_table_columns(table)
        cols = [col[1] for col in info]
        tree["columns"] = cols
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")
        # vider le tableau
        for r in tree.get_children():
            tree.delete(r)
        for row in rows:
            tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        conn.close()

# fonction d'insertion
def insert_data_dynamic(table, entries_values):
    # entries_values = (col_nom, valeur)
    try:
        cols = [c for c, v in entries_values]
        vals = [v for c, v in entries_values]
        placeholders = ", ".join(["?"] * len(vals))
        cols_str = ", ".join(cols)
        query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query, vals)
        conn.commit()
        # mise à jour automatique du status de l'animal après adoption
        if table.lower() == "adoptions":
            try:
                id_index = [c.lower() for c in cols].index("code_an")
                code_an = vals[id_index]
                cur.execute("UPDATE Animaux SET status = 'Adopté' WHERE code_an = ?", (code_an,))
                conn.commit()
            except ValueError:
                pass

        messagebox.showinfo("Succès", "Insertion réussie ✅")
    except Exception as e:
        messagebox.showerror("Erreur insertion", str(e))
    finally:
        conn.close()

# fonction de suppression
def delete_row(table, pk_col, pk_value):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {pk_col} = ?", (pk_value,))
        conn.commit()
        messagebox.showinfo("Succès", "Suppression réussie ✅")
    except Exception as e:
        messagebox.showerror("Erreur suppression", str(e))
    finally:
        conn.close()

# fonction de MAJ
def update_row(table, pk_col, pk_value, updates):
    try:
        set_clause = ", ".join([f"{c}=?" for c, v in updates])
        vals = [v for c, v in updates] + [pk_value]
        query = f"UPDATE {table} SET {set_clause} WHERE {pk_col} = ?"
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query, vals)
        conn.commit()
        messagebox.showinfo("Succès", "Mise à jour réussie ✅")
    except Exception as e:
        messagebox.showerror("Erreur mise à jour", str(e))
    finally:
        conn.close()

# interface graphique
window = tk.Tk()
window.title("PetPal : Gestion du centre d'adoption")
window.geometry("1000x650")
window.resizable(True, True)

icon= tk.PhotoImage(file="Images/icon.png")
window.iconphoto(True, icon)

bg_original = Image.open("Images/background_interface.jpg")
initial_w, initial_h = 1000, 650
bg_resized = bg_original.resize((initial_w, initial_h), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_resized)

bg_label = tk.Label(window, image=bg_photo)
bg_label.image = bg_photo
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

_resize_after_id = None

def resize_bg(event):
    global _resize_after_id
    if _resize_after_id is not None:
        window.after_cancel(_resize_after_id)
    _resize_after_id = window.after(120, lambda: _do_resize(event.width, event.height))

def _do_resize(new_w, new_h):
    global bg_photo, _resize_after_id
    if new_w <= 0 or new_h <= 0:
        return
    resized = bg_original.resize((new_w, new_h), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized)
    bg_label.config(image=bg_photo)
    bg_label.image = bg_photo
    _resize_after_id = None

window.bind("<Configure>", resize_bg)

main_color = "#0f2941"
accent_blue = "#93cfe6"
light_bg = "#bfe5f4"
white = "#ffffff"

title_font = ("Anton", 22, "bold")
label_font = ("Poppins", 11)
button_font = ("Poppins", 10, "bold")

style = ttk.Style()
style.theme_use("clam")

style.configure("Rounded.TButton",
    font=button_font,
    background=accent_blue,
    foreground=main_color,
    padding=8,
    borderwidth=0,
    relief="flat"
)
style.map("Rounded.TButton",
    background=[("active", "#aadcf2"), ("pressed", "#7cc3de")]
)

style.configure("Treeview",
    background=white,
    fieldbackground=white,
    foreground=main_color,
    font=("Poppins", 10),
    rowheight=26
)
style.configure("Treeview.Heading",
    background=accent_blue,
    foreground=main_color,
    font=("Poppins", 10, "bold")
)
style.map("Treeview", background=[("selected", "#d4eefb")])

top_frame = tk.Frame(window, bg=light_bg)
top_frame.pack(fill="x", padx=12, pady=8)

tk.Label(top_frame, text="Table :", bg=light_bg, fg=main_color, font=label_font).pack(side="left")
table_var = tk.StringVar(value="Adopteurs")
tables = ["Adopteurs", "Animaux", "Adoptions"]
table_menu = ttk.Combobox(top_frame, textvariable=table_var, values=tables, state="readonly", width=18, font=label_font)
table_menu.pack(side="left", padx=8)

btn_frame = tk.Frame(top_frame, bg=light_bg)
btn_frame.pack(side="right")

tree_frame = tk.Frame(window)
tree_frame.pack(fill="both", expand=True, padx=12, pady=(0,8))

tree = ttk.Treeview(tree_frame, show="headings")
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Actions des bouttons afficher(show) , inserer (insert) , supprimer(delete) ,  MAJ (update))
def refresh():
    show_data(table_var.get(), tree)

def open_insert_window():
    table = table_var.get()
    info = get_table_columns(table)
    insert_cols = [col for col in info if col[5] == 0]

    win = tk.Toplevel(window)
    win.title(f"Insérer dans {table}")
    win.config(bg="#e4f5fb")
    entries = []
    for i, col in enumerate(insert_cols):
        tk.Label(win, text=col[1], bg="#e4f5fb", fg=main_color, font=label_font).grid(row=i, column=0, padx=8, pady=6, sticky="e")
        ent = tk.Entry(win, width=40, font=label_font, fg=main_color)
        ent.grid(row=i, column=1, padx=8, pady=6, sticky="w")
        entries.append((col[1], ent))

    def on_insert():
        pairs = []
        for col, ent in entries:
            val = ent.get().strip()

            # Vérification : pas de chiffres dans nom, prénom, etc.
            if col.lower() in ["nom_an", "nom_ad", "prenom_ad", "race",'status']:
                if any(char.isdigit() for char in val):
                    messagebox.showerror("Erreur", f"Le champ '{col}' ne doit pas contenir de chiffres ❌")
                    return

            if val == "":
                val = None
            pairs.append((col, val))

        insert_data_dynamic(table, pairs)
        
        win.destroy()
        refresh()

    ttk.Button(win, text="Insérer", style="Rounded.TButton", command=on_insert).grid(row=len(entries), column=0, columnspan=2, pady=10)

def delete_selected():
    table = table_var.get()
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Alerte", "Aucune ligne sélectionnée")
        return
    vals = tree.item(sel[0])['values']
    info = get_table_columns(table)
    pk_col = info[0][1]
    pk_value = vals[0]
    if messagebox.askyesno("Confirmer", f"Supprimer {pk_col}={pk_value} ?"):
        delete_row(table, pk_col, pk_value)
        refresh()

def open_update_window():
    table = table_var.get()
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Alerte", "Aucune ligne sélectionnée")
        return
    vals = tree.item(sel[0])['values']
    info = get_table_columns(table)
    cols = [c[1] for c in info]
    pk_col = info[0][1]
    pk_value = vals[0]

    updatable = [col for col in info if col[5] == 0]

    win = tk.Toplevel(window)
    win.title(f"Mettre à jour {table} - {pk_col}={pk_value}")
    win.config(bg="#e4f5fb")
    entries = []
    col_index = {c: i for i, c in enumerate(cols)}

    for i, col in enumerate(updatable):
        col_name = col[1]
        tk.Label(win, text=col_name, bg="#e4f5fb", fg=main_color, font=label_font).grid(row=i, column=0, padx=8, pady=6, sticky="e")
        ent = tk.Entry(win, width=40, font=label_font, fg=main_color)
        current_val = vals[col_index[col_name]]
        ent.insert(0, "" if current_val is None else str(current_val))
        ent.grid(row=i, column=1, padx=8, pady=6, sticky="w")
        entries.append((col_name, ent))

    def on_update():
        updates = [(col, ent.get().strip() or None) for col, ent in entries]
        update_row(table, pk_col, pk_value, updates)
        win.destroy()
        refresh()

    ttk.Button(win, text="Mettre à jour",style="Rounded.TButton", command=on_update).grid(row=len(entries), column=0, columnspan=2, pady=10)

ttk.Button(btn_frame, text="Afficher",style="Rounded.TButton", command=refresh).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Insérer",style="Rounded.TButton", command=open_insert_window).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Supprimer",style="Rounded.TButton", command=delete_selected).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Mettre à jour",style="Rounded.TButton", command=open_update_window).pack(side="left", padx=6)

refresh()

window.mainloop()