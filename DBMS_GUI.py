import psycopg2
from tkinter import *
from tkinter import messagebox, simpledialog, ttk

# ===================== DATABASE CONNECTION =====================
def connect_db(dbname=None):
    try:
        if dbname:
            return psycopg2.connect(
                dbname=dbname,
                user="postgres",
                password=" Tjl3e",
                host="localhost",
                port="5432"
            )
        else:
            return psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=" Tjl3e",
                host="localhost",
                port="5432"
            )
    except Exception as e:
        return None

# ===================== WAITING MODAL (NO ANIMATION) =====================
def show_waiting_modal(parent, check_func, on_ready):
    modal = Toplevel(parent)
    modal.title("Please Wait")
    modal.geometry("320x120")
    modal.transient(parent)
    modal.grab_set()
    modal.resizable(False, False)
    Label(modal, text="Please wait as we create the database...", font=("Arial", 11, "bold")).pack(pady=30)

    def poll():
        if check_func():
            modal.destroy()
            on_ready()
        else:
            modal.after(400, poll)

    poll()

# ===================== GUI FUNCTIONS =====================
def show_welcome():
    welcome = Toplevel(bg="#f0f8ff")
    welcome.title("Welcome")
    welcome.geometry("400x220")
    Label(welcome, text="WELCOME TO THE GUI FOR CREATING AND MANAGING YOUR DATABASES",
          wraplength=350, font=("Arial", 12, "bold"), bg="#f0f8ff", fg="#222").pack(pady=20)
    Button(welcome, text="View Existing Databases", bg="#27ae60", fg="white", width=25,
           font=("Arial", 10, "bold"), command=lambda: [welcome.destroy(), show_db_list(show_welcome)]).pack(pady=5)
    Button(welcome, text="Create a New Database", bg="#2980b9", fg="white", width=25,
           font=("Arial", 10, "bold"), command=lambda: [welcome.destroy(), show_create_db(show_welcome)]).pack(pady=5)

def show_db_list(back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title("Existing Databases")
    win.geometry("350x340")
    Label(win, text="Databases:", font=("Arial", 11, "bold"), bg="#f9f9f9", fg="#333").pack(pady=5)
    db_listbox = Listbox(win, width=40, bg="#eaf2fb", fg="#222", font=("Arial", 10))
    db_listbox.pack(pady=5)
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = cur.fetchall()
        for db in dbs:
            db_listbox.insert(END, db[0])
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e), parent=win)
    def open_db():
        selected = db_listbox.get(ACTIVE)
        if selected:
            win.destroy()
            manage_database_window(selected, lambda: show_db_list(back_callback))
    Button(win, text="Manage Selected Database", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
           command=open_db).pack(pady=10)
    Button(win, text="Back", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
           command=lambda: [win.destroy(), back_callback()]).pack(pady=2)

def manage_database_window(db_name, back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title(f"Manage Database: {db_name}")
    win.geometry("350x200")
    Label(win, text=f"Database: {db_name}", font=("Arial", 12, "bold"), bg="#f9f9f9", fg="#333").pack(pady=10)
    def delete_db():
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete database '{db_name}'?", parent=win):
            conn = connect_db("postgres")  # Connect to 'postgres' to drop another db
            if conn:
                conn.autocommit = True
                cur = conn.cursor()
                try:
                    cur.execute(f"DROP DATABASE \"{db_name}\"")
                    messagebox.showinfo("Deleted", f"Database '{db_name}' deleted.", parent=win)
                    win.destroy()
                    back_callback()
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=win)
                cur.close()
                conn.close()
    def update_db():
        win.destroy()
        show_table_list(db_name, lambda: manage_database_window(db_name, back_callback))
    Button(win, text="Delete Database", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
           command=delete_db).pack(pady=10)
    Button(win, text="Update Database (Tables)", bg="#2980b9", fg="white", font=("Arial", 10, "bold"),
           command=update_db).pack(pady=5)
    Button(win, text="Back", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
           command=lambda: [win.destroy(), back_callback()]).pack(pady=2)

