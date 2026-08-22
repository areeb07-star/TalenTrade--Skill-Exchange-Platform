from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os, random, string

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///talentrade.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------ CAPTCHA Functions ------------------
def generate_captcha():
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choice(chars) for _ in range(6))

# ------------------ Models ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    teach_skills = db.Column(db.String(300), default="")
    learn_skills = db.Column(db.String(300), default="")

    streak_count = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, nullable=True)

    def set_password(self, p):
        self.password_hash = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

    def teach_list(self):
        raw = [s.strip() for s in self.teach_skills.split(",") if s.strip()]
        return sorted({s.title() for s in raw})

    def learn_list(self):
        raw = [s.strip() for s in self.learn_skills.split(",") if s.strip()]
        return sorted({s.title() for s in raw})

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(120), index=True)
    sender = db.Column(db.String(80))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------ Sample Data ------------------
ALL_SKILLS = [
    "Python","Java","C++","HTML","CSS","JavaScript","React","Node.js",
    "Data Science","Machine Learning","Public Speaking","Cooking",
    "Graphic Design","Video Editing","Photography","Excel",
    "UI/UX Design","Singing","Guitar","Dancing","Finance Basics",
    "Digital Marketing","SEO","Content Writing","3D Modeling",
    "Artificial Intelligence","Deep Learning","Cloud Computing",
    "Cybersecurity","SQL","MongoDB","Blockchain","DevOps",
    "App Development","Game Development","AR/VR Development",
    "Networking Basics","Linux","Software Testing",
    "Mathematics","Statistics","Problem Solving","Leadership",
    "Time Management","Critical Thinking","Teamwork","Negotiation",
    "Project Management","Entrepreneurship","Business Strategy",
    "Accounting","Data Analysis","Research Skills","Writing Skills",
    "Creative Writing","Blogging","Podcasting","Voice Acting",
    "Drawing","Painting","Calligraphy","Crafting","Animation",
    "Music Production","Piano","Drums","Chess","Sports Coaching",
    "Yoga","Meditation","First Aid","Event Management",
    "Language Learning","Spanish","French","German","Japanese",
    "Public Relations","Advertising","Sales Skills","Customer Service",
    "Teaching","Mentoring","Volunteering","baking","arts"
]

