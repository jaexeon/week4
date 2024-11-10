import flask
import pymysql
import time
import re

app = flask.Flask(__name__)
app.secret_key = "very safe key"

IpList = {
}
DDoSCnt = {
}

@app.before_request
def ddos_protection():
    ip = flask.request.remote_addr
    cur_time = int(time.time())

    if not IpList.get(ip) or IpList.get(ip) != cur_time:
        IpList[ip] = cur_time
        DDoSCnt[ip] = 0

    elif IpList[ip] == cur_time:
        DDoSCnt[ip] += 1

    if DDoSCnt[ip] >= 10:
        print(f"DDoS Warning! : {ip}")

def db_execute(query):
    conn = pymysql.connect(host="host.docker.internal", port=3307, user="root", password="1234", db="week4", charset='utf8')
    #conn = pymysql.connect(host="localhost", port=3306, user="root", password="1234", db="week4", charset='utf8')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    cur.execute(query)
    res = cur.fetchall()

    conn.commit()
    conn.close()
    return res

@app.route("/", methods=['GET', 'POST'])
@app.route("/board", methods=['GET', 'POST'])
def index():
    session = flask.session
    post_info = db_execute("SELECT * FROM post_table")
    post_is_secret = db_execute("SELECT post_is_secret FROM post_table")

    return flask.render_template('main.html', post_info=post_info, session=session)

@app.route("/join", methods=['GET', 'POST'])
def join():
    if flask.request.method == 'GET':
        return flask.render_template('join.html')
    elif flask.request.method == 'POST':
        inserted_user = flask.request.form['inserted_user']
        inserted_password = flask.request.form['inserted_password']
        
        valid = re.findall(r"^[a-zA-Z0-9~!@#$%^&*_-]{8,}$", inserted_password)

        if not valid:
            return "<script>alert('비밀번호가 정상적이지 않습니다!');location.href='/join'</script>"

        query = f"SELECT * FROM user_table WHERE user_name='{inserted_user}'"
        res = db_execute(query)

        if res:
            return "<script>alert('해당 이름의 유저가 이미 존재합니다!'); location.href='/join'</script>"
        
        query = f"INSERT INTO user_table(user_name, user_password) VALUES('{inserted_user}', '{inserted_password}')"
        db_execute(query)
        
        return "<script>alert('성공적으로 회원가입 되었습니다!'); location.href='/'</script>"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    elif flask.request.method == 'POST':
        inserted_user = flask.request.form['inserted_user']
        inserted_password = flask.request.form['inserted_password']
        
        query = f"SELECT * FROM user_table WHERE user_name='{inserted_user}' and user_password='{inserted_password}'"
        res = db_execute(query)

        if not res:
            return "<script>alert('해당 유저를 찾을 수 없습니다. 이름 혹은 비밀번호를 확인해주십시오.'); location.href='/login'</script>"
        else:
            for key, val in res[0].items():
                flask.session[key] = val
            return "<script>alert('로그인 성공'); location.href='/'</script>"
        
@app.route("/logout")
def logout():
    flask.session.clear()
    return flask.redirect('/')

@app.route("/board/write", methods=['GET', 'POST'])
def write():
    if flask.request.method == 'GET':
        return flask.render_template('write.html', session = flask.session)
    elif flask.request.method == 'POST':
        if not flask.session.get('user_name'): # 로그인 X
            username = flask.request.form['inserted_user']
            password = flask.request.form['inserted_password']
        elif flask.session.get('user_name'): # 로그인 O
            username = flask.session['user_name']
            password = flask.session['user_password']

        inserted_title = flask.request.form['inserted_title']
        inserted_content = flask.request.form['inserted_content']
        if not flask.request.form.get('is_secret_post'):
            is_secret_post = 0
        else:
            is_secret_post = 1

        if not inserted_title:
            return "<script>alert('제목이 비어있습니다!'); location.href='/board/write'</script>"

        query = f"INSERT INTO post_table(post_user, post_password, post_title, post_content, post_is_secret, post_date) VALUES('{username}', '{password}', '{inserted_title}', '{inserted_content}', {is_secret_post}, now());"
        db_execute(query)
        return "<script>location.href='/'</script>"
    
@app.route("/board/modify/<int:post_id>", methods=['GET', 'POST'])
def modify(post_id):
    res = db_execute(f"SELECT * FROM post_table WHERE post_id={post_id}")
    
    if not res:
        return "<script>alert('존재하지 않는 게시글입니다!'); location.href='/'</script>"
    else:
        res = res[0]
    # 유효한 게시글인지 확인

    inserted_title = 0
    if flask.request.form.get('inserted_title'):
        inserted_title = flask.request.form['inserted_title']
        inserted_content = flask.request.form['inserted_content']
        if flask.request.form.get('is_secret_post'):
            is_secret_post = 1
        else:
            is_secret_post = 0
    
    if flask.session.get('user_name'):
        if res['post_user'] == flask.session['user_name']:
            if not inserted_title   : # 아직 서브밋 안함
                return flask.render_template('modify.html', post_info = res)
            else:
                query = f"UPDATE post_table SET post_title='{inserted_title}', post_content='{inserted_content}', post_is_secret={is_secret_post} WHERE post_id={post_id}"
                db_execute(query=query)
                return f"<script>alert('게시글이 수정되었습니다.'); location.href='/board/view/{post_id}'</script>"
    if flask.request.form.get('inserted_password'):
        inserted_password = flask.request.form['inserted_password']
        if res['post_password'] == inserted_password:
            return flask.render_template('modify.html', post_info = res)
        else:
            return "<script>alert('비밀번호가 일치하지 않습니다!'); location.href='/'</script>"
    else:
        return flask.render_template('need_password.html')

