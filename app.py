from flask import Flask,render_template,request
from flask_socketio import SocketIO,emit,send
import database as d

app=Flask(__name__)
app.config['SECRET_KEY']="sahith_kumar"
socketio=SocketIO(app,cors_allowed_origins="*",async_mode=None)

active_user={}
users=[]
sids=[]
con=d.connect()

def checkDup(l1,l2):
    for i in l1:
        for ind,j in enumerate(l2):
            if i[0]==j[0]:
                del l2[ind]
    l2c=[]
    for i in l2:
        if i[0] not in l2c:
            l2c.append(i[0])
    return {'new_list':l1,'old_list':l2c}



def r_sid(user):
    global users,sids
    for ind,u in enumerate(users):
        if u==user:
            return sids[ind]
    return None
@app.route('/')
def home():
    return render_template('index.html',async_mode=socketio.async_mode)

@socketio.on('connect_user')
def connect(user):
    global users,sids
    if user['user'] not in users:
        print("\n\nconnected\n\n",request.sid,user)
        users.append(user['user'])
        sids.append(request.sid)
    else:
        ind=users.index(user['user'])
        del users[ind]
        del sids[ind]
        users.append(user['user'])
        sids.append(request.sid)
       
@socketio.on('disconnect')
def disconnect():
    global users
    print("\n\ndisconnected\n\n",request.sid)
    print("\n\n\n",users,"\n\n\n")


@socketio.on("search_username")
def search_username(user):
    global con
    data=d.retrieve_usernames(user['uname'],con)
    print(data)
    emit("recieve_usernames",data,room=request.sid)

@socketio.on("retrieve_active")
def retrieve_active(user):
    global con
    active_user[user['f_u']]=d.retrieve_active(con,user['f_u'])
    emit("recieve_active",{"active":active_user[user['f_u']]},room=request.sid)


@socketio.on('insert_backup')
def insert_backup(user):
    d.insert_backup(user['f_u'],user['t_u'],con)

@socketio.on('retrieve_onload')
def retrieve_onload(user):
    global con
    data=d.retrieve_onload(user['f_u'],con)
    data=checkDup(data['new_list'],data['old_list'])
    emit("recieve_onload",data,room=request.sid)

@socketio.on("send_msg")
def send_msg(user):
    global con
    ti=d.insert_new(user['f_u'],user['t_u'],user['msg'],con)
    sid=r_sid(user['t_u'])
    user['time']=ti
    if sid!=None:
        emit("new_msg",user,room=sid)
    emit("recieve_sent",user,room=request.sid)

@socketio.on("search_user")
def search_user(user):
        global con
        emit("search_result",d.retrieve_user(user["uname"],con),room=request.sid)

@socketio.on("send_msg_backup")
def backup(user):
    global con
    d.insert_backup(user['f_u'],user['t_u'],con)

@socketio.on("send_g_msg")
def send_g(user):
    global con
    ti=d.insert_global(user['f_u'],user['msg'],con)
    user["time"]=ti
    emit("recieve_global_new",user,broadcast=True)

@socketio.on("retrieve_new")
def retrieve_n(user):
    global con
    data = d.retrieve_new(user['f_u'],user['t_u'],con)
    emit("recieve_new",data,room=request.sid)


@socketio.on("retrieve_old")
def retrieve_o(user):
    global con
    data = d.retrieve_old(user['f_u'],user['t_u'],con)
    emit("recieve_old",data,room=request.sid)
    d.insert_backup(user['f_u'],user['t_u'],con)

@socketio.on("update_active")
def update_active(user):
    global con
    active_user[user['f_u']]=user['t_u']
    d.insert_active(con,user['f_u'],user['t_u'])

@socketio.on("retrieve_global")
def retrieve_global_msg(user):
    global con
    data=d.retrieve_g(con)
    emit("recieve_global",data,room=request.sid)

@app.route("/check_user",methods=["GET","POST"])
def check_user():
    un=request.args.get("uname")
    global con
    if d.check_user(un,con):
        return "true"
    else:
        pswd=request.args.get("pswd")
        d.register(un,pswd,con)
        return "false"

@app.route("/validate_user",methods=["GET","POST"])
def validate_user():
    un=request.args.get("uname")
    pswd=request.args.get("pswd")
    global con
    if d.validate_user(un,pswd,con):
        return "true"
    else:
        return "false"

@app.route("/chat",methods=["GET","POST"])
def render_chat():
    return render_template("chat.html",uname=request.args.get("uname"))

    
if __name__ == "__main__":
    socketio.run(app,debug=True)    