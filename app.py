from flask import Flask, render_template, request, redirect, url_for
import uuid
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"

# Load existing data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save current data to file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=4)

# Start with saved events or empty
events = load_data()

def get_task_by_id(event_name, task_id):
    return next((task for task in events.get(event_name, []) if task["id"] == task_id), None)

@app.route("/", methods=["GET", "POST"])
def index():
    selected_event = request.args.get("event") or "Default Event"
    
    if selected_event not in events:
        events[selected_event] = []

    if request.method == "POST":
        task = {
            "id": str(uuid.uuid4()),
            "name": request.form.get("task_name"),
            "status": request.form.get("status"),
            "priority": request.form.get("priority"),
            "assigned_to": request.form.get("assigned_to"),
            "reason": request.form.get("reason"),
            "due_date": request.form.get("due_date"),
            "subtasks": []
        }
        events[selected_event].append(task)
        save_data()
        return redirect(url_for("index", event=selected_event))

    total_tasks = len(events[selected_event])
    done_tasks = sum(1 for task in events[selected_event] if task["status"] == "Done")
    progress = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template("index.html", 
                           tasks=events[selected_event], 
                           progress=progress, 
                           event_names=list(events.keys()), 
                           current_event=selected_event)

@app.route("/edit/<event>/<task_id>", methods=["POST"])
def edit(event, task_id):
    task = get_task_by_id(event, task_id)
    if task:
        task["status"] = request.form.get("status")
        task["priority"] = request.form.get("priority")
        task["assigned_to"] = request.form.get("assigned_to")
        task["reason"] = request.form.get("reason")
        task["due_date"] = request.form.get("due_date")
        save_data()
    return redirect(url_for("index", event=event))

@app.route("/delete/<event>/<task_id>", methods=["POST"])
def delete(event, task_id):
    events[event] = [task for task in events[event] if task["id"] != task_id]
    save_data()
    return redirect(url_for("index", event=event))

@app.route("/add_subtask/<event>/<task_id>", methods=["POST"])
def add_subtask(event, task_id):
    subtask_text = request.form.get("subtask")
    task = get_task_by_id(event, task_id)
    if task and subtask_text:
        task["subtasks"].append(subtask_text)
        save_data()
    return redirect(url_for("index", event=event))

@app.route("/add_event", methods=["POST"])
def add_event():
    new_event = request.form.get("new_event_name").strip()
    if new_event and new_event not in events:
        events[new_event] = []
        save_data()
    return redirect(url_for("index", event=new_event))

if __name__ == "__main__":
    app.run(debug=True)

