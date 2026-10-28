import io
import qrcode
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lihkg_secret_key_123456'
# 設定 MySQL 資料庫連線 (請依個人環境修改 root:password 及 db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/lihkg_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==================== 多對多關聯表 (M:N) ====================
post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)

# ==================== 資料庫模型 (Models) ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # 密碼加密存儲
    
    # 1 對 1 關聯
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    # 1 對多 關聯 (發文)
    posts = db.relationship('Post', backref='author', lazy=True)
    # 多對多 關聯 (讚好)
    liked_posts = db.relationship('Post', secondary=post_likes, backref=db.backref('liked_by', lazy='dynamic'))

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False) # 1:1 Unique
    bio = db.Column(db.String(200), default="這個會員很懶，什麼也沒寫。")
    avatar_url = db.Column(db.String(255), default="https://i.imgur.com/6VBx3io.png")

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="時事")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    # 1 對多 關聯 (留言)
    comments = db.relationship('Comment', backref='post', cascade="all, delete-orphan", lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    commenter = db.relationship('User', backref='comments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== 路由邏輯 (Routes) ====================

# 1. 討論區首頁 (仿 LIHKG 列表)
@app.route('/')
@app.route('/category/<cat>')
def index(cat=None):
    category = request.args.get('cat', '時事')
    order = request.args.get('order', 'now')
    
    query = Post.query
    if cat:
        query = query.filter_by(category=cat)
        
    posts = query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, current_cat=category)

# 2. 文章內容頁面
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("請先登入再發表留言！", "warning")
            return redirect(url_for('login'))
        
        comment_content = request.form.get('content')
        if comment_content:
            new_comment = Comment(content=comment_content, user_id=current_user.id, post_id=post.id)
            db.session.add(new_comment)
            db.session.commit()
            flash("留言成功！", "success")
            return redirect(url_for('post_detail', post_id=post.id))
            
    return render_template('post.html', post=post)

# 3. 註冊頁面 (含輸入驗證與密碼加密)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        # 後端驗證
        if not username or not email or not password:
            flash("所有欄位均為必填！", "danger")
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash("該使用者名稱已被使用！", "danger")
            return redirect(url_for('register'))
            
        # 額外 Python 功能 1：密碼安全雜湊 (Password Hashing)
        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        # 建立 1:1 個人檔案
        new_profile = UserProfile(user_id=new_user.id)
        db.session.add(new_profile)
        db.session.commit()
        
        flash("註冊成功，請登入！", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

# 4. 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("登入成功！", "success")
            return redirect(url_for('index'))
        else:
            flash("帳號或密碼錯誤！", "danger")
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("已成功登出。", "info")
    return redirect(url_for('index'))

# 5. 發表新文章
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        
        if title and content:
            post = Post(title=title, category=category, content=content, user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("文章發表成功！", "success")
            return redirect(url_for('index'))
            
    return render_template('create_post.html')

# 6. 額外 Python 功能 2：動態生成文章 QR Code 圖片
@app.route('/qrcode/<int:post_id>')
def generate_qrcode(post_id):
    post_url = url_for('post_detail', post_id=post_id, _external=True)
    img = qrcode.make(post_url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # 自動建立資料庫表結構
    app.run(debug=True)