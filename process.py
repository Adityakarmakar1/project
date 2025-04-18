import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections
import random

def initialize_cpu_percent():
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def show_view(view_type):
    welcome_frame.pack_forget()
    dashboard_frame.pack(expand=True, fill="both")
    initialize_cpu_percent()
    frame.pack_forget()
    graph_frame.pack_forget()

    if view_type == "processes":
        frame.pack(fill="x", padx=15, pady=(10, 10))
    elif view_type == "graphs":
        graph_frame.pack(expand=True, fill="both", padx=15, pady=(10, 15))
    elif view_type == "dashboard":
        frame.pack(fill="x", padx=15, pady=(5, 10))
        graph_frame.pack(expand=True, fill="both", padx=15, pady=(0, 15))

    if not update_dashboard.running:
        update_dashboard.running = True
        update_dashboard()

def update_dashboard():
    cpu_val = psutil.cpu_percent(interval=None)
    cpu_usage.set(f"CPU: {cpu_val:.1f}%")
    mem = psutil.virtual_memory()
    memory_usage.set(f"Memory: {mem.used / (1024 ** 2):.1f} MB / {mem.total / (1024 ** 2):.1f} MB")

    update_process_list()
    update_pie_chart(mem)
    update_line_graph(cpu_val)

    root.after(1000, update_dashboard)
update_dashboard.running = False

def update_process_list():
    process_list.delete(*process_list.get_children())
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_info().rss / (1024 * 1024)
            name = proc.info['name']
            if name.lower() not in ["system idle process", "system"]:
                processes.append((proc.pid, name, f"{cpu:.1f}", f"{mem:.1f}"))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    for pid, name, cpu, mem in sorted(processes, key=lambda x: float(x[2]), reverse=True):
        process_list.insert("", "end", values=(pid, name, cpu, mem))

def update_pie_chart(mem):
    labels = ["Used", "Available"]
    sizes = [mem.used, mem.available]
    colors = ["#ff6b6b", "#48dbfb"]
    ax_pie.clear()
    ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax_pie.set_title("Memory Usage", fontsize=12, color="white")
    canvas_pie.draw_idle()

def update_line_graph(cpu_val):
    cpu_history.append(cpu_val)
    ax_line.clear()
    ax_line.plot(cpu_history, color="#00cec9", linewidth=2)
    ax_line.set_ylim(0, 100)
    ax_line.set_title("CPU Usage Over Time", fontsize=12, color="white")
    ax_line.set_facecolor("#2c3e50")
    ax_line.tick_params(colors="white")
    ax_line.set_xlabel("Time (s)", color="white")
    ax_line.set_ylabel("CPU %", color="white")
    canvas_line.draw_idle()

def back_to_menu():
    update_dashboard.running = False
    dashboard_frame.pack_forget()
    welcome_frame.pack(expand=True, fill="both")

# ---------------------- GUI Setup -------------------------
root = tk.Tk()
root.title("Modern Task Manager")
root.geometry("1080x750")
root.configure(bg="#1e272e")

# ---------------------- Welcome Frame with Animated Background ---------------------
welcome_frame = tk.Frame(root, bg="#1e272e")
canvas_bg = tk.Canvas(welcome_frame, bg="#1e272e", highlightthickness=0)
canvas_bg.pack(fill="both", expand=True)

particles = []
for _ in range(50):
    x = random.randint(0, 1080)
    y = random.randint(0, 750)
    r = random.randint(1, 3)
    dx = random.uniform(-0.5, 0.5)
    dy = random.uniform(-0.5, 0.5)
    p = canvas_bg.create_oval(x - r, y - r, x + r, y + r, fill="#7f8fa6", outline="")
    particles.append((p, dx, dy))

def animate_particles():
    for i, (p, dx, dy) in enumerate(particles):
        canvas_bg.move(p, dx, dy)
        x1, y1, x2, y2 = canvas_bg.coords(p)
        if x1 < 0 or x2 > 1080: dx = -dx
        if y1 < 0 or y2 > 750: dy = -dy
        particles[i] = (p, dx, dy)
    canvas_bg.after(33, animate_particles)
animate_particles()

# Welcome content container
welcome_container = tk.Frame(canvas_bg, bg="#1e272e")
canvas_bg.create_window(540, 360, window=welcome_container)