def show_table_list(db_name, back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title(f"Tables in {db_name}")
    win.geometry("400x400")
    Label(win, text=f"Tables in {db_name}:", font=("Arial", 11, "bold"), bg="#f9f9f9", fg="#333").pack(pady=5)
    table_listbox = Listbox(win, width=40, bg="#eaf2fb", fg="#222", font=("Arial", 10))
    table_listbox.pack(pady=5, fill=X)

    def refresh_tables():
        table_listbox.delete(0, END)
        try:
            conn = connect_db(dbname=db_name)
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            for t in tables:
                table_listbox.insert(END, t[0])
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    def add_table():
        win.destroy()
        show_table_creation(db_name, lambda: show_table_list(db_name, back_callback))

    def edit_table():
        selected = table_listbox.get(ACTIVE)
        if selected:
            win.destroy()
            open_table_window(db_name, selected, lambda: show_table_list(db_name, back_callback))

    def delete_table():
        selected = table_listbox.get(ACTIVE)
        if selected and messagebox.askyesno("Confirm", f"Delete table '{selected}'?", parent=win):
            try:
                conn = connect_db(dbname=db_name)
                cur = conn.cursor()
                cur.execute(f'DROP TABLE IF EXISTS "{selected}" CASCADE')
                conn.commit()
                cur.close()
                conn.close()
                refresh_tables()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

    refresh_tables()

    Button(win, text="Add Table", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
           command=add_table).pack(pady=5)
    Button(win, text="Edit Table", bg="#2980b9", fg="white", font=("Arial", 10, "bold"),
           command=edit_table).pack(pady=5)
    Button(win, text="Delete Table", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
           command=delete_table).pack(pady=5)
    Button(win, text="Back", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
           command=lambda: [win.destroy(), back_callback()]).pack(pady=5)

def show_create_db(back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title("Create Database")
    win.geometry("350x180")
    Label(win, text="Enter Database Name:", font=("Arial", 11), bg="#f9f9f9", fg="#333").pack(pady=10)
    db_name_entry = Entry(win, width=30, bg="#eaf2fb", fg="#222", font=("Arial", 10))
    db_name_entry.pack(pady=5)
    def create_db():
        db_name = db_name_entry.get()
        if db_name:
            conn = connect_db()
            if conn:
                conn.autocommit = True
                cur = conn.cursor()
                try:
                    cur.execute(f"CREATE DATABASE {db_name}")
                    win.destroy()
                    # Show waiting modal (no animation)
                    def check_db_ready():
                        try:
                            test_conn = connect_db(dbname=db_name)
                            if test_conn:
                                test_conn.close()
                                return True
                        except:
                            return False
                        return False
                    def after_ready():
                        show_table_creation(db_name, show_welcome)
                    show_waiting_modal(root, check_db_ready, after_ready)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=win)
                cur.close()
                conn.close()
    Button(win, text="Create Database", bg="#2980b9", fg="white", font=("Arial", 10, "bold"),
           command=create_db).pack(pady=10)
    Button(win, text="Back", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
           command=lambda: [win.destroy(), back_callback()]).pack(pady=2)

def show_table_creation(db_name, back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title(f"Create Table in {db_name}")
    win.geometry("400x400")
    Label(win, text=f"Database: {db_name}", font=("Arial", 11, "bold"), bg="#f9f9f9", fg="#333").pack(pady=5)
    Label(win, text="Table Name:", bg="#f9f9f9", fg="#333").pack()
    table_name_entry = Entry(win, width=30, bg="#eaf2fb", fg="#222", font=("Arial", 10))
    table_name_entry.pack(pady=2)
    Label(win, text="Number of Columns:", bg="#f9f9f9", fg="#333").pack()
    col_num_entry = Entry(win, width=5, bg="#eaf2fb", fg="#222", font=("Arial", 10))
    col_num_entry.pack(pady=2)

    col_frame = Frame(win, bg="#f9f9f9")
    col_frame.pack(pady=5)
    col_entries = []

    def create_col_entries():
        for widget in col_frame.winfo_children():
            widget.destroy()
        col_entries.clear()
        try:
            n = int(col_num_entry.get())
            for i in range(n):
                Label(col_frame, text=f"Column {i+1} Name:", bg="#f9f9f9", fg="#333").grid(row=i, column=0, sticky="e")
                e = Entry(col_frame, width=15, bg="#eaf2fb", fg="#222", font=("Arial", 10))
                e.grid(row=i, column=1)
                col_entries.append(e)
        except:
            pass

    col_num_entry.bind("<Return>", lambda e: create_col_entries())
    Button(win, text="Set Columns", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
           command=create_col_entries).pack(pady=2)

    def create_table_and_open():
        table_name = table_name_entry.get()
        col_names = [e.get() for e in col_entries if e.get()]
        if db_name and table_name and col_names:
            conn = connect_db(dbname=db_name)
            if conn:
                cur = conn.cursor()
                try:
                    columns_sql = ', '.join([f'"{col}" TEXT' for col in col_names])
                    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (id SERIAL PRIMARY KEY, {columns_sql})'
                    cur.execute(sql)
                    conn.commit()
                    messagebox.showinfo("Success", f"Table '{table_name}' created in '{db_name}'", parent=win)
                    win.destroy()
                    open_table_window(db_name, table_name, lambda: show_table_creation(db_name, back_callback))
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=win)
                cur.close()
                conn.close()
    Button(win, text="Create Table", bg="#2980b9", fg="white", font=("Arial", 10, "bold"),
           command=create_table_and_open).pack(pady=10)
    Button(win, text="Back", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
           command=lambda: [win.destroy(), back_callback()]).pack(pady=2)

def open_table_window(db_name, table_name, back_callback):
    win = Toplevel(bg="#f9f9f9")
    win.title(f"Table: {table_name}")
    win.geometry("700x420")

    def get_columns():
        conn = connect_db(dbname=db_name)
        cur = conn.cursor()
        cur.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        cols = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return cols

    columns = get_columns()
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 10), rowheight=25, background="#eaf2fb", fieldbackground="#eaf2fb")
    tree = ttk.Treeview(win, columns=columns, show="headings", style="Treeview")
    for col in columns:
        tree.heading(col, text=col.capitalize())
    tree.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    # Add Column Button
    def add_column():
        new_col = simpledialog.askstring("Add Column", "Enter column name:", parent=win)
        if new_col:
            try:
                conn = connect_db(dbname=db_name)
                cur = conn.cursor()
                cur.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{new_col}" TEXT')
                conn.commit()
                cur.close()
                conn.close()
                # Refresh columns and treeview
                new_columns = get_columns()
                tree["columns"] = new_columns
                for col in new_columns:
                    tree.heading(col, text=col.capitalize())
                fetch_rows()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

    Button(win, text="Add Column", command=add_column, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)

    # Add/Edit/Delete logic
    def add_row():
        values = []
        for col in tree["columns"]:
            if col == "id":
                values.append(None)
            else:
                val = simpledialog.askstring("Input", f"Enter value for {col}:", parent=win)
                values.append(val)
        try:
            conn = connect_db(dbname=db_name)
            cur = conn.cursor()
            cols = ','.join(f'"{c}"' for c in tree["columns"] if c != "id")
            placeholders = ','.join(['%s'] * (len(values) - 1))
            cur.execute(
                f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})',
                tuple(values[1:])
            )
            conn.commit()
            cur.close()
            conn.close()
            fetch_rows()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    def delete_row():
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            row_id = item["values"][0]
            try:
                conn = connect_db(dbname=db_name)
                cur = conn.cursor()
                cur.execute(f'DELETE FROM "{table_name}" WHERE id=%s', (row_id,))
                conn.commit()
                cur.close()
                conn.close()
                fetch_rows()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

    def edit_row():
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            row_id = item["values"][0]
            new_values = []
            for idx, col in enumerate(tree["columns"]):
                if col == "id":
                    new_values.append(row_id)
                else:
                    val = simpledialog.askstring("Edit", f"New value for {col}:", initialvalue=item["values"][idx], parent=win)
                    new_values.append(val)
            try:
                conn = connect_db(dbname=db_name)
                cur = conn.cursor()
                set_clause = ', '.join(f'"{col}"=%s' for col in tree["columns"] if col != "id")
                cur.execute(
                    f'UPDATE "{table_name}" SET {set_clause} WHERE id=%s',
                    tuple(new_values[1:] + [row_id])
                )
                conn.commit()
                cur.close()
                conn.close()
                fetch_rows()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

    # Save button to go back to previous window
    def save_and_back():
        messagebox.showinfo("Saved", "Changes saved.")
        win.destroy()
        back_callback()

    Button(win, text="Add Row", command=add_row, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=0, pady=5)
    Button(win, text="Edit Row", command=edit_row, bg="#2980b9", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=1, pady=5)
    Button(win, text="Delete Row", command=delete_row, bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=2, pady=5)
    Button(win, text="Save", command=save_and_back, bg="#16a085", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=3, pady=5)

    def fetch_rows():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = connect_db(dbname=db_name)
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM "{table_name}"')
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", END, values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    fetch_rows()

# ===================== MAIN WINDOW =====================
root = Tk()
root.title("PostgreSQL GUI CRUD Tool")
root.geometry("400x200")
root.withdraw()  # Hide main window, show welcome first

show_welcome()

root.mainloop()