skill_links = {
    "Python": {
        "youtube": "https://www.youtube.com/results?search_query=python+tutorial",
        "course": "https://www.coursera.org/courses?query=python",
        "other": "https://www.w3schools.com/python/"
    },
    "Java": {
        "youtube": "https://www.youtube.com/results?search_query=java+tutorial",
        "course": "https://www.coursera.org/courses?query=java",
        "other": "https://www.w3schools.com/java/"
    },
    "C++": {
        "youtube": "https://www.youtube.com/results?search_query=c%2B%2B+tutorial",
        "course": "https://www.coursera.org/courses?query=c%2B%2B",
        "other": "https://www.w3schools.com/cpp/"
    },
    "C": {
        "youtube": "https://www.youtube.com/results?search_query=c+programming+tutorial",
        "course": "https://www.coursera.org/courses?query=c%20programming",
        "other": "https://www.learn-c.org/"
    },
    "HTML": {
        "youtube": "https://www.youtube.com/results?search_query=html+tutorial",
        "course": "https://www.coursera.org/courses?query=html",
        "other": "https://www.w3schools.com/html/"
    },
    "CSS": {
        "youtube": "https://www.youtube.com/results?search_query=css+tutorial",
        "course": "https://www.coursera.org/courses?query=css",
        "other": "https://www.w3schools.com/css/"
    },
    "JavaScript": {
        "youtube": "https://www.youtube.com/results?search_query=javascript+tutorial",
        "course": "https://www.coursera.org/courses?query=javascript",
        "other": "https://www.w3schools.com/js/"
    },
    "React": {
        "youtube": "https://www.youtube.com/results?search_query=react+tutorial",
        "course": "https://www.coursera.org/courses?query=react",
        "other": "https://react.dev/"
    },
    "Node.js": {
        "youtube": "https://www.youtube.com/results?search_query=node+js+tutorial",
        "course": "https://www.coursera.org/courses?query=nodejs",
        "other": "https://nodejs.org/en/docs/"
    },
    "Express.js": {
        "youtube": "https://www.youtube.com/results?search_query=express+js+tutorial",
        "course": "https://www.udemy.com/topic/expressjs/",
        "other": "https://expressjs.com/"
    },
    "Angular": {
        "youtube": "https://www.youtube.com/results?search_query=angular+tutorial",
        "course": "https://www.coursera.org/courses?query=angular",
        "other": "https://angular.io/"
    },
    "SQL": {
        "youtube": "https://www.youtube.com/results?search_query=sql+tutorial",
        "course": "https://www.coursera.org/courses?query=sql",
        "other": "https://www.w3schools.com/sql/"
    },
    "MongoDB": {
        "youtube": "https://www.youtube.com/results?search_query=mongodb+tutorial",
        "course": "https://university.mongodb.com/",
        "other": "https://www.mongodb.com/docs/"
    },
    "Firebase": {
        "youtube": "https://www.youtube.com/results?search_query=firebase+tutorial",
        "course": "https://www.udemy.com/topic/firebase/",
        "other": "https://firebase.google.com/docs"
    },
    "Data Science": {
        "youtube": "https://www.youtube.com/results?search_query=data+science+tutorial",
        "course": "https://www.coursera.org/specializations/data-science",
        "other": "https://www.kaggle.com/learn"
    },
    "Machine Learning": {
        "youtube": "https://www.youtube.com/results?search_query=machine+learning+tutorial",
        "course": "https://www.coursera.org/learn/machine-learning",
        "other": "https://scikit-learn.org/stable/"
    },
    "Artificial Intelligence": {
        "youtube": "https://www.youtube.com/results?search_query=artificial+intelligence+tutorial",
        "course": "https://www.coursera.org/specializations/artificial-intelligence",
        "other": "https://ai.google/education/"
    },
    "Deep Learning": {
        "youtube": "https://www.youtube.com/results?search_query=deep+learning+tutorial",
        "course": "https://www.coursera.org/specializations/deep-learning",
        "other": "https://www.deeplearning.ai/"
    },
    "Cloud Computing": {
        "youtube": "https://www.youtube.com/results?search_query=cloud+computing+tutorial",
        "course": "https://www.coursera.org/courses?query=cloud+computing",
        "other": "https://aws.amazon.com/what-is-cloud-computing/"
    },
    "AWS": {
        "youtube": "https://www.youtube.com/results?search_query=aws+tutorial",
        "course": "https://www.coursera.org/courses?query=aws",
        "other": "https://aws.amazon.com/getting-started/"
    },
    "Cybersecurity": {
        "youtube": "https://www.youtube.com/results?search_query=cybersecurity+tutorial",
        "course": "https://www.coursera.org/specializations/cyber-security",
        "other": "https://www.cisa.gov/"
    },
    "Ethical Hacking": {
        "youtube": "https://www.youtube.com/results?search_query=ethical+hacking+tutorial",
        "course": "https://www.udemy.com/topic/ethical-hacking/",
        "other": "https://www.kali.org/"
    },
    "Networking": {
        "youtube": "https://www.youtube.com/results?search_query=computer+networking+tutorial",
        "course": "https://www.coursera.org/courses?query=networking",
        "other": "https://www.geeksforgeeks.org/computer-network-tutorials/"
    },
    "Operating Systems": {
        "youtube": "https://www.youtube.com/results?search_query=operating+system+tutorial",
        "course": "https://www.coursera.org/courses?query=operating%20system",
        "other": "https://www.geeksforgeeks.org/operating-systems/"
    },
    "DSA": {
        "youtube": "https://www.youtube.com/results?search_query=dsa+tutorial",
        "course": "https://www.coursera.org/courses?query=data%20structures%20algorithms",
        "other": "https://www.geeksforgeeks.org/data-structures/"
    },
    "Blockchain": {
        "youtube": "https://www.youtube.com/results?search_query=blockchain+tutorial",
        "course": "https://www.coursera.org/courses?query=blockchain",
        "other": "https://www.ibm.com/topics/what-is-blockchain"
    },
    "DevOps": {
        "youtube": "https://www.youtube.com/results?search_query=devops+tutorial",
        "course": "https://www.coursera.org/specializations/devops",
        "other": "https://azure.microsoft.com/en-in/resources/cloud-computing-dictionary/what-is-devops"
    },
    "UI/UX Design": {
        "youtube": "https://www.youtube.com/results?search_query=ui+ux+design+tutorial",
        "course": "https://www.coursera.org/courses?query=ui%20ux%20design",
        "other": "https://www.interaction-design.org/literature/topics/ux-design"
    },
    "Graphic Design": {
        "youtube": "https://www.youtube.com/results?search_query=graphic+design+tutorial",
        "course": "https://www.coursera.org/courses?query=graphic%20design",
        "other": "https://www.canva.com/learn/graphic-design/"
    },
    "Video Editing": {
        "youtube": "https://www.youtube.com/results?search_query=video+editing+tutorial",
        "course": "https://www.udemy.com/topic/video-editing/",
        "other": "https://helpx.adobe.com/premiere-pro/tutorials.html"
    },
    "Photography": {
        "youtube": "https://www.youtube.com/results?search_query=photography+tutorial",
        "course": "https://www.coursera.org/courses?query=photography",
        "other": "https://photographylife.com/"
    },
    "Excel": {
        "youtube": "https://www.youtube.com/results?search_query=excel+tutorial",
        "course": "https://www.coursera.org/courses?query=excel",
        "other": "https://www.excel-easy.com/"
    },
    "Finance Basics": {
        "youtube": "https://www.youtube.com/results?search_query=finance+basics+tutorial",
        "course": "https://www.coursera.org/courses?query=finance",
        "other": "https://www.investopedia.com/"
    },
    "Public Speaking": {
        "youtube": "https://www.youtube.com/results?search_query=public+speaking+tutorial",
        "course": "https://www.coursera.org/courses?query=public%20speaking",
        "other": "https://www.toastmasters.org/"
    },
    "Content Writing": {
        "youtube": "https://www.youtube.com/results?search_query=content+writing+tutorial",
        "course": "https://www.udemy.com/topic/content-writing/",
        "other": "https://www.grammarly.com/blog/"
    },
    "Digital Marketing": {
        "youtube": "https://www.youtube.com/results?search_query=digital+marketing+tutorial",
        "course": "https://www.coursera.org/specializations/digital-marketing",
        "other": "https://mailchimp.com/marketing-glossary/digital-marketing/"
    },
    "SEO": {
        "youtube": "https://www.youtube.com/results?search_query=seo+tutorial",
        "course": "https://www.coursera.org/courses?query=seo",
        "other": "https://moz.com/learn/seo/what-is-seo"
    },
    "3D Modeling": {
        "youtube": "https://www.youtube.com/results?search_query=3d+modeling+tutorial",
        "course": "https://www.udemy.com/topic/3d-modeling/",
        "other": "https://www.blender.org/"
    },
    "Singing": {
        "youtube": "https://www.youtube.com/results?search_query=singing+tutorial",
        "course": "https://www.udemy.com/topic/singing/",
        "other": "https://takelessons.com/"
    },
    "Guitar": {
        "youtube": "https://www.youtube.com/results?search_query=guitar+tutorial",
        "course": "https://www.udemy.com/topic/guitar/",
        "other": "https://www.justinguitar.com/"
    },
    "Dancing": {
        "youtube": "https://www.youtube.com/results?search_query=dance+tutorial",
        "course": "https://www.udemy.com/topic/dance/",
        "other": "https://www.steezy.co/"
    },
     "Cooking": {
        "youtube": "https://www.youtube.com/playlist?list=PL8dDSKArO2-mwRx_wGeUZ6zZ5p1nY4t2N",
        "course": "https://www.udemy.com/course/cooking-class/",
        "other": "https://www.allrecipes.com/"
    },
    "Baking": {
        "youtube": "https://www.youtube.com/playlist?list=PLhhv1n2Z7JgUbdXyW6N7K0y-MG8L4Y_LQ",
        "course": "https://www.udemy.com/course/baking-for-beginners/",
        "other": "https://sallysbakingaddiction.com/"
    }
}

