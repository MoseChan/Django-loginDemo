from django.shortcuts import render
from django.http import HttpResponse
import MySQLdb
import re
import random

# Create your views here.
'''
@ author：jaydenchan
@ e-mail：2564845837@qq.com

开发者是新手 求轻喷
欢迎一起学习交流
'''

class login():
    def LOGIN(request):
        #判断是否为 post请求
        if request.POST:
            # 取输入信息
            Uid = request.POST['uid']
            password = request.POST['password']

            # 检测是否有sql注入
            check_result = login.check_sql(Uid,password)
            if check_result == 'wrring':
                return HttpResponse('想注入我没那么简单！')  

            # 验证用户名
            real_passwd = login.get_Passwd(Uid)
            if real_passwd == "ERROR":
                return HttpResponse('没有这个用户名!')

            print(real_passwd,password)  

            # 验证密码
            if password ==  real_passwd:
                run_result,Info = login.get_UserInfo(Uid)
                if run_result == 1: 
                    #渲染网页
                    connect = {
                    'login_result' : "登录成功!",
                    'user_sex' : Info[1],
                    'user_Email' : Info[3],
                    'user_age' : Info[2],
                    'user_name' : Info[0],
                    'user_tel':Info[4]
                    }
                    return render(request,"login.html",connect)  
                else:
                    
                    connect = {
                    'login_result' : "登录成功 获取信息失败！"
                    }
                    return render(request,'login.html',connect)
                    
                    #return HttpResponse("登录成功 获取信息失败！")  
            else:
                return HttpResponse("密码错误！")  

    def get_Passwd(uid):
        # 取正确密码
        conn = MySQLdb.connect(host="localhost",user="root",passwd="root",db="userinformation",charset="utf8")  
        cursor = conn.cursor()
        sql = 'select password from userinfo where Uid = "{}"'.format(uid)
        sql_return = cursor.execute(sql)

        #如果出现错误返回 ERROR
        if sql_return == 0:
            conn.close()  
            return "ERROR"
        elif sql_return==1:
            passwd = cursor.fetchone()
            conn.close()  
            return passwd[0]  

    def get_UserInfo(Uid):  
        #取个人信息
        print('getting info')  
        conn = MySQLdb.connect(host="localhost",user="root",passwd="root",db="userinformation",charset="utf8")  
        cursor = conn.cursor()
          
        try:
            #这里代码比较凌乱 因为刚学 django 和 mysql 不长时间 所以不知道有什么好的语法
            cursor.execute('select name from userinfo where Uid = "{}"'.format(Uid))
            username = cursor.fetchone()[0]
            cursor.execute('select sex from userinfo where Uid = "{}"'.format(Uid))  
            sex = cursor.fetchone()[0]
            cursor.execute('select age from userinfo where Uid = "{}"'.format(Uid))  
            age = cursor.fetchone()[0]
            cursor.execute('select Email from userinfo where Uid = "{}"'.format(Uid))
            Email = cursor.fetchone()[0]
            cursor.execute('select tel from userinfo where Uid = "{}"'.format(Uid))
            tel = cursor.fetchone()[0]  
            conn.close()   
            print(username,sex,age,Email,tel)  

            # 返回1 代表成功获取信息
            # 后面的list 是个人信息
            return 1,[username,sex,age,Email,tel]  

        except:
            conn.close()  
            return 0,[]

    def check_sql(uid,inputPassword):
        # 判断是否有sql注入
        if uid[-1] == '\'':
            print('有人尝试注入！')
            return 'wrring'
        elif inputPassword[-1] == '\'':
            print('有人尝试注入！')
            return 'wrring'
        else:
            return 0  


    def index(response):
        # 显示主页
        connect = {}
        return render(response,'index.html',connect)

