# main page의 route & view function들이 있는 스크립트 파일
from flask import current_app, flash, request, redirect, session, render_template, url_for, jsonify
from . import main
from ..models import User
from .. import db
from sqlalchemy.sql.expression import func


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    # 로그인 뷰함수
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        password_hash = db.session.query(func.sha2(pw, 224))
        user = User.query.filter_by(user_id = id, password_hash = password_hash).first()

        if not user:
            flash('존재하지 않는 아이디거나, 비밀번호가 옳바르지 않습니다.')
            return redirect(url_for('.login'))

        session['id'] = user.id
        session['user_id'] = user.user_id

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
            except Exception as e:
                return jsonify(data = False, msg = e)

            return jsonify(data = True)

    return render_template('main/register.html')