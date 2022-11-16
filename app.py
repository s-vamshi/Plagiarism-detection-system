from flask import Flask, render_template ,request,url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy  
import nltk
from flask_ngrok import run_with_ngrok
nltk.download("punkt")
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

from nltk.corpus import stopwords

app = Flask(__name__)
run_with_ngrok(app) 

app.secret_key = "abc"  

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student.db"
db = SQLAlchemy(app)

class stud(db.Model):
    id = db.Column(db.String(100),primary_key = True)
    file_name = db.Column(db.String(100),nullable = False)
    tokens = db.Column(db.String(10000),nullable = False)
    sent = db.Column(db.String(10000),nullable = False)
    def __init__(self,id,file_name,tokens,sent):
        self.id = id
        self.file_name =file_name 
        self.tokens = tokens
        self.sent = sent 
        

class auto(db.Model):
    userid = db.Column(db.String(100),primary_key = True)
    username = db.Column(db.String(100),nullable = False)
    role = db.Column(db.String(100),nullable = True)
    password = db.Column(db.String(100),nullable = False)
    def __init__(self,userid,username,role,password):
        self.userid = userid
        self.username = username 
        self.role = role
        self.password = password 

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/uploadd")
def uploadd():
    return render_template("home.html")

@app.route("/reqdata",methods=['POST'])
def viewdata():
    uid = request.form["userid"]
    data = stud.query.filter_by(id = uid)
    return render_template("viewdata.html",sdata = data)
     

def uploadd():
    return render_template("home.html")

@app.route('/sign')
def sign():
    return render_template("signin.html")

@app.route('/login')
def login():
    return render_template("login.html",)

@app.route('/admin')
def admin():
    all_details = auto.query.filter(auto.role=='NULL')
    lens=auto.query.filter(auto.role=='NULL').count()
    return render_template("view.html",all_detail=all_details,len=lens)

@app.route('/acc',methods=['POST'])
def acc():
    uid = request.form["userid"]
    urole = request.form["role"]
    if urole=="remove":
        auto.query.filter_by(userid=uid).delete()
        db.session.commit()
        return redirect("/admin")

    ad = auto.query.filter_by(userid = uid).first()
    ad.role = urole
    if(urole=="student"):
        addEmptyAssignment=stud(uid,"","","")
        db.session.add(addEmptyAssignment)
    db.session.commit()
    return redirect("/admin")

@app.route('/signed', methods = ['POST', 'GET'])
def signed():
    #if request.form['uid'] != "" and request.form['uname'] != "" and  request.form['urole'] !="" and  request.form['upw'] != "" : 
    if db.session.query(db.exists().where(auto.userid==request.form["uid"])).scalar() == False :
        add_details = auto(request.form["uid"],request.form["uname"],"NULL",request.form['upw'])
        db.session.add(add_details)
        db.session.commit()
        flash("Successfully Registered")
        return render_template("login.html")
    else:
        flash("ID Exists")
        return render_template("signin.html")

@app.route("/remstu" ,methods = ['POST', 'GET'])
def remstu():
    all_details = auto.query.filter_by(role="student")
    lens = auto.query.filter_by(role="student").count()
    return render_template("remstu.html",all_detail=all_details,len=lens)

@app.route("/deldata",methods = ['POST', 'GET'])
def deldata():
    deletedata=stud.query.filter_by(id=request.form["userid"]).first()
    deletedata.file_name=""
    deletedata.sent=""
    deletedata.tokens=""
    db.session.commit()
    return redirect("/viewtea")

@app.route('/loged',methods = ['POST', 'GET'])
def loged():
    if request.method == "POST":
        uname = request.form["uid"]
        passw = request.form["upw"]
        login = auto.query.filter_by(userid=uname,password=passw).first()
        if login is not None:
                if(login.role=='student' ):
                    if db.session.query(db.exists().where(stud.id==uname)).scalar() == True:
                        temp=stud.query.filter_by(id=uname).first()
                        if(len(temp.file_name)!=0):
                            flash("Already uploaded")
                            return render_template("success.html")
                        else:
                            return  render_template("home.html",uname=uname)
                    else:
                        return render_template("home.html",uname=uname)
                elif(login.role=='teacher'):
                    return redirect("/viewtea")
                elif(login.role=='NULL'):
                    flash("You are not verified by admin please wait for a day!")
                    return redirect("/login")
                return redirect("/admin")
        else:
            flash("Incorrect ID or PASSWORD")
            return redirect("/login")


