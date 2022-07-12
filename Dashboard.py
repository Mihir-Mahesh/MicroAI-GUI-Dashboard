from tkinter import *
from tkinter.ttk import LabeledScale
from turtle import bgcolor
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation  
import random
from PIL import Image, ImageTk
import time
import redis
import datetime
import statistics

matplotlib.use("TkAgg")
r = redis.Redis(host='192.168.2.122', port=6379, db=0) #change host to your ip
running = False #checks to see if the program is running (do not change)
font = 'Arial' #font for the whole app

class figMaker:     
    def __init__(self, x, y, res, title):
        self.x = x
        self.y = y
        self.res = res
        self.title = title

    def figMaker(self):
        self.figs = Figure(figsize=(self.x, self.y), dpi=self.res)
        self.figs.suptitle(self.title)

class subplotMaker:
    def __init__(self, fig, num_col, num_row, num_ax, redis_key, title, yax):
        self.fig = fig
        self.ax = fig.add_subplot(num_col, num_row, num_ax)
        self.title = title
        self.y_label = yax
        self.redis_key = redis_key
        self.x = []
        self.y = []
        self.upper = []
        self.lower = []
    
    def append_all(self):
        if (len(self.x) > 0):
            self.x.append(max(self.x) + 1)
        else:
            self.x.append(0)
        if (self.redis_key != "HS_1"):
            self.y.append(float(r.get(self.redis_key + "_R")))
            self.upper.append(float(r.get(self.redis_key + "_U")))
            self.lower.append(float(r.get(self.redis_key + "_L")))
        else:
            self.y.append(float(r.get("1_HS")))
            self.upper.append(float(r.get("c0" + "_U")))
            self.lower.append(float(r.get("c0" + "_U")))

        if (len(self.x) > 20):
            self.x.pop(0)
            self.y.pop(0)
            self.upper.pop(0)
            self.lower.pop(0)
    
    def graph(self):
        self.ax.clear()
        self.ax.set_xlabel("Time (s)", fontsize = 7)
        self.ax.set_ylabel(self.y_label, fontsize = 6)
        self.ax.tick_params(labelsize=5)
        self.ax.set_title(self.title, fontweight = "bold", fontsize = 7)
        self.ax.plot(self.x, self.upper, color = "b")
        self.ax.plot(self.x, self.lower, color = "b")
        self.ax.plot(self.x, self.y, color = "yellow")
        self.ax.fill_between(self.x, self.upper, self.lower, facecolor='green', alpha = .15)
        
    def add_data(self):
        if len(self.y) > 1:
            self.str1 = Analytics(statistics.stdev(self.y), statistics.stdev(self.y) * statistics.stdev(self.y), self.upper[len(self.upper) - 1] - self.lower[len(self.upper) - 1], max(self.y) - min(self.y), sum(self.y)/len(self.y), self.y[len(self.y) -1] - self.y[len(self.y) -2])
        else:
            self.str1 = Analytics(0, 0, self.upper[len(self.upper) - 1] - self.lower[len(self.upper) - 1], max(self.y) - min(self.y), sum(self.y)/len(self.y), self.y[len(self.y) -1])


    
    def graph_hs(self):
        self.ax.clear()
        self.ax.set_xlabel("Time (s)", fontsize = 7)
        self.ax.set_ylabel(self.y_label)
        self.ax.plot(self.x, self.y, color = "red")
        #Graph_Page.hsConfig(int(self.y[len(self.y) - 1] * 100))
        if (self.y[len(self.y) - 1] * 100 < 99):
            Graph_Page.add_error(str(int(self.y[len(self.y) - 1] * 100)))
        #Graph_Page.pred_maint(int(self.y[len(self.y) - 1] * 10))
    
    def get_value(self):
        return self.y


class Label_Maker:
            def placer(root, x, y, text, font_size, color):
                global font
                if color == "black":
                    Label(root, text=text, font=(font,font_size), fg="black", bg= "white").place(x=x, y=y)
                else:
                    Label(root, text=text, font=(font,font_size), fg="white", bg= "#1c2e4a").place(x=x, y=y)
            
            def packer(root, text, font_size, color, packer):
                if color == "black":
                    Label(root, text=text, font=(font,font_size), fg="black", bg= "white").pack(pady=packer)
                else:
                    Label(root, text=text, font=(font,font_size), fg="white", bg= "#1c2e4a").pack(pady=packer)


