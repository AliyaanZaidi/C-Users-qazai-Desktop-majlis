from flask import Flask, render_template, request, redirect, url_for
import uuid

app = Flask(__name__)

tasks = []

def get_task_by_id(task_id):
    return next((task for task in tasks if task["id"] == task_id), None)

@app.route("/", methods=["GET", "POST"])
def index():
    # Gather unique events from tasks
    events = sorted({task["event"] for task in tasks if task.get("event")})

    # If no events yet, default to empty string (so dropdown empty)
    selected_event = request.args.get("event", events[0] if events else "")

    if request.method == "POST":
        task = {
            "id": str(uuid.uuid4()),
            "event": request.form.get("event"),
            "name": request.form.get("task_name"),
            "status": request.form.get("status"),
            "priority": request.form.get("priority"),
            "assigned_to": request.form.get("assigned_to"),
            "reason": request.form.get("reason"),
            "due_date": request.form.get("due_date"),
            "subtasks": []
        }
        tasks.append(task)
        return redirect(url_for("index", event=task["event"]))

    # Filter tasks by selected event
    event_tasks = [t for t in tasks if t.get("event") == selected_event]
    total_tasks = len(event_tasks)
    done_tasks = sum(1 for task in event_tasks if task["status"] == "Done")
    progress = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template("index.html", tasks=event_tasks, progress=progress, events=events, selected_event=selected_event)

@app.route("/edit/<task_id>", methods=["POST"])
def edit(task_id):
    task = get_task_by_id(task_id)
    if task:
        task["status"] = request.form.get("status")
        task["priority"] = request.form.get("priority")
        task["assigned_to"] = request.form.get("assigned_to")
        task["reason"] = request.form.get("reason")
        task["due_date"] = request.form.get("due_date")
    return redirect(url_for("index", event=task["event"] if task else ""))

@app.route("/delete/<task_id>", methods=["POST"])
def delete(task_id):
    global tasks
    task = get_task_by_id(task_id)
    if task:
        tasks = [t for t in tasks if t["id"] != task_id]
        return redirect(url_for("index", event=task["event"]))
    return redirect(url_for("index"))

@app.route("/add_subtask/<task_id>", methods=["POST"])
def add_subtask(task_id):
    subtask_text = request.form.get("subtask")
    task = get_task_by_id(task_id)
    if task and subtask_text:
        task["subtasks"].append(subtask_text)
    return redirect(url_for("index", event=task["event"]))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