@app.route("/board/delete/<int:post_id>", methods=['GET', 'POST'])
def delete(post_id):
    res = db_execute(f"SELECT * FROM post_table WHERE post_id={post_id}")
    
    if not res:
        return "<script>alert('존재하지 않는 게시글입니다!'); location.href='/'</script>"
    else:
        res = res[0]
    

    if flask.request.method == 'GET':
        return flask.render_template('need_password.html')
    elif flask.request.method == 'POST':
        inserted_password = flask.request.form['inserted_password']
        res = db_execute(f"SELECT * FROM post_table WHERE post_id={post_id} and post_password='{inserted_password}'")
        if not res:
            return "<script>alert('비밀번호가 일치하지 않습니다!');location.href='/'</script>" 
        else :
            db_execute(f"DELETE FROM post_table WHERE post_id={post_id}")
            db_execute(f"DELETE FROM comment_table WHERE comment_parent_post_id={post_id}")
            return "<script>alert('성공적으로 삭제되었습니다.');location.href='/'</script>" 

@app.route("/board/view/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    res = db_execute(f"SELECT * FROM post_table WHERE post_id={post_id}")
    
    if not res:
        return "<script>alert('존재하지 않는 게시글입니다!'); location.href='/'</script>"
    else:
        res = res[0]
    
    comment_list = db_execute(f"SELECT * FROM comment_table WHERE comment_parent_post_id={post_id}")

    if not res['post_is_secret']: # 비밀글이 아니면
        db_execute(f"UPDATE post_table SET post_view_cnt={res['post_view_cnt']+1} WHERE post_id={post_id};")
        return flask.render_template("board.html", post_info=res, comment_list = comment_list, session = flask.session)
    
    #비밀글이면
    if flask.request.method == 'POST':
        if flask.request.form.get('inserted_password'):
            inserted_password = flask.request.form['inserted_password']
            if res['post_password'] == inserted_password:
                flask.session['post_secret_auth'] = post_id
            else:
                return "<script>alert('비밀번호가 일치하지 않습니다!');location.href=location.href;</script>"
        else:
            return "<script>alert('비밀번호를 입력해주세요.');location.href=location.href;</script>"
    if flask.session.get('post_secret_auth') == post_id or flask.session.get('user_name') == res['post_user']:
        db_execute(f"UPDATE post_table SET post_view_cnt={res['post_view_cnt']+1} WHERE post_id={post_id};")
        return flask.render_template("board.html", post_info=res, comment_list = comment_list, session = flask.session)
    
    return flask.render_template('need_password.html')
            
@app.route("/board/write_comment/<int:post_id>", methods=['POST'])
def write_comment(post_id):
    if not flask.session.get('user_name'): # 로그인 X
        comment_user = flask.request.form['comment_user']
        comment_password = flask.request.form['comment_password']
    elif flask.session.get('user_name'): # 로그인 O
        comment_user = flask.session['user_name']
        comment_password = flask.session['user_password']

    comment_content = flask.request.form['comment_content']

    db_execute(f"INSERT INTO comment_table(comment_parent_post_id, comment_user, comment_password, comment_content, comment_date) VALUES({post_id}, '{comment_user}', '{comment_password}', '{comment_content}', now())")
    return flask.redirect(f'/board/view/{post_id}')

@app.route("/board/delete_comment/<int:comment_id>", methods=['GET', 'POST'])
def delete_comment(comment_id):
    res = db_execute(f"SELECT * FROM comment_table WHERE comment_id={comment_id}")
    if not res:
        return "<script>alert('존재하지 않는 댓글입니다!'); location.href='/'</script>"
    else:
        res = res[0]


    post_id = res['comment_parent_post_id']
    if flask.session.get('user_id'):
        if flask.session['user_id'] == res['comment_user'] and flask.session['user_password'] == res['comment_password']:
            db_execute(f"DELETE FROM comment_table WHERE comment_id={comment_id}")
            return flask.redirect(f'/board/view/{post_id}')
        else:
            return f"<script>alert('다른 유저의 댓글입니다.');location.href='/board/view/{post_id}'</script>"
    elif flask.request.form.get('inserted_password'):
        if res['comment_password'] == flask.request.form['inserted_password']:
            db_execute(f"DELETE FROM comment_table WHERE comment_id={comment_id}")
            return flask.redirect(f'/board/view/{post_id}')
        else:
            return "<script>alert('비밀번호가 일치하지 않습니다.');location.href=location.href;</script>"
    else:
        return flask.render_template('need_password.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    print("Server On")