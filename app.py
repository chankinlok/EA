from flask import Flask, render_template, request

app = Flask(__name__)

NEWS_ITEMS = [
    {
        "category": "Campus",
        "date": "October 24, 2026",
        "title": "Students turn the courtyard into a community garden",
        "summary": (
            "A new student-led project is bringing fresh produce, greener "
            "spaces, and neighbors together on campus."
        ),
        "read_time": "4 min read",
    },
    {
        "category": "Technology",
        "date": "October 21, 2026",
        "title": "The ideas helping make technology more accessible",
        "summary": (
            "Local volunteers are sharing practical ways to make everyday "
            "digital tools easier for everyone to use."
        ),
        "read_time": "6 min read",
    },
    {
        "category": "People",
        "date": "October 18, 2026",
        "title": "Meet the volunteers keeping the weekend club thriving",
        "summary": (
            "For more than a decade, a small group of neighbors has made "
            "room for creativity, conversation, and new friendships."
        ),
        "read_time": "3 min read",
    },
]


@app.get("/")
def home():
    return render_template("home.html", featured_news=NEWS_ITEMS[0])


@app.get("/news")
def news():
    return render_template("news.html", news_items=NEWS_ITEMS)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = "Sign-in is not enabled for this demo." if request.method == "POST" else None
    return render_template("login.html", message=message)


if __name__ == "__main__":
    app.run()