class sign_up():
    def sign_up_index(response):
        #渲染主页
        connect = {}
        return render(response,'sign-up.html',connect)

    def sign_up(request):
        if request.POST:
            #获取输入信息
            name = request.POST['name']
            sex = request.POST['sex']
            age = request.POST['age']
            tel = request.POST['tel']
            password = request.POST['password']
            reinput_password = request.POST['passwd_reInput']
            Email = request.POST['Email']

            #State_code 为状态码  Check_info 为返回的提示信息
            State_code,Check_info = sign_up.check_inforMation(name,sex,age,tel,password,reinput_password,Email)

            if State_code == 0:
                #如果出现了错误 就提示用户
                return HttpResponse("错误！"+Check_info)
            else:
                #生成 userid 即为 Uid
                #并且 写入数据库
                conn = conn=MySQLdb.connect(host="localhost",user="root",
                    passwd="root",db="userinformation",charset="utf8")
                cursor = conn.cursor()
                Uid = sign_up.generate_Uid()  
                sql = 'insert into userinfo(name,sex,age,tel,Uid,password,Email) value("{}","{}","{}","{}","{}","{}","{}")'.format(name,sex,age,tel,Uid,password,Email)  
                #record = cursor.execute(sql)
                cursor.execute(sql)
                
                return HttpResponse('注册成功！你的账号(UID)是 ：'+ Uid)  
                
    def generate_Uid():
        '''简单的生成一个 uid'''

        #生成 uid的长度
        loop_Number = random.randint(8,10)
        
        uid = ''
        #使用 random 模块 生成uid
        for i in range(0,loop_Number):
            uid = uid+str(random.randint(0,9))

        # 连接数据库
        conn=MySQLdb.connect(host="localhost",user="root",passwd="root",
            db="userinformation",charset="utf8")
        cursor = conn.cursor()
        cursor.execute('select Uid from userinfo where Uid = "{}"'.format(uid))  
        # 这里是判断 uid有无重复
        if cursor.fetchone() == None:
            # 没有重复 返回 uid
            return uid
        else:
            # 重复了 重新调用当前函数 新生成一个
            sign_up.generate_Uid()  

    def check_inforMation(name,sex,age,tel,password,reinput_password,Email):
        #判断数据是否为空
        if name=='':
            return 0,'name cannot be empty.'
        elif sex == '':
            return 0,'sex cannot be empty'
        elif password == '':
            return 0,'password cannot be empty'
        elif Email == '':
            return 0,'Email cannot be empty'
        elif sex != 'man' and sex != 'woman' and sex != 'MAN' and sex != 'WOMAN':
            return 0,'Please input man or woman in sexText'
        
        #判断数据类型 防止数据类型错误
        if age != '':
            try:
                int(age)
            except:
                return 0,'error ,the age must be Int !'
        #判断数据类型
        if tel != '' :
            try:
                int(tel)
            except :
                return 0,'error ,the tel must be Int !'  

        # 判断 E-Mail的格式有无错误
        Email_re = re.compile(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
        check_mail = re.search(Email_re,Email)
        if check_mail == None:
            return 0,'error ,邮箱格式错误！'


        if sign_up.check_value_length(name,sex,age,tel,password,reinput_password,Email) == 0:
            return 0,'请检查字符长度！'

        if password != reinput_password:
            return 0,'两次输入密码不一致！'

        a=sign_up.check_Email(Email) #获取返回值
        if a == 2:
            return 0,'该邮箱已注册'
        elif a==0:
            return 0,'该邮箱无法通过审核系统,请更换。'

        #上面的检测都没有问题 返回1 
        return 1,'OjbK'

    def check_value_length(name,sex,age,tel,password,reinput_password,Email):
        # 判断有无超出长度导致 sql注入
        #有则返回0
        if len(name) > 50 or len(sex)>5 or len(tel)>15 or len(age)>20 or len(password)>20 or \
        len(Email)>30:
            return 0   

    def check_Email(mail):
        '''
        函数约定：
        返回值 为
        1 : 通过检测
        2 : 不通过检测 , 原因 - 邮箱已注册
        0 ：不通过检测, 原因 -会造成sql注入
        '''
        conn=MySQLdb.connect(host="localhost",user="root",passwd="root",
            db="userinformation",charset="utf8")
        cursor = conn.cursor()
        # 判断是否有注入内容
        if mail[-1] != '\'':
            sql = 'select Email from userinfo where Email = "{}"'.format(mail)
            cursor.execute(sql)
            a = cursor.fetchone()
            print(a)  
            # 检查邮箱有无重复
            if a == None:
                conn.close()  
                return 1
            elif a != None:
                conn.close()  
                return 2

        else:
            conn.close()  
            return 0