# ------------------ Helpers ------------------
def normalize_skill(s: str) -> str:
    return (s or "").strip().title()

def current_user():
    uid = session.get("uid")
    if uid:
        return User.query.get(uid)
    return None

def update_streak(user: User):
    today = date.today()
    if not user.last_active:
        user.streak_count = 1
        user.last_active = today
    else:
        delta = (today - user.last_active).days
        if delta == 1:
            user.streak_count += 1
            user.last_active = today
        elif delta > 1:
            user.streak_count = 1
            user.last_active = today
    db.session.commit()

def badge_list(user: User):
    badges = []
    if user.streak_count >= 3: badges.append("Streak Starter")
    if user.streak_count >= 7: badges.append("Weekly Warrior")
    if user.streak_count >= 14: badges.append("Consistency King/Queen")
    if len(user.teach_list()) >= 1: badges.append("Mentor")
    if len(user.learn_list()) >= 1: badges.append("Explorer")
    if len(user.teach_list()) >= 3: badges.append("Skill Maestro")
    return badges

def random_room_for_pair(a, b):
    names = "-".join(sorted([a, b]))
    return "TT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6)) + "-" + names

# ------------------ Routes ------------------
MOTTOS = {
    "home": "Swap Skills. Build Friendships. Grow Together.",
    "login": "Welcome back—your next skill awaits.",
    "signup": "Every skill shared is a step forward.",
    "profile": "Track your growth. Earn your badges.",
    "skills": "Add skills. Unlock opportunities.",
    "receiver": "Tell us what you want to learn.",
    "match": "Find the right partner to learn or teach.",
    "help": "Need guidance? We're here to help.",
    "chat": "Say hi—learning starts with a hello."
}