class Analytics:
    analytic_Data = ["Std Dev. (over the last 20 values)", "Variance (over the last 20 values)", "Difference between Bounds", "Range (of the last 20 values)",
                        "Average (of the last 20 values)", "Delta (of the last 2 values)"]
    def __init__(self, std, var, dbb, range, avg, delta):
        self.std = std
        self.var = var
        self.dbb = dbb
        self.range = range
        self.avg = avg
        self.delta = delta

    def getStr(self):
        vals = ""
        vals += Analytics.analytic_Data[0]
        vals += ": " + str("%.2f" % self.std)
        vals += "   "

        vals += Analytics.analytic_Data[1]
        vals += ": " + str("%.2f" % self.var)
        vals += "\n"


        vals += Analytics.analytic_Data[2]
        vals += ": " + str("%.2f" % self.dbb)
        vals += "   "

        vals += Analytics.analytic_Data[3]
        vals += ": " + str("%.2f" % self.range)
        vals += "\n"


        vals += Analytics.analytic_Data[4]
        vals += ": " + str("%.2f" % self.avg)
        vals += "   "

        vals += Analytics.analytic_Data[5]
        vals += ": " + str("%.2f" % self.delta)
        vals += "\n"

        return vals

        

    
    

    
    





class MicroAI_App(Tk):

        def __init__(self, *args, **kwargs):
            
            Tk.__init__(self, *args, **kwargs)
            Tk.wm_title(self, "Micro AI Dashboard")            
            self.geometry("2000x900")
            container = Frame(self)
            container.pack(side="top", fill="both", expand = True)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            self.frames = {}

            for F in (Splash, Graph_Page, PageOne):

                frame = F(container, self)
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky="nsew")

            self.show_frame(Splash)

        def show_frame(self, cont):

            frame = self.frames[cont]
            frame.tkraise()



            




