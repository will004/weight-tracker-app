from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from weight_tracker import app, db
from weight_tracker.forms import RegistrationForm, LoginForm
from weight_tracker.models import User


@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
       hashed = generate_password_hash(form.password.data) 
       user = User(name=form.fullname.data, username=form.username.data, email=form.email.data, hashed=hashed)
       db.session.add(user)
       db.session.commit()
       flash('Registration succeed', 'success')
       return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.hashed, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')

            flash('Welcome!', 'success')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check your email and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/friends')
@login_required
def friends():
    friends = current_user.friends.all()
    return render_template('friends.html', title='Friend List', friends=friends)

@app.route('/new_friends')
@login_required
def new_friends():
    new_friends = current_user.friends.all() 
    if not new_friends:
        # TODO: Add pagination if there is a lot of user
        new_friends = User.query.filter(User.id != current_user.id).all()
    else:
        # Query: SELECT * FROM user WHERE id != (SELECT adder_id FROM friendship WHERE added_id = current_user.id);
        new_friends = []
    print(new_friends)
    return render_template('new_friends.html', title='New Friends', new_friends=new_friends)