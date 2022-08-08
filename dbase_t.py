import psycopg2
from datetime import datetime
def connect():
    try:
        return psycopg2.connect(user="dxxfrcvpwpiwum",password="222460cb9d179cbfa06956b654f219528a9092c7d8bf1feab83f802e64aebce2",host="ec2-107-21-120-104.compute-1.amazonaws.com",port="5432",database="d19ava5a4pmn8a")
    except:
        print("could not connect")
        return False

def create(con):
    cur=con.cursor()
    # cur.execute("drop table backup_global")
    # cur.execute("drop table new_messages")
    # cur.execute("drop table backup")
    # cur.execute("drop table registered_users")
    # cur.execute("drop table recent_chats")
    cur.execute("create table if not exists new_messages(from_u text,to_u text,msg text,date_msg text)")
    cur.execute("create table if not exists backup(from_u text,to_u text,msg text,date_msg text)")
    cur.execute("create table if not exists backup_global(from_u text,msg text,date_msg text)")
    cur.execute("create table if not exists registered_users(id_uname text,uname text,pswd text)")
    con.commit()
    # cur.execute("create table if not exists active_chats(f_u text,t_u text,id integer PRIMARY KEY AUTOINCREMENT)")
    

def insert_new(from_u,to_u,msg,con):
    cur=con.cursor()
    d=datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
    cur.execute(f"insert into new_messages values('{from_u}','{to_u}','{msg}','{d}')")
    con.commit()
    return d

def insert_global(from_u,msg,con):
    cur=con.cursor()
    d=datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
    cur.execute(f"insert into backup_global values('{from_u}','{msg}','{d}')")
    con.commit()
    return d

def insert_backup(from_u,to_u,con):
    cur=con.cursor()
    data=cur.execute(f"select * from new_messages where from_u='{to_u}' and to_u='{from_u}'")
    rows=data.fetchall()
    for row in rows:
        cur.execute(f"insert into backup values('{row[0]}','{row[1]}','{row[2]}','{row[3]}')")
    cur.execute(f"delete from new_messages where from_u='{to_u}' and to_u='{from_u}'")
    con.commit()


def retrieve_user(uname,con):
    cur=con.cursor()
    data=cur.execute(f"select * from registered_users where uname='{uname}'")
    return data.fetchall()


def retrieve_new(f_u,t_u,con):
    cur=con.cursor()
    
    insert_backup(f_u,t_u,con)
    data=[]
    data2=cur.execute(f"select * from new_messages where from_u='{f_u}' and to_u='{t_u}'")
    data = data2.fetchall()
    for da in data2:
        data.append(da)
    data2=cur.execute(f"select * from backup where from_u='{f_u}' and to_u='{t_u}'")
    data2=data2.fetchall()
    for da in data2:
        data.append(da)
    
    data2=cur.execute(f"select * from backup where from_u='{t_u}' and to_u='{f_u}'")
    data2=data2.fetchall()
    for da in data2:
        data.append(da)
    data=list(set(data))
    return sorted(data,key=lambda x:datetime.strptime(x[3],'%d-%m-%Y %I:%M:%S %p'))

def retrieve_old(f_u,t_u,con):
    cur=con.cursor()
    data=cur.execute(f"select * from backup where from_u='{f_u}' and to_u='{t_u}'")
    data =  data.fetchall()
    data2=cur.execute(f"select * from new_messages where from_u='{t_u}' and to_u='{f_u}'")
    data2=data2.fetchall()
    for da in data2:
        data.append(da)
    return sorted(data,key=lambda x:datetime.strptime(x[3],'%d-%m-%Y %I:%M:%S %p'))

def retrieve_onload(f_u,con):
    cur=con.cursor()
    data2=cur.execute(f"select from_u,count(to_u) from new_messages where to_u='{f_u}' group by from_u order by count(to_u) desc")
    data2=data2.fetchall()
    data3=cur.execute(f"select from_u,date_msg from backup where to_u='{f_u}' group by from_u")
    data3=data3.fetchall()
    data4=cur.execute(f"select to_u,date_msg from backup where from_u='{f_u}' group by to_u")
    data4=data4.fetchall()
    for da in data4:
        data3.append(da)
    data4=cur.execute(f"select to_u,date_msg from new_messages where from_u='{f_u}' group by from_u")
    for da in data4:
        data3.append(da)
    data3=sorted(data3,key=lambda x:datetime.strptime(x[1],'%d-%m-%Y %I:%M:%S %p'),reverse=True)
    return {"new_list":data2,"old_list":data3}


def check_user(user,con):
    cur=con.cursor()
    data=cur.execute(f"select * from registered_users where uname='{user}'")
    data=data.fetchall()
    if len(data)==0:
        return False
    return True

def register(user,pswd,con):
    cur=con.cursor()
    cur.execute(f"insert into registered_users values('{user.lower()}','{user}','{pswd}')")
    con.commit()

def validate_user(user,pswd,con):
    cur=con.cursor()
    data=cur.execute(f"select * from registered_users where uname='{user}' and pswd='{pswd}'")
    data=data.fetchall()
    if len(data)==0:
        return False
    return True

def retrieve_g(con):
    cur=con.cursor()
    data = cur.execute(f"select * from backup_global")
    data =  data.fetchall()
    return sorted(data,key=lambda x:datetime.strptime(x[2],'%d-%m-%Y %I:%M:%S %p'))

def retrieve_active(con,f_u):
    cur=con.cursor()
    data=cur.execute(f"select f_u,t_u from (select * from active_chats where f_u='{f_u}') order by id desc limit 1")
    return data.fetchall()

def insert_active(con,f_u,t_u):
    cur=con.cursor()
    cur.execute(f"insert into active_chats(f_u,t_u) values('{f_u}','{t_u}')")
    con.commit()


def retrieve_usernames(user,con):
    cur=con.cursor()
    data=cur.execute(f"select uname from registered_users where id_uname like('%{user}%')")
    return data.fetchall()

# con=connect()
# create(con)
# print(list(retrieve_usernames("sajo",con)))
# insert_global("sahith","It works",con)