class Graph_Page(Frame):

        health_score = 1
        table_canv_label = 0
        message = ""
        pr_label = ""
        label = 7
        root = 0
        switcher = 0
        switch_counter = 0

        an_1 = ""
        an_2 = ""
        an_3 = ""
        an_4 = ""
        an_5 = ""
        an_6 = ""
        
        def __init__(self, parent, controller):
            global health_score
            global table_canv_label
            global pr_label
            global message
            global label
            global root
            global font
            root = self

            global an_1
            global an_2
            global an_3
            global an_4
            global an_5
            global an_6

            message = ""
            Frame.__init__(self, parent, bg="white")
            label = Label(self, text= "Raspberry Pi Monitoring Dashboard", font = (font, 30), bg = "white")
            label.place(x=670, y=0)
            button1 = Button(self, text="Logout", font = (font),
                                command=lambda: controller.show_frame(Login))
            button1.configure(highlightbackground='black', fg='black', bg = "white")
            #button1.place(x=450, y=15)

            button2 = Button(self, text="Settings", font = (font), command=lambda: controller.show_frame(PageOne))
            button2.place(x = 1439, y = 15)
            button2.configure(highlightbackground='black', fg='black', bg = "white")
            
            w = Canvas(self, height=1000, width=1000, background='red')
            canvas = FigureCanvasTkAgg(Main.fig.figs, w)
            canvas.get_tk_widget().configure(background="#1c2e4a")
            canvas.draw()
            canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
            canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
            w.place(x=0, y=100)


            w1 = Canvas(self, height=1000, width=1000, background='red')
            canvas1 = FigureCanvasTkAgg(Main.fig1.figs, w1)
            canvas1.get_tk_widget().configure(background="#1c2e4a")
            canvas1.draw()
            canvas1.get_tk_widget().pack( side=BOTTOM, fill=BOTH, expand=True)

            canvas1._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
            w1.place(x=0, y=570)

            table_canv = Canvas(self, height = 230, width = 885,  highlightbackground="black", bg = "white")
            table_canv.pack_propagate(False)
            table_canv_label = Label(table_canv, bg = "white")
            table_canv_label.pack(pady=5)
            table_canv.place(x=1000, y=605)

            

            cpu_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            cpu_canv.pack_propagate(False)
            Label(cpu_canv, text="1:", bg="white", font = (font, 20)).place(x=5,y=5)

            an_1 = Label(cpu_canv, text="", bg = "white", font=(font, 8))
            an_1.place(x=5, y= 60)

            cpu_canv.place(x=1000,y=140)

            discr_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            discr_canv.pack_propagate(False)
            Label(discr_canv, text="2:", bg="white", font = (font, 20)).place(x=5,y=5)

            an_2 = Label(discr_canv, text="", bg = "white", font=(font, 8))
            an_2.place(x=5, y= 60)

            discr_canv.place(x=1000 + 885/2,y=140)

            discw_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            discw_canv.pack_propagate(False)
            Label(discw_canv, text="3:", bg="white", font = (font, 20)).place(x=5,y=5)

            an_3 = Label(discw_canv, text="", bg = "white", font=(font, 8))
            an_3.place(x=5, y= 60)

            discw_canv.place(x=1000,y=140 + 400/3)

            ram_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            ram_canv.pack_propagate(False)
            Label(ram_canv, text="4:", bg="white", font = (font, 20)).place(x=5,y=5)


            an_4 = Label(ram_canv, text="", bg = "white", font=(font, 8))
            an_4.place(x=5, y= 60)


            ram_canv.place(x=1000 + 885/2,y=140 + 400/3)

            temp_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            temp_canv.pack_propagate(False)
            Label(temp_canv, text="5:", bg="white", font = (font, 20)).place(x=5,y=5)

            an_5 = Label(temp_canv, text="", bg = "white", font=(font, 8))
            an_5.place(x=5, y= 60)


            temp_canv.place(x=1000,y=140 + 400/3 + 400/3)




            load_canv = Canvas(self, height = 400/3, width = 885/2, highlightbackground="black", bg = "white")
            load_canv.pack_propagate(False)


            an_6 = Label(load_canv, text="", bg = "white", font=(font, 8))
            an_6.place(x=5, y= 60)



            Label(load_canv, text="6:", bg="white", font = (font, 20)).place(x=5,y=5)
            load_canv.place(x=1000 + 885/2,y=140 + 400/3 + 400/3)


            

        def hsConfig(texts):
            health_score.config(text=texts)
        
        def add_error(health):
            global message
            global table_canv_label
            if message.count("\n") > 10:
                message = message[message.index("\n") + 1:]
            message += "\n"
            if (PageOne.getName() != ""):
                name = PageOne.getName()
                while len(name) < 13:
                    name += " "
                while len(name) > 12:
                    name = name[0: len(name)]
                message += name + "        Health Score Error        Health Score = " + str(health) + "        " + str(datetime.datetime.now())
            else:
                message += "Raspberry Pi" + "        Health Score Error        Health Score = " + str(health) + "        " + str(datetime.datetime.now())
            table_canv_label.config(text=message)
        
        def pred_maint(health):
            pr_label.config(text= str(health) + " Days")
        
        def get_name():
            global running
            global label
            if (running and PageOne.getName() == ""):
                label.config(text="Raspberry Pi Monitoring Dashboard")
            else:
                label.config(text= PageOne.getName() + " Monitoring Dashboard")
        
        def add_analysis(str1, str2, str3, str4, str5, str6):
            global an_1
            global an_2
            global an_3
            global an_4
            global an_5
            global an_6

            an_1.config(text=str1)
            an_2.config(text=str2)
            an_3.config(text=str3)
            an_4.config(text=str4)
            an_5.config(text=str5)
            an_6.config(text=str6)
            




    
class Splash(Frame):
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)
            self.bg = ImageTk.PhotoImage(file='/home/pi/Pictures/splash_pic.png')
            label = Label(self, image=self.bg)
            label.place(x=0,y=0)
            self.after(5000,lambda:controller.show_frame(Graph_Page))
            

# class Login(Frame):
#         def __init__(self, parent, controller):
#             global font
#             Frame.__init__(self,parent)
#             self.bg = ImageTk.PhotoImage(file='/home/pi/Pictures/MicroAIFactory-1.jpg')
#             label = Label(self, image=self.bg)
#             label.place(x=0,y=0)
#             self.carousel = ImageTk.PhotoImage(file='/home/pi/Pictures/first-carousel.png')
#             bigpic = Label(self,image=self.carousel)
#             bigpic.place(x=100,y=180)
            
