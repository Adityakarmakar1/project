import tkinter as tk
import psutil
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections

def start_monitoring():
    welcome_frame.pack_forget()
    dashboard_frame.pack(expand=True, fill="both")
    update_dashboard()

def update_dashboard():
    cpu_usage_value = psutil.cpu_percent()
    cpu_usage.set(f"CPU Usage: {cpu_usage_value}%")
    memory_info = psutil.virtual_memory()
    memory_usage.set(f"Memory Usage: {memory_info.percent}%")
    
    process_list.delete(*process_list.get_children())
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        process_list.insert("", "end", values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
    
    update_pie_chart()
    update_line_graph(cpu_usage_value)
    root.after(1000, update_dashboard)

def update_pie_chart():
    memory_info = psutil.virtual_memory()
    labels = ["Used", "Available"]
    sizes = [memory_info.used, memory_info.available]
    colors = ["#e74c3c", "#2ecc71"]
    ax_pie.clear()
    ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax_pie.set_title("Memory Consumption")
    canvas_pie.draw_idle()

def update_line_graph(cpu_value):
    cpu_history.append(cpu_value)
    ax_line.clear()
    ax_line.plot(cpu_history, marker='o', linestyle='-', color='b', label="CPU Usage (%)")
    ax_line.set_title("CPU Usage Over Time")
    ax_line.set_xlabel("Time (seconds)")
    ax_line.set_ylabel("CPU Usage (%)")
    ax_line.set_ylim(0, 100)
    ax_line.legend()
    canvas_line.draw_idle()

root = tk.Tk()
root.title("Real-Time Process Monitoring Dashboard")
root.geometry("900x700")
root.configure(bg="#2c3e50")

# Welcome Page
welcome_frame = tk.Frame(root, bg="#2c3e50")
tk.Label(welcome_frame, text="Welcome to System Monitor", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=20)
tk.Button(welcome_frame, text="Start Monitoring", font=("Arial", 12), bg="#3498db", fg="white", command=start_monitoring).pack(pady=10)
welcome_frame.pack(expand=True, fill="both")

# Monitoring Dashboard
dashboard_frame = tk.Frame(root, bg="#2c3e50")
cpu_usage = tk.StringVar()
memory_usage = tk.StringVar()

tk.Label(dashboard_frame, text="System Monitor", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=10)
tk.Label(dashboard_frame, textvariable=cpu_usage, font=("Arial", 12), fg="#f39c12", bg="#2c3e50").pack(pady=5)
tk.Label(dashboard_frame, textvariable=memory_usage, font=("Arial", 12), fg="#e74c3c", bg="#2c3e50").pack(pady=5)

frame = tk.Frame(dashboard_frame, bg="#34495e", bd=2, relief="ridge")
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

# Frame for Pie Chart and Line Graph
graph_frame = tk.Frame(dashboard_frame, bg="#2c3e50")
graph_frame.pack(expand=True, fill="both", padx=10, pady=10, side="top")

# Pie Chart for Memory Consumption
fig_pie, ax_pie = plt.subplots(figsize=(4, 4), dpi=100)
canvas_pie = FigureCanvasTkAgg(fig_pie, master=graph_frame)
canvas_pie.get_tk_widget().pack(side="left", padx=10, pady=10)

# Line Graph for CPU Usage
cpu_history = collections.deque(maxlen=60)  # Stores last 60 seconds of CPU data
fig_line, ax_line = plt.subplots(figsize=(5, 3), dpi=100)
canvas_line = FigureCanvasTkAgg(fig_line, master=graph_frame)
canvas_line.get_tk_widget().pack(side="right", padx=10, pady=10, fill='both', expand=True)

root.mainloop()