from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey123"

def generate_summary(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    return ". ".join(sentences[:4]) + "." if sentences else "Add more detailed notes."

def golden_nugget(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    return max(sentences, key=len) if sentences else "Write more content."

def generate_quiz(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    quiz = []
    options_pool = [
        ["Important concept", "Unrelated fact", "Random statement", "Not useful"],
        ["Key principle", "Minor detail", "Wrong assumption", "Irrelevant point"],
        ["Core idea", "Side note", "Common mistake", "False claim"],
        ["Main topic", "Off-topic detail", "Incorrect fact", "Trivial point"],
        ["Central theme", "Background noise", "Misleading info", "Unrelated idea"],
    ]
    for i, s in enumerate(sentences[:5]):
        opts = options_pool[i % len(options_pool)]
        quiz.append({
            "question": f"What best describes: '{s[:80]}...'?" if len(s) > 80 else f"What is true about: '{s}'?",
            "options": opts,
            "answer": opts[0]
        })
    return quiz

def generate_flashcards(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    cards = []
    for s in sentences[:6]:
        words = s.split()
        if len(words) > 4:
            cards.append({"front": " ".join(words[:4]) + "...?", "back": s})
    return cards

def generate_timetable(subjects, exam_time_str):
    now = datetime.now()
    try:
        exam_time = datetime.strptime(exam_time_str, "%Y-%m-%dT%H:%M")
    except:
        return ["Invalid date format."]
    if (exam_time - now).total_seconds() <= 0:
        return ["Not enough time! Sleep and revise key points only!"]
    total_minutes = int((exam_time - now).total_seconds() / 60)
    block, break_time = 50, 10
    timetable, current, subject_index, day, sessions_today = [], now, 0, 1, 0
    while total_minutes > block:
        if sessions_today == 0:
            timetable.append(f"── Day {day} ({current.strftime('%A, %d %b')}) ──")
        end = current + timedelta(minutes=block)
        timetable.append(f"  {current.strftime('%H:%M')} - {end.strftime('%H:%M')} → 📖 {subjects[subject_index]}")
        current = end + timedelta(minutes=break_time)
        total_minutes -= (block + break_time)
        subject_index = (subject_index + 1) % len(subjects)
        sessions_today += 1
        if sessions_today >= 6:
            timetable.append("  😴 Rest for the day")
            current = (current + timedelta(days=1)).replace(hour=8, minute=0)
            day += 1
            sessions_today = 0
    timetable.append("🏁 Final revision & good sleep before exam!")
    return timetable

def music_match(text):
    text = text.lower()
    if "history" in text or "war" in text: return "epic"
    elif "math" in text or "calculus" in text: return "lofi"
    elif "code" in text or "programming" in text: return "deep"
    else: return "chill"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"]        = request.form["name"]
        session["email"]       = request.form.get("email", "")
        session["coins"]       = 0
        session["score"]       = 0
        session["weak_topics"] = []
        return redirect("/home")
    return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if "name" not in session:
        return redirect("/")
    summary = nugget = quiz = flashcards = timetable = music = message = None
    active_tab = "notes"

    if request.method == "POST":
        action = request.form.get("action")

        if action == "summary":
            summary = generate_summary(request.form["notes"])
            session["coins"] += 1
            active_tab = "notes"

        elif action == "nugget":
            nugget = golden_nugget(request.form["notes"])
            session["coins"] += 1
            active_tab = "notes"

        elif action == "quiz":
            quiz = generate_quiz(request.form["notes"])
            session["quiz_data"] = quiz
            active_tab = "quiz"

        elif action == "answer":
            selected, correct = request.form.get("selected"), request.form.get("correct")
            question = request.form.get("question", "")
            if selected == correct:
                session["coins"] += 2
                session["score"] += 1
                message = "correct"
            else:
                message = f"wrong::{correct}"
                weak = session.get("weak_topics", [])
                weak.append(question[:60])
                session["weak_topics"] = weak[-20:]
            quiz = session.get("quiz_data")
            active_tab = "quiz"

        elif action == "flashcards":
            flashcards = generate_flashcards(request.form["notes"])
            session["coins"] += 1
            active_tab = "flashcards"

        elif action == "timetable":
            subjects = [s for s in request.form.getlist("subjects") if s.strip()]
            timetable = generate_timetable(subjects, request.form["exam_time"])
            session["coins"] += 2
            active_tab = "timetable"

        elif action == "pick_music":
            music = request.form.get("genre", "lofi")
            active_tab = "music"

    return render_template("index.html",
        name=session["name"], coins=session.get("coins",0), score=session.get("score",0),
        weak_topics=session.get("weak_topics",[]),
        summary=summary, nugget=nugget, quiz=quiz, flashcards=flashcards,
        timetable=timetable, music=music, message=message, active_tab=active_tab)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)