#             self.logo = PhotoImage(file='/home/pi/Pictures/Screen Shot 2022-06-22 at 5.19.42 PM.png')
#             label_logo = Label(self, image=self.logo)
#             label_logo.pack()
#             w = Canvas(self, height=564, width=580, background='#1c2e4a')
#             Label_Maker.placer(w, 60, 15, "Please enter your Email and \nPassword to log in:", 25, "white")
#             Label_Maker.placer(w, 60, 130, "Email:", 25, "white")
#             username = Entry(w, width=45)
#             username.place(x=60, y=180)
#             Label_Maker.placer(w, 60, 240, "Password:", 25, "white")
#             password = Entry(w,  show = '*', width=45)
#             password.place(x=60, y=290)
#             button3 = Button(w, text="Login", width=42,highlightbackground= '#1c2e4a',command=lambda: controller.show_frame(Graph_Page),fg='white', bg='#039be5', font=(font))
#             button3.place(x=60, y=370)
#             button4 = Button(w, text="Forgot Password?", width=42,highlightbackground= '#1c2e4a',command=lambda: controller.show_frame(StartPage), font=(font))
#             button4.place(x=60, y=435)
#             button5 = Button(w, text="New User?", width=42,highlightbackground= '#1c2e4a',command=lambda: controller.show_frame(Create_Login), font=(font))
#             button5.place(x=60, y=500)
#             w.place(x=1250,y=180)



class PageOne(Frame):
        name = ""
        def __init__(self, parent, controller):
            global font
            global name
            Frame.__init__(self,parent)
            self.bg = ImageTk.PhotoImage(file='/home/pi/Pictures/MicroAIFactory-1.jpg')
            
            label = Label(self, image=self.bg)
            label.place(x=0,y=0)
            w = Canvas(self, height=500, width=350, background='#1c2e4a')
            Label_Maker.placer(w, 20, 15, "Settings", 20, "white")
            button5 = Button(w, text="Back", font=(font), width=20,highlightbackground= '#1c2e4a',command=lambda: [controller.show_frame(Graph_Page), Graph_Page.get_name()], fg='white', bg='#039be5')
            button5.place(x=60, y=340)
            checker = Checkbutton(w, text="       Email Notification", highlightbackground='#1c2e4a', font=(font,15), bg='#1c2e4a', fg='white')
            checker.place(x=20, y=90)
            Label(w, text="Device Name:", font=(font, 15), bg='#1c2e4a', fg='white').place(x=27, y=160)
            Label_Maker.placer(w, 27, 160, "Device Name:", 15, "white")
            name = Entry(w, width=23)
            name.place(x=28, y=190)
            w.place(x=900,y=180)
        
        def getName():
            return name.get()









class Main: 
    global running
    fig = figMaker(10, 6, 100, "Sensor Data")
    fig.figMaker()
    fig1 = figMaker(10, 3, 100, "Health Score")
    fig1.figMaker()
    def main():
        global running
        running = True
        app = MicroAI_App()
        ani = animation.FuncAnimation(Main.fig.figs, Charts.animate, interval=1000)
        ani1 = animation.FuncAnimation(Main.fig1.figs, Charts.animate1, interval=1000)
        app.mainloop()

class Charts:

    subarray = [1,2,7,8,13,14]
    channelarray = ["c0","c3","c1","c2","c4","c5"]
    titles = ["1: Abnormal Behavior of CPU Usage Percent Over Time","2: Abnormal Behavior of RAM Usage Percent Over Time", "3: Abnormal Behavior of Disc Reads Over Time", 
    "4: Abnormal Behavior of Disc Writes Over Time",
    "5: Abnormal Behavior of Temperature Over Time", "6: Abnormal Behavior of Load Average Over Time"]
    yaxs = ["Percent", "Percent", "Disc Reads", "Disc Writes", "º Fahrenheit", "Number of Cores"]
   
    x = 0 
    subplots = []
    sub1 = subplotMaker(Main.fig1.figs, 1, 1, 1, "HS_1", "Health Score", "Health Score Value (out of 1)")
   

    while (x < 6):
        subplots.append(subplotMaker(Main.fig.figs, 9, 2, subarray[x], channelarray[x], titles[x], yaxs[x]))
        x+=1
        

    def animate(i):
        data = []
        for subplot in Charts.subplots:
            subplot.append_all()
            subplot.graph()
            subplot.add_data()
            data.append(subplot.str1.getStr())
        Graph_Page.add_analysis(data[0], data[1], data[2], data[3], data[4], data[5])
        plt.show()

    def animate1(i):
        Charts.sub1.append_all()
        Charts.sub1.graph_hs()
        plt.show()






if __name__ == "__main__":
    m = Main.main()
