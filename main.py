import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Smart Student Dashboard", layout="wide")
st.title("🎓 Smart Student Productivity Dashboard")

DATA = "data"
os.makedirs(DATA, exist_ok=True)

attendance_file = f"{DATA}/attendance.csv"
expenses_file = f"{DATA}/expenses.csv"
tasks_file = f"{DATA}/tasks.csv"
budget_file = f"{DATA}/budget.txt"


# -------- LOAD DATA --------
def load(path):
    return pd.read_csv(path) if os.path.exists(path) else None

attendance = load(attendance_file)
expenses = load(expenses_file)
tasks = load(tasks_file)


# -------- BUDGET --------
budget = int(open(budget_file).read()) if os.path.exists(budget_file) else 1000
budget = st.sidebar.number_input("Monthly Budget", 100, value=budget, step=100)
open(budget_file, "w").write(str(budget))


tabs = st.tabs(["🚀 Productivity", "💰 Expenses", "✅ Tasks","📅 Attendance"])


# -------- PRODUCTIVITY --------
with tabs[0]:

    if all(x is not None for x in [attendance, expenses, tasks]):

        attendance["Attendance %"] = attendance["Attended"] / attendance["TotalClasses"] * 100

        task_rate = tasks["Completed"].mean() * 100
        avg_att = attendance["Attendance %"].mean()
        spend = expenses["Amount"].sum()

        score = task_rate*0.5 + avg_att*0.3 + max(0,100-spend/budget*100)*0.2

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Task Completion", f"{task_rate:.1f}%")
        c2.metric("Avg Attendance", f"{avg_att:.1f}%")
        c3.metric("Expenses", f"${spend}")
        c4.metric("Productivity", f"{score:.1f}/100")

        st.progress(int(score))


# -------- ATTENDANCE --------
with tabs[3]:

    if attendance is not None:

        attendance["Attendance %"] = attendance["Attended"] / attendance["TotalClasses"] * 100

        st.dataframe(attendance)

        fig, ax = plt.subplots()
        colors = ["green" if x>=75 else "red" for x in attendance["Attendance %"]]

        ax.bar(attendance["Subject"], attendance["Attendance %"], color=colors)
        ax.axhline(75, linestyle="--")
        ax.set_ylim(0,100)

        plt.xticks(rotation=45)
        st.pyplot(fig)


# -------- EXPENSES --------
with tabs[1]:

    if expenses is not None:

        st.subheader("Add Expense")

        category = st.selectbox("Category", sorted(expenses["Category"].unique()))
        amount = st.number_input("Amount", min_value=0)

        if st.button("Add Expense"):
            expenses.loc[len(expenses)] = [pd.Timestamp.today(), category, amount]
            expenses.to_csv(expenses_file, index=False)
            st.success("Expense added")

        summary = expenses.groupby("Category")["Amount"].sum().reset_index()

        st.subheader("Category Spending")
        st.dataframe(summary)

        fig, ax = plt.subplots()
        ax.pie(summary["Amount"], labels=summary["Category"], autopct="%1.1f%%")
        st.pyplot(fig)


# -------- TASKS --------
with tabs[2]:

    if tasks is not None:

        st.subheader("Task List")

        updated = [1 if st.checkbox(t["Task"], bool(t["Completed"]), key=i) else 0
                   for i,t in tasks.iterrows()]

        if st.button("Save Tasks"):
            tasks["Completed"] = updated
            tasks.to_csv(tasks_file, index=False)
            st.success("Tasks saved")

        new_task = st.text_input("New Task")

        if st.button("Add Task") and new_task:
            tasks.loc[len(tasks)] = [new_task,0]
            tasks.to_csv(tasks_file,index=False)
            st.success("Task added")