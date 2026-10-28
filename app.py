from datetime import datetime
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

CATEGORIES = [
    {"slug": "general", "name": "General", "icon": "✳"},
    {"slug": "technology", "name": "Technology", "icon": "⌘"},
    {"slug": "life", "name": "Life & style", "icon": "☀"},
    {"slug": "entertainment", "name": "Entertainment", "icon": "♫"},
    {"slug": "gaming", "name": "Gaming", "icon": "◈"},
    {"slug": "campus", "name": "Campus", "icon": "✎"},
]

DISCUSSIONS = [
    {
        "id": 1,
        "category": "general",
        "title": "What’s one small thing that made your week better?",
        "body": "Could be a good coffee, a kind stranger, or finally getting around to that thing you’ve been putting off. Share the little wins.",
        "author": "latecheckout",
        "avatar": "L",
        "color": "coral",
        "created": "2 min ago",
        "timestamp": 1730000600,
        "upvotes": 248,
        "comments": 84,
        "tag": "Community",
        "replies": [
            {"author": "slowmornings", "avatar": "S", "body": "My neighbor left a bag of mandarins at my door. Made my whole day.", "created": "1 min ago"},
            {"author": "paperplanes", "avatar": "P", "body": "Finally went for a run after putting it off all month. Feeling great.", "created": "just now"},
        ],
    },
    {
        "id": 2,
        "category": "technology",
        "title": "What are you building lately? Show us your side projects",
        "body": "Been working on a tiny weather app that only tells me if it’s a good day to sit outside. What are you making in your spare time?",
        "author": "pixelpusher",
        "avatar": "P",
        "color": "violet",
        "created": "8 min ago",
        "timestamp": 1730000300,
        "upvotes": 176,
        "comments": 52,
        "tag": "Show & tell",
        "replies": [],
    },
    {
        "id": 3,
        "category": "life",
        "title": "A reminder that you don’t have to have it all figured out",
        "body": "Some days, showing up is enough. Sharing this in case somebody else needed to hear it today.",
        "author": "somewherequiet",
        "avatar": "S",
        "color": "green",
        "created": "16 min ago",
        "timestamp": 1729999800,
        "upvotes": 391,
        "comments": 37,
        "tag": "Good thoughts",
        "replies": [],
    },
    {
        "id": 4,
        "category": "entertainment",
        "title": "The movie you can rewatch a hundred times and never get bored",
        "body": "Looking for something familiar for movie night. Mine is still Spirited Away — the details get me every time.",
        "author": "framebyframe",
        "avatar": "F",
        "color": "blue",
        "created": "24 min ago",
        "timestamp": 1729999300,
        "upvotes": 92,
        "comments": 108,
        "tag": "Conversation",
        "replies": [],
    },
    {
        "id": 5,
        "category": "gaming",
        "title": "Cozy game recommendations for a rainy weekend?",
        "body": "Looking for something low-stress to sink a few hours into. Bonus points if it has a great soundtrack.",
        "author": "savepoint",
        "avatar": "S",
        "color": "orange",
        "created": "31 min ago",
        "timestamp": 1729998800,
        "upvotes": 64,
        "comments": 43,
        "tag": "Recommendations",
        "replies": [],
    },
    {
        "id": 6,
        "category": "campus",
        "title": "Best quiet spots to study when the library is full?",
        "body": "Every table has been taken all week. Where do you go when you need a peaceful place to focus?",
        "author": "marginnote",
        "avatar": "M",
        "color": "teal",
        "created": "45 min ago",
        "timestamp": 1729998000,
        "upvotes": 38,
        "comments": 19,
        "tag": "Campus life",
        "replies": [],
    },
]

NEWS_ITEMS = [
    {
        "category": "Campus",
        "date": "October 24, 2026",
        "title": "Students turn the courtyard into a community garden",
        "summary": "A new student-led project is bringing fresh produce, greener spaces, and neighbors together on campus.",
        "read_time": "4 min read",
    },
    {
        "category": "Technology",
        "date": "October 21, 2026",
        "title": "The ideas helping make technology more accessible",
        "summary": "Local volunteers are sharing practical ways to make everyday digital tools easier for everyone to use.",
        "read_time": "6 min read",
    },
    {
        "category": "People",
        "date": "October 18, 2026",
        "title": "Meet the volunteers keeping the weekend club thriving",
        "summary": "For more than a decade, a small group of neighbors has made room for creativity, conversation, and new friendships.",
        "read_time": "3 min read",
    },
]