@app.route("/")
def index():
    return render_template("index.html", motto=MOTTOS["home"])

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        captcha = generate_captcha()
        session['captcha'] = captcha
        return render_template("login.html", motto=MOTTOS["login"], captcha=captcha, error=None)
    
    elif request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user_captcha = request.form.get("captcha_input")
        
        session_captcha = session.get('captcha', '')
        
        if not user_captcha or user_captcha.upper() != session_captcha.upper():
            new_captcha = generate_captcha()
            session['captcha'] = new_captcha
            return render_template("login.html", motto=MOTTOS["login"], 
                                 captcha=new_captcha, 
                                 error="Invalid CAPTCHA. Please try again.")
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["uid"] = user.id
            update_streak(user)
            session['captcha'] = generate_captcha()
            return redirect(url_for("profile"))
        
        new_captcha = generate_captcha()
        session['captcha'] = new_captcha
        return render_template("login.html", motto=MOTTOS["login"], 
                             captcha=new_captcha, 
                             error="Invalid username or password.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email = request.form.get("email","").strip()
        password = request.form.get("password","")
        if not username or not email or not password:
            return render_template("signup.html", motto=MOTTOS["signup"], error="All fields required")
        if User.query.filter((User.username==username)|(User.email==email)).first():
            return render_template("signup.html", motto=MOTTOS["signup"], error="User already exists")
        u = User(username=username, email=email)
        u.set_password(password)
        db.session.add(u); db.session.commit()
        session["uid"] = u.id
        update_streak(u)
        return redirect(url_for("profile"))
    return render_template("signup.html", motto=MOTTOS["signup"])

@app.route("/profile")
def profile():
    user = current_user()
    if not user: return redirect(url_for("login"))
    badges = badge_list(user)
    return render_template("profile.html", user=user, badges=badges, motto=MOTTOS["profile"],
                           teach_skills=user.teach_list(), learn_skills=user.learn_list())

@app.route("/register_skill", methods=["GET","POST"])
def register_skill():
    user = current_user()
    if not user: return redirect(url_for("login"))
    if request.method == "POST":
        teach = normalize_skill(request.form.get("teach",""))
        learn = normalize_skill(request.form.get("learn",""))

        if teach:
            cur = {normalize_skill(s) for s in user.teach_list()}
            cur.add(teach)
            user.teach_skills = ", ".join(sorted(cur))
        if learn:
            cur = {normalize_skill(s) for s in user.learn_list()}
            cur.add(learn)
            user.learn_skills = ", ".join(sorted(cur))

        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("register_skill.html", user=user, motto=MOTTOS["skills"])

@app.route("/receiver", methods=["GET","POST"])
def receiver():
    user = current_user()
    if not user: return redirect(url_for("login"))
    if request.method == "POST":
        learn = normalize_skill(request.form.get("learn",""))
        if learn:
            cur = {normalize_skill(s) for s in user.learn_list()}
            cur.add(learn)
            user.learn_skills = ", ".join(sorted(cur))
            db.session.commit()
            return redirect(url_for("match"))
    return render_template("register_receiver.html", user=user, motto=MOTTOS["receiver"])

@app.route("/delete_skill", methods=["POST"])
def delete_skill():
    user = current_user()
    if not user: return redirect(url_for("login"))

    skill = normalize_skill(request.form.get("skill",""))
    skill_type = (request.form.get("type","") or "").strip().lower()

    if not skill or skill_type not in {"teach","learn"}:
        return redirect(url_for("profile"))

    if skill_type == "teach":
        cur = {normalize_skill(s) for s in user.teach_list()}
        if skill in cur:
            cur.remove(skill)
            user.teach_skills = ", ".join(sorted(cur))
    else:
        cur = {normalize_skill(s) for s in user.learn_list()}
        if skill in cur:
            cur.remove(skill)
            user.learn_skills = ", ".join(sorted(cur))

    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/delete_skill/<skill_type>/<skill_name>", methods=["POST"])
def delete_skill_by_url(skill_type, skill_name):
    user = current_user()
    if not user: return redirect(url_for("login"))

    skill = normalize_skill(skill_name)
    skill_type = (skill_type or "").strip().lower()

    if skill_type == "teach":
        cur = {normalize_skill(s) for s in user.teach_list()}
        if skill in cur:
            cur.remove(skill)
            user.teach_skills = ", ".join(sorted(cur))
    elif skill_type == "learn":
        cur = {normalize_skill(s) for s in user.learn_list()}
        if skill in cur:
            cur.remove(skill)
            user.learn_skills = ", ".join(sorted(cur))

    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/match")
def match():
    user = current_user()
    if not user: return redirect(url_for("login"))

    teach = set(user.teach_list())
    learn = set(user.learn_list())

    candidates = User.query.filter(User.id != user.id).all()
    results = []

    for c in candidates:
        c_teach = set(c.teach_list())
        c_learn = set(c.learn_list())

        learn_match = learn & c_teach if learn else set()
        teach_match = teach & c_learn if teach else set()
        swap_match = (teach & c_learn) | (learn & c_teach)

        if learn_match or teach_match:
            results.append({
                "username": c.username,
                "teach_for_you": sorted(list(learn_match)),
                "learn_from_you": sorted(list(teach_match)),
                "swap_overlap": sorted(list(swap_match))
            })
    return render_template("matchmaking.html", user=user, matches=results, motto=MOTTOS["match"],skill_links=skill_links)

@app.route("/help")
def help_page():
    return render_template("help.html", motto=MOTTOS["help"])

@app.route("/search_skill")
def search_skill():
    q = (request.args.get("q") or "").lower().strip()
    if not q:
        return jsonify([])
    db_skills = set()
    for u in User.query.all():
        db_skills.update(u.teach_list())
        db_skills.update(u.learn_list())
    pool = set(ALL_SKILLS) | db_skills
    results = [s for s in sorted(pool) if q in s.lower()][:10]
    return jsonify(results)

@app.route("/refresh-captcha", methods=["GET"])
def refresh_captcha():
    new_captcha = generate_captcha()
    session['captcha'] = new_captcha
    return jsonify({'captcha': new_captcha})
@app.route('/socket.io/socket.io.js')
def socketio_js():
    from flask import send_from_directory
    import os
    return send_from_directory(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
        'socket.io.min.js'
    )

# ---------- CHAT ROUTES ----------
# ===== SIMPLE CHAT ROUTES (NO SOCKET.IO) =====
def random_room_for_pair(a, b):
    # Always return the SAME room for the same pair
    names = "-".join(sorted([a, b]))
    return "TT-" + names

# ---------- CHAT ROUTES ----------
@app.route("/chat/<peer_username>")
def chat(peer_username):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    
    # Both users get the SAME room name
    room = random_room_for_pair(user.username, peer_username)
    history = Message.query.filter_by(room=room).order_by(Message.timestamp.asc()).limit(50).all()
    
    return render_template("chat.html", 
                         room=room, 
                         peer=peer_username, 
                         history=history, 
                         motto=MOTTOS["chat"],
                         user=user)

@app.route('/get_chat_messages')
def get_chat_messages():
    room = request.args.get('room')
    if not room:
        return jsonify({'messages': []})
    
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp.asc()).all()
    
    return jsonify({
        'messages': [{
            'sender': m.sender,
            'text': m.text,
            'time': m.timestamp.strftime('%H:%M') if m.timestamp else ''
        } for m in messages]
    })

