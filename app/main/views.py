# main page의 route & view function들이 있는 스크립트 파일
from flask import current_app, flash, request, redirect, session, render_template, url_for, jsonify
from . import main
from ..models import User
from .. import db
from sqlalchemy.sql.expression import func
import os


@main.route('/')
def index():
    user = None
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first_or_404()

    return render_template('main/index.html', user = user)


@main.route('/login', methods=['GET', 'POST'])
def login():
    # 로그인 뷰함수
    print(session)
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        password_hash = db.session.query(func.sha2(pw, 224))
        user = User.query.filter_by(user_id = id, password_hash = password_hash).first()

        if not user:
            flash('존재하지 않는 아이디거나, 비밀번호가 옳바르지 않습니다.')
            return redirect(url_for('.login'))

        session['id'] = user.id

        return redirect(url_for('.index'))

    return render_template('main/login.html')


@main.route('/register', methods =['GET', 'POST'])
def register():
    # 회원가입 뷰함수
    if request.method == "POST":
        data = request.get_json()

        if 'id' in data:
            user = User.query.filter_by(user_id = data['id']).first()

            if user:
                return jsonify(data = False)
            else:
                return jsonify(data = True)

        elif 'userName' in data:
            user = User.query.filter_by(username = data['userName']).first()

            if user:
                return jsonify(data = False)
            else:
                return jsonify(data = True)

        elif 'form' in data:
            try:
                password_hash = db.session.query(func.sha2(data["form"]["password"], 224))
                user = User(user_id = data['form']['id'], username = data["form"]["username"], password_hash = password_hash)
                db.session.add(user)
                db.session.commit()
                os.mkdir(os.path.join(current_app.config['PROFILE_PATH'], user.user_id))
            except Exception as e:
                return jsonify(data = False, msg = e)

            return jsonify(data = True)

    return render_template('main/register.html')


@main.route('/search', methods=['GET', 'POST'])
def search():
    if not 'id' in session:
        if request.method == 'POST':
            id = request.form['id']
            user = User.query.filter_by(user_id = id).first_or_404()

            session['id'] = user.id

            return redirect(url_for('.reset'))
        return render_template('main/search_password.html')

    else:
        flash('로그인이 되어있습니다.')
        return redirect(url_for('.index'))


@main.route('/reset', methods=['GET', 'POST'])
def reset():
    if 'id' in session:
        if request.method == 'POST':
            user = User.query.filter_by(id = session['id']).first()
            password_hash = db.session.query(func.sha2(request.form['pw'], 224))
            user.password_hash = password_hash
            db.session.commit()

            session.pop('id', None)

            flash('비밀번호 변경했습니다.')

            return redirect(url_for('.index'))
        return render_template('main/reset_password.html')
    else:
        flash('로그인이 되어있지 않거나, 해당 접근 방식으로는 비밀번호 변경이 불가능합니다.')
        return redirect(url_for('.index'))


@main.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id', None)
    else:
        flash('로그인이 되어있지 않는 상태입니다.')

    return redirect(url_for('.index'))


@main.route('/profile')
def profile():
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first_or_404()
        return render_template('main/profile.html', user = user)
    else:
        flash('로그인이 되어있지 않습니다.')
        return redirect(url_for('.index'))


@main.route('/edit_profile')
def edit_profile():
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first()
        return render_template('main/edit_profile.html', user = user)
    else:
        flash('로그인이 되어있지 않습니다.')
        return redirect(url_for('.index'))