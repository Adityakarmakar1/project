import tkinter as tk
import psutil
from tkinter import ttk

def update_dashboard():
    cpu_usage.set(f"CPU Usage: {psutil.cpu_percent()}%")
    memory_info = psutil.virtual_memory()
    memory_usage.set(f"Memory Usage: {memory_info.percent}%")
    
    process_list.delete(*process_list.get_children())
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        process_list.insert("", "end", values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
    
    root.after(1000, update_dashboard)

root = tk.Tk()
root.title("Real-Time Process Monitoring Dashboard")
root.geometry("600x450")
root.configure(bg="#2c3e50")

cpu_usage = tk.StringVar()
memory_usage = tk.StringVar()

tk.Label(root, text="System Monitor", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=10)
tk.Label(root, textvariable=cpu_usage, font=("Arial", 12), fg="#f39c12", bg="#2c3e50").pack(pady=5)
tk.Label(root, textvariable=memory_usage, font=("Arial", 12), fg="#e74c3c", bg="#2c3e50").pack(pady=5)

frame = tk.Frame(root, bg="#34495e", bd=2, relief="ridge")
frame.pack(expand=True, fill="both", padx=10, pady=10)

columns = ("PID", "Process Name", "CPU Usage (%)")
process_list = ttk.Treeview(frame, columns=columns, show="headings")
for col in columns:
    process_list.heading(col, text=col)
    process_list.column(col, anchor="center", width=180)

style = ttk.Style()
style.configure("Treeview", background="#ecf0f1", foreground="black", rowheight=25, fieldbackground="#bdc3c7")
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#3498db", foreground="white")
style.map("Treeview", background=[("selected", "#2980b9")])

process_list.pack(expand=True, fill="both", padx=5, pady=5)

update_dashboard()
root.mainloop()
