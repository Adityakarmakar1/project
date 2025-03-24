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
root.geometry("500x400")

cpu_usage = tk.StringVar()
memory_usage = tk.StringVar()

tk.Label(root, textvariable=cpu_usage, font=("Arial", 12)).pack(pady=5)
tk.Label(root, textvariable=memory_usage, font=("Arial", 12)).pack(pady=5)

columns = ("PID", "Process Name", "CPU Usage (%)")
process_list = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    process_list.heading(col, text=col)
    process_list.column(col, anchor="center", width=150)

process_list.pack(expand=True, fill="both", padx=10, pady=10)

update_dashboard()
root.mainloop()