@app.route('/send_chat_message', methods=['POST'])
def send_chat_message():
    data = request.get_json()
    room = data.get('room')
    sender = data.get('sender')
    text = data.get('text')
    
    if not room or not sender or not text:
        return jsonify({'success': False, 'error': 'Missing fields'})
    
    msg = Message(room=room, sender=sender, text=text)
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({'success': True})
# ===== TYPING INDICATOR =====
typing_status_store = {}  # Store typing status {room: username}

@app.route('/typing_status', methods=['POST'])
def update_typing_status():
    data = request.get_json()
    room = data.get('room')
    user = data.get('user')
    typing = data.get('typing', False)
    
    if typing:
        typing_status_store[room] = user
    else:
        if room in typing_status_store and typing_status_store[room] == user:
            del typing_status_store[room]
    
    return jsonify({'success': True})

@app.route('/get_typing_status')
def get_typing_status():
    room = request.args.get('room')
    typing_user = typing_status_store.get(room)
    return jsonify({'typing_user': typing_user})
# ===== ONLINE STATUS =====
online_users = {}  # Store online users {username: last_active_timestamp}

@app.route('/update_online', methods=['POST'])
def update_online():
    data = request.get_json()
    user = data.get('user')
    if user:
        online_users[user] = datetime.now()
    return jsonify({'success': True})

