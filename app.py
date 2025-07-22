from flask import Flask, render_template, request, redirect, url_for
import uuid

app = Flask(__name__)

tasks = []

def get_task_by_id(task_id):
    return next((task for task in tasks if task["id"] == task_id), None)

@app.route("/", methods=["GET", "POST"])
def index():
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
        tasks.append(task)
        return redirect(url_for("index"))

    total_tasks = len(tasks)
    done_tasks = sum(1 for task in tasks if task["status"] == "Done")
    progress = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template("index.html", tasks=tasks, progress=progress)

@app.route("/edit/<task_id>", methods=["POST"])
def edit(task_id):
    task = get_task_by_id(task_id)
    if task:
        task["status"] = request.form.get("status")
        task["priority"] = request.form.get("priority")
        task["assigned_to"] = request.form.get("assigned_to")
        task["reason"] = request.form.get("reason")
        task["due_date"] = request.form.get("due_date")
    return redirect(url_for("index"))

@app.route("/delete/<task_id>", methods=["POST"])
def delete(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return redirect(url_for("index"))

@app.route("/add_subtask/<task_id>", methods=["POST"])
def add_subtask(task_id):
    subtask_text = request.form.get("subtask")
    task = get_task_by_id(task_id)
    if task and subtask_text:
        task["subtasks"].append(subtask_text)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
