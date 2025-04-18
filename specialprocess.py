import streamlit as st
import psutil
import matplotlib.pyplot as plt
import collections
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="System Monitor Dashboard")

# Theme toggling
theme = st.sidebar.radio("Choose Theme", ["Dark", "Light"])
if theme == "Dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #1e272e;
            color: white;
            background-image: linear-gradient(to right top, #1e272e, #2c3e50);
        }
        .stButton>button {
            background-color: #48dbfb;
            color: black;
            font-weight: bold;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: white;
            color: black;
        }
        .stButton>button {
            background-color: #0984e3;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("💻 Task Manager Dashboard")
st.subheader("Monitor, analyze and optimize your system in real time.")

# Sidebar options
view_type = st.sidebar.radio("Choose View", ["Dashboard", "Processes", "Graphs"])
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)

if "cpu_vals" not in st.session_state:
    st.session_state.cpu_vals = collections.deque([0]*60, maxlen=60)

def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return cpu_percent, mem, disk

def get_process_data():
    data = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_info().rss / (1024 * 1024)
            name = proc.info['name']
            if name.lower() not in ["system idle process", "system"]:
                data.append((proc.pid, name, cpu, mem))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    df = pd.DataFrame(data, columns=["PID", "Process", "CPU (%)", "Memory (MB)"])
    df = df.sort_values("CPU (%)", ascending=False)
    return df

def draw_pie(mem):
    labels = ["Used", "Available"]
    sizes = [mem.used, mem.available]
    colors = ["#ff6b6b", "#48dbfb"]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("Memory Usage")
    st.pyplot(fig)

def draw_cpu_line(cpu_history):
    fig, ax = plt.subplots()
    ax.plot(cpu_history, color="#00cec9", linewidth=2)
    ax.set_ylim(0, 100)
    ax.set_title("CPU Usage Over Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("CPU %")
    st.pyplot(fig)

def draw_disk_chart(disk):
    labels = ["Used", "Free"]
    sizes = [disk.used, disk.free]
    colors = ["#e17055", "#55efc4"]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("Disk Usage")
    st.pyplot(fig)

placeholder = st.empty()

while True:
    with placeholder.container():
        cpu, mem, disk = get_system_stats()
        st.session_state.cpu_vals.append(cpu)

        if view_type == "Dashboard":
            col1, col2, col3 = st.columns(3)
            col1.metric("CPU Usage", f"{cpu:.1f}%")
            col2.metric("Memory Usage", f"{mem.used / (1024 ** 2):.1f} MB / {mem.total / (1024 ** 2):.1f} MB")
            col3.metric("Disk Usage", f"{disk.used / (1024 ** 3):.1f} GB / {disk.total / (1024 ** 3):.1f} GB")

            st.divider()
            st.subheader("Top Processes")

            df = get_process_data()
            selected_pid = st.selectbox("Select PID to kill", df["PID"])
            if st.button("❌ Kill Process"):
                try:
                    p = psutil.Process(selected_pid)
                    p.terminate()
                    st.success(f"Process {selected_pid} terminated.")
                except Exception as e:
                    st.error(f"Failed to kill process: {e}")

            st.dataframe(df, use_container_width=True)

            st.subheader("Usage Charts")
            col1, col2, col3 = st.columns(3)
            with col1:
                draw_pie(mem)
            with col2:
                draw_cpu_line(st.session_state.cpu_vals)
            with col3:
                draw_disk_chart(disk)

        elif view_type == "Processes":
            df = get_process_data()
            st.subheader("Running Processes")
            selected_pid = st.selectbox("Select PID to kill", df["PID"])
            if st.button("❌ Kill Process"):
                try:
                    p = psutil.Process(selected_pid)
                    p.terminate()
                    st.success(f"Process {selected_pid} terminated.")
                except Exception as e:
                    st.error(f"Failed to kill process: {e}")
            st.dataframe(df, use_container_width=True)

        elif view_type == "Graphs":
            cpu, mem, disk = get_system_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                draw_pie(mem)
            with col2:
                draw_cpu_line(st.session_state.cpu_vals)
            with col3:
                draw_disk_chart(disk)

    if not auto_refresh:
        break
    time.sleep(refresh_rate)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Created")