@app.route('/check_online')
def check_online():
    user = request.args.get('user')
    if not user:
        return jsonify({'online': False})
    
    # Check if user is online (active within last 10 seconds)
    last_active = online_users.get(user)
    if last_active:
        time_diff = (datetime.now() - last_active).total_seconds()
        is_online = time_diff < 10
    else:
        is_online = False
    
    return jsonify({'online': is_online})

# ===== READ RECEIPTS =====
read_status = {}  # Store read status {room: last_read_message_id}

@app.route('/mark_as_read', methods=['POST'])
def mark_as_read():
    data = request.get_json()
    room = data.get('room')
    user = data.get('user')
    
    if room and user:
        # Get the last message ID in this room
        last_msg = Message.query.filter_by(room=room).order_by(Message.id.desc()).first()
        if last_msg:
            read_status[f"{room}_{user}"] = last_msg.id
    
    return jsonify({'success': True})

@app.route('/get_read_status')
def get_read_status():
    room = request.args.get('room')
    user = request.args.get('user')
    
    if room and user:
        read_id = read_status.get(f"{room}_{user}", 0)
        return jsonify({'last_read': read_id})
    
    return jsonify({'last_read': 0})

# ---------- Setup / seed ----------
def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="alice").first():
            a = User(username="alice", email="alice@example.com")
            a.set_password("alice123")
            a.teach_skills = "Graphic Design, Public Speaking"
            a.learn_skills = "Python, Data Science"
            db.session.add(a)

        if not User.query.filter_by(username="bob").first():
            b = User(username="bob", email="bob@example.com")
            b.set_password("bob123")
            b.teach_skills = "Python, Data Science"
            b.learn_skills = "Public Speaking"
            db.session.add(b)

        if not User.query.filter_by(username="charlie").first():
            c = User(username="charlie", email="charlie@example.com")
            c.set_password("charlie123")
            c.teach_skills = "Guitar, Singing"
            c.learn_skills = "Video Editing, Photography"
            db.session.add(c)

        db.session.commit()
        print("[SUCCESS] Database initialized and default users seeded (if missing).")
if __name__ == "__main__":
    init_db()
    print("\n[INFO] TalentTrade is running!")
    print(" Open your browser at: http://127.0.0.1:5001/\n")
app.run(debug=True, host="0.0.0.0", port=5001)