# Image/Icon above heading (replace with your custom path or icon)
try:
    welcome_img = PhotoImage(file="c")  # Make sure the image existsz
    tk.Label(welcome_container, image=welcome_img, bg="#1e272e").pack(pady=(0, 10))
except Exception as e:
    tk.Label(welcome_container, text="💻", font=("Segoe UI Emoji", 56), bg="#1e272e").pack(pady=(0, 10))

# Heading
tk.Label(welcome_container, text="Task Manager Dashboard", font=("Segoe UI", 28, "bold"),
         fg="#f5f6fa", bg="#1e272e").pack(pady=(0, 8))

tk.Label(welcome_container, text="Monitor, analyze and optimize your system in real time.",
         font=("Segoe UI", 14), fg="#a4b0be", bg="#1e272e").pack(pady=(0, 35))

# Updated button style with modern look
def make_modern_button(text, command):
    btn = tk.Label(welcome_container, text=text, font=("Segoe UI", 13, "bold"),
                   bg="#48dbfb", fg="black", padx=30, pady=12, cursor="hand2",
                   relief="raised", bd=0, width=22)
    btn.pack(pady=10)
    btn.bind("<Button-1>", lambda e: command())
    btn.bind("<Enter>", lambda e: btn.config(bg="#00cec9"))
    btn.bind("<Leave>", lambda e: btn.config(bg="#48dbfb"))
    btn.config(highlightthickness=2, highlightbackground="#1e272e", highlightcolor="#1e272e")
    return btn

make_modern_button("🔍 Show Processes", lambda: show_view("processes"))
make_modern_button("📈 Show Graphs", lambda: show_view("graphs"))
make_modern_button("🧩 Show Dashboard", lambda: show_view("dashboard"))

welcome_frame.pack(expand=True, fill="both")

# ---------------------- Dashboard Frame ---------------------
dashboard_frame = tk.Frame(root, bg="#1e272e")

cpu_usage = tk.StringVar()
memory_usage = tk.StringVar()

tk.Label(dashboard_frame, textvariable=cpu_usage, font=("Segoe UI", 16, "bold"),
         fg="#f1c40f", bg="#1e272e").pack(pady=(10, 5))

tk.Label(dashboard_frame, textvariable=memory_usage, font=("Segoe UI", 16, "bold"),
         fg="#e17055", bg="#1e272e").pack(pady=(0, 10))

frame = tk.Frame(dashboard_frame, bg="#2f3542", bd=2)
columns = ("PID", "Process", "CPU (%)", "Memory (MB)")
process_list = ttk.Treeview(frame, columns=columns, show="headings", height=10)
for col in columns:
    process_list.heading(col, text=col)
    process_list.column(col, anchor="center", width=180)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#dfe6e9", fieldbackground="#dfe6e9",
                foreground="#2d3436", rowheight=28, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#00cec9", foreground="black")

process_list.pack(fill="x", padx=10, pady=10)

graph_frame = tk.Frame(dashboard_frame, bg="#1e272e")
fig_pie, ax_pie = plt.subplots(figsize=(4, 4), dpi=100)
fig_pie.patch.set_facecolor('#1e272e')
ax_pie.set_facecolor("#1e272e")
canvas_pie = FigureCanvasTkAgg(fig_pie, master=graph_frame)
canvas_pie.get_tk_widget().pack(side="left", padx=20, pady=10)

cpu_history = collections.deque(maxlen=60)
fig_line, ax_line = plt.subplots(figsize=(5.5, 3), dpi=100)
fig_line.patch.set_facecolor('#1e272e')
canvas_line = FigureCanvasTkAgg(fig_line, master=graph_frame)
canvas_line.get_tk_widget().pack(side="right", padx=20, pady=10, fill='both', expand=True)

exit_button = tk.Button(dashboard_frame, text="🚪 Exit to Menu", font=("Segoe UI", 12),
                        bg="#d63031", fg="white", padx=20, pady=10, bd=0,
                        activebackground="#c0392b", activeforeground="white",
                        command=back_to_menu)
exit_button.pack(pady=(10, 20))

# ---------------------- Main Loop -------------------------
root.mainloop()
