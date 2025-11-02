import tkinter as tk
from tkinter import ttk, messagebox    #un sous module de tkinter plus moderne et stylé
import sqlite3

DB_PATH =r"C:\Users\malak\Documents\POO\POO Projet\AdoptionCenter.db"

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

        #vider le tableau 
        for r in tree.get_children():
            tree.delete(r)
        for row in rows:
            tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        conn.close()

# fonction d'incertion
def insert_data_dynamic(table, entries_values):
    # entries_valeues = (col_nom, valeur)
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
window.title("🐾 PetPal - Gestion du centre d'adoption")
window.geometry("1000x650")

style = ttk.Style()
style.theme_use("clam")

top_frame = tk.Frame(window)
top_frame.pack(fill="x", padx=12, pady=8)

tk.Label(top_frame, text="Table :", font=("Arial", 11)).pack(side="left")
table_var = tk.StringVar(value="Adopteurs")
tables = ["Adopteurs", "Animaux", "Adoptions"]
table_menu = ttk.Combobox(top_frame, textvariable=table_var, values=tables, state="readonly", width=18)
table_menu.pack(side="left", padx=8)

btn_frame = tk.Frame(top_frame)
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
    entries = []
    for i, col in enumerate(insert_cols):
        tk.Label(win, text=col[1]).grid(row=i, column=0, padx=8, pady=6, sticky="e")
        ent = tk.Entry(win, width=40)
        ent.grid(row=i, column=1, padx=8, pady=6, sticky="w")
        entries.append((col[1], ent))

    def on_insert():
        pairs = []
        for col_name, ent in entries:
            val = ent.get().strip()
            if val == "":
                val = None
            pairs.append((col_name, val))
        insert_data_dynamic(table, pairs)
        win.destroy()
        refresh()

    ttk.Button(win, text="Insérer", command=on_insert).grid(row=len(entries), column=0, columnspan=2, pady=10)

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
    confirm = messagebox.askyesno("Confirmer", f"Supprimer {pk_col}={pk_value} ?")
    if not confirm:
        return
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
    entries = []
    col_index = {c: i for i, c in enumerate(cols)}

    for i, col in enumerate(updatable):
        col_name = col[1]
        tk.Label(win, text=col_name).grid(row=i, column=0, padx=8, pady=6, sticky="e")
        ent = tk.Entry(win, width=40)
        current_val = vals[col_index[col_name]]
        ent.insert(0, "" if current_val is None else str(current_val))
        ent.grid(row=i, column=1, padx=8, pady=6, sticky="w")
        entries.append((col_name, ent))

    def on_update():
        updates = []
        for col_name, ent in entries:
            val = ent.get().strip()
            if val == "":
                val = None
            updates.append((col_name, val))
        update_row(table, pk_col, pk_value, updates)
        win.destroy()
        refresh()

    ttk.Button(win, text="Mettre à jour", command=on_update).grid(row=len(entries), column=0, columnspan=2, pady=10)

ttk.Button(btn_frame, text="Afficher", command=refresh).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Insérer", command=open_insert_window).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Supprimer", command=delete_selected).pack(side="left", padx=6)
ttk.Button(btn_frame, text="Mettre à jour", command=open_update_window).pack(side="left", padx=6)

refresh()

window.mainloop()