def get_category(slug):
    return next((category for category in CATEGORIES if category["slug"] == slug), None)


@app.get("/")
def home():
    selected_category = request.args.get("category", "all")
    sort_order = request.args.get("order", "now")
    search_query = request.args.get("q", "").strip()

    if selected_category != "all" and not get_category(selected_category):
        abort(404)
    if sort_order not in {"now", "hot", "top"}:
        sort_order = "now"

    discussions = list(DISCUSSIONS)
    if selected_category != "all":
        discussions = [post for post in discussions if post["category"] == selected_category]
    if search_query:
        query = search_query.casefold()
        discussions = [
            post for post in discussions
            if query in post["title"].casefold()
            or query in post["body"].casefold()
            or query in post["author"].casefold()
        ]

    if sort_order == "hot":
        discussions.sort(key=lambda post: post["upvotes"] + post["comments"] * 2, reverse=True)
    elif sort_order == "top":
        discussions.sort(key=lambda post: post["upvotes"], reverse=True)
    else:
        discussions.sort(key=lambda post: post["timestamp"], reverse=True)

    return render_template(
        "home.html",
        discussions=discussions,
        categories=CATEGORIES,
        selected_category=selected_category,
        sort_order=sort_order,
        search_query=search_query,
        category_names={category["slug"]: category["name"] for category in CATEGORIES},
    )


@app.get("/forum")
def forum():
    return home()


@app.route("/discussion/new", methods=["GET", "POST"])
def new_discussion():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        category = request.form.get("category", "general")
        raw_author = request.form.get("author", "").strip()
        author = raw_author[:30] if raw_author else "newneighbor"

        if not title or not body:
            error = "Add a title and a few details before posting."
        elif len(title) > 140 or len(body) > 2000:
            error = "Keep your title under 140 characters and your post under 2,000."
        elif not get_category(category):
            error = "Choose one of the listed discussion categories."
        else:
            # 修正 1：防止 DISCUSSIONS 為空時 max() 報錯
            post_id = max((post["id"] for post in DISCUSSIONS), default=0) + 1
            
            # 修正 2：確保 timestamp 格式與預設資料一致（轉為整數）
            DISCUSSIONS.insert(0, {
                "id": post_id,
                "category": category,
                "title": title,
                "body": body,
                "author": author,
                "avatar": author[0].upper(),
                "color": "teal",
                "created": "just now",
                "timestamp": int(datetime.now().timestamp()),
                "upvotes": 0,
                "comments": 0,
                "tag": "New discussion",
                "replies": [],
            })
            return redirect(url_for("home", category=category))
            
    return render_template("new_discussion.html", categories=CATEGORIES, error=error)


@app.route("/discussion/<int:discussion_id>", methods=["GET", "POST"])
def discussion_detail(discussion_id):
    post = next((item for item in DISCUSSIONS if item["id"] == discussion_id), None)
    if post is None:
        abort(404)
        
    error = None
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        raw_author = request.form.get("author", "").strip()
        author = raw_author[:30] if raw_author else "newneighbor"
        
        if not body:
            error = "Write a reply before posting."
        elif len(body) > 1000:
            error = "Keep your reply under 1,000 characters."
        else:
            post["replies"].append({
                "author": author,
                "avatar": author[0].upper(),
                "body": body,
                "created": "just now",
            })
            post["comments"] += 1
            return redirect(url_for("discussion_detail", discussion_id=discussion_id))
            
    return render_template(
        "discussion.html",
        discussion=post,
        category_name=get_category(post["category"])["name"],
        error=error,
    )


@app.get("/news")
def news():
    return render_template("news.html", news_items=NEWS_ITEMS)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = "Sign-in is not enabled for this demo." if request.method == "POST" else None
    return render_template("login.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)