@app.route("/delstu",methods=['POST', 'GET'])
def delstu():
    auto.query.filter_by(userid=request.form["userid"]).delete()
    stud.query.filter_by(id=request.form["userid"]).delete()
    db.session.commit()
    return redirect("/remstu")

    
@app.route('/viewtea', methods = ['POST', 'GET'])
def wiewtea():
    all_details = stud.query.all()
    lens=stud.query.filter().count()
    return render_template("viewtea.html",all_detail=all_details,len=lens)

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    #try:
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        
        userid = request.form["userid"]
        
        for files in uploaded_files:
            text = ((files.read().decode('utf-8','strict').replace("\n"," ").replace("\r"," ")).lower()) 
            tokens_o=word_tokenize(text)
            tokens_o = [token.lower() for token in tokens_o]
            sent_o=sent_tokenize(text)[0]
            #print(sent_o) 
            stude = stud.query.filter_by(id=userid).first()
  
            stude.file_name = files.filename
            stude.tokens = " ".join(tokens_o)
            stude.sent = sent_o
            db.session.commit()
        flash("files uploaded successfully")
        return render_template("success.html")
    # except:
    #     flash("Already uploaded")
    #     return render_template("success.html")

# @app.route('/view',methods = ['POST', 'GET'])
# def view():
#     all_details = stud.query.all()
#     return render_template("view.html",all_detail=all_details)


@app.route('/plag',methods = ['POST', 'GET'])
def plag():
    all_details = stud.query.all()
    d = {}
    for detail in all_details:
        d[detail.id] = detail.tokens.replace("  "," ").split(" ")
    #print("d ",d)
    parent =[]
    for i in (d.keys()):
        parent.append(i)
    #print(parent)
    dfile = {}
    for detail in all_details:
        dfile[detail.id] = detail.file_name
    #print(dfile)
    dsent = {}
    for detail in all_details:
        dsent[detail.id] = detail.sent
    #print("dsent : ",dsent)
    #maximum length of LCS for a sentence in suspicious text
    copy = {}
    for i in parent:
        copy[i] = 0
    for i in range(len(parent)):
        a = parent[i]
        l1 = []
        for j in range(len(parent)):
            if j != i:
                max_lcs=0
                sum_lcs=0
                sent_o=dsent[a]
                sent_p=dsent[parent[j]]
                #print(sent_o,"--",sent_p)
                l=lcs(sent_o,sent_p)
                max_lcs=max(max_lcs,l)
                sum_lcs+=max_lcs
                #print(sum_lcs,len(d[parent[j]]),(d[parent[j]]))
                score=sum_lcs/len(d[parent[j]])
                #print("score : ",score)
                if(score>0.5):#j,i
                    l1.append([parent[j],(score)])
                    #print("l1 :",l1)
        if(len(l1)==0):
            copy[parent[i]]=[[0,0]]
        else:
            copy[parent[i]]=l1
    #print(copy.items())
    lens=stud.query.filter().count()
    return render_template("report.html",copy=copy.items(),len=lens)

def lcs(l1,l2):
    # storing the dp values 
    s1=word_tokenize(l1)
    
    s2=word_tokenize(l2)
    dp = [[None]*(len(s1)+1) for i in range(len(s2)+1)] 
  
    for i in range(len(s2)+1): 
        for j in range(len(s1)+1): 
            if i == 0 or j == 0: 
                dp[i][j] = 0
            elif s2[i-1] == s1[j-1]: 
                dp[i][j] = dp[i-1][j-1]+1
            else: 
                dp[i][j] = max(dp[i-1][j] , dp[i][j-1]) 
    return dp[len(s2)][len(s1)]

@app.route('/del',methods = ['POST', 'GET'])
def delete():
    # db.session.query(stud).delete()
    allstud=stud.query.all()
    for student in allstud:
        student.file_name=""
        student.tokens=""
        student.sent=""
    #db.session.delete(stud)
    db.session.commit()
    return redirect('/viewtea')


if __name__ == "__main__":
    app.run()
    # app.run(debug = True)