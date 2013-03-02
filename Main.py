'''
Created on Dec 30, 2012

'''


#!/usr/bin/python
import logging, os, StringIO, cgi
try: import webapp2
except: pass  # when ran directly from command line
import subprocess
def no_popen(*args, **kwargs): raise OSError("forbjudet")
subprocess.Popen = no_popen  # not allowed in GAE, missing from module
subprocess.PIPE = None
subprocess.STDOUT = None
os.environ["MATPLOTLIBDATA"] = os.getcwdu()  # own matplotlib data
os.environ["MPLCONFIGDIR"] = os.getcwdu()    # own matplotlibrc
import numpy, matplotlib, matplotlib.pyplot as plt
import datetime

def getEphemerisMPC(asteroid_id, observatory_code, start_date, step_size, step_type, nr_steps):   
    '''
    (str, str, str, str, str, str) -> None
    Downloads the ephemeris for given asteroid_id, observatory code, starting date,
    and step (specify step size and type). 
    
    Precondition: Step type: h for hours, m for minutes, s for seconds.
    Start date has to be in format: year month day, for example "2013 05 01" .
    Always starts computing from noon 12:00.
    
    >> getEphemerisMPC("1", "B31", "2013 05 01", "2", "h", "31")
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed

    0    73    0    73    0     0    295      0 --:--:-- --:--:-- --:--:--   295
    100 13807    0 13807    0     0  53855      0 --:--:-- --:--:-- --:--:-- 1490k
    '''
    year = start_date.split()[0]
    month = start_date.split()[1]
    day = start_date.split()[2]
    import urllib2
    #text = StringIO.StringIO()
 
    text = urllib2.urlopen("http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea="+asteroid_id+"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+"%20"+day+"&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty=a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0")
#    text = urllib2.urlopen("http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea=" + "%0D%0A" + 
#              asteroid_id +"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+
#              "%20"+day+"%2012%3A00&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty="+
#              "a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0")
    
#    text.write(os.system("curl 'http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea=" + "%0D%0A" + 
#              asteroid_id +"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+
#              "%20"+day+"%2012%3A00&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty="+
#              "a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0'"))
    
   #
    
    return text
    #os.system("mv mpc.eph.html " + asteroid_id + ".html")
    
    

def readAltitude(text):    
    
    altitude = []
    dates = []
    
    SOE = False # start of ephemeris
    EOE = False # end of ephemeris
    ready = False
    
    days = []
    cnt = 0
    for next in text:
       # print line
        if next.__contains__("h m s"):
            SOE = True
        if next.__contains__("</pre>"):
            EOE = True
        if(SOE and not EOE and ready):
            
            year = int(next.split()[0])
            month = int(next.split()[1])
            day = int(next.split()[2])
            hours = int(next.split()[3][0:2])
            minutes = int(next.split()[3][2:4])
            
            if cnt==0:
                days.append(day)
            if(int(hours)>16 or day not in days):
                altitude.append(float(next.split()[18]))
                dates.append(datetime.datetime(year, month, day, hour=hours, minute=minutes))
            cnt = cnt + 1
            
        elif(SOE and not EOE and not ready):
            ready = True     
        if(EOE):
            text.close()
            return dates, altitude   
            
        
def chunk(array, size):
    while array:
        tmp, array = array[:size], array[size:]
        yield tmp
        
        
def plot_svg():        
    #now = datetime.datetime.gmtime()
    now = datetime.datetime.now()
    #print now
    obs_date = str(now.year) + " " + str(now.month) + " " + str(now.day)  
    obs_code = "950"
    asteroid_IDs = "1 2 3 4 5 6 7 8 9 19 37 76 98 77 15 98 76 66".split()
  
    plots = []
    try:
        for current in chunk(asteroid_IDs, 10):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
            import matplotlib.dates as mdates
            date = []
            for asteroid in current:
                
             #   print asteroid
                dates, altitudes = readAltitude(getEphemerisMPC(asteroid, obs_code, obs_date+" 17:00", "1", "m", "2000")) #780
                #dates, altitudes = readAltitude(asteroid+".html")
                alt = altitudes[::30]
                maxalt = max(alt)
                maxdate = dates[altitudes.index(maxalt)]
                ax.text(maxdate, maxalt, asteroid, color="black", weight='bold', size=10)
                
                plt.plot_date(dates[::30], altitudes[::30], linestyle='dashed', label=asteroid, color="red")
                date = dates[0]
            
            #plt.legend()
            plt.grid(True)
            plt.title("Visibility plot for observatory code " + obs_code)
            #plt.xlabel("Universal time, starting night " + str(date))
            plt.xlabel("Universal time, starting night " + str(dates[0]))
            plt.ylabel("Altitude [degrees]")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            from matplotlib.ticker import MaxNLocator 
            ax.xaxis.set_major_locator(MaxNLocator(10)) 
            ax.set_ylim(bottom = 0)
            ax.set_ylim(top = 95)
            fig.autofmt_xdate(rotation=25)
           # imgdata = StringIO.StringIO()
           # fig.savefig(imgdata, format='svg')
           # imgdata.seek(0)  # rewind the data
            #svg_dta = imgdata.buf  # this is svg data
            rv = StringIO.StringIO()
            plt.savefig(rv, format="svg")
            plots.append(rv.getvalue().partition("-->")[-1])
        return plots
    finally:
        plt.clf()

if __name__ != "__main__":
    class MainHandler(webapp2.RequestHandler):
        
        def get(self):
            
            
            self.response.write("""<html><head><title>Visibility plots of target asteroids </title></head><body>""")
            
            asteroid_IDs = "1 2".split()
            now = datetime.datetime.now()
            
            self.response.write("Asteroid ephemerides for the NOT for today, that is " + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "<br>")
            
            
            #self.response.write("<table border="'1'"><tr><td>Asteroid ID</td><td>Ephemeris</td></tr></table>")
                
            self.response.write("<br>")
            for asteroid in asteroid_IDs:
                link = "http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea="+asteroid+"&adir=S&alt=&bu=&c="+"950"+"&ce=f&ch=c&d="+str(now.year)+"%20"+str(now.month)+"%20"+str(now.day)+"&e=-2&i="+"1"+"&js=f&l="+"1980"+"&lat=&long=&m=m&oed=&raty=a&resoc=&s=t&tit=&ty=e&u="+"m"+"&uto=0"
                
                
                

                self.response.write(asteroid + "<a href="+link+">"+" ephemeris"+"</a><br>")

            plots = plot_svg()
            for plot in plots:
                self.response.write(plot)
            #self.response.write("<pre>%s</pre>" % cgi.escape(file(__file__.rstrip("c")).read()))  # source, dev runs .py, gae runs .pyc
            
            self.response.write("""</body> </html>""")


        
                
               # link = "http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea="+asteroid+"&adir=S&alt=&bu=&c="+"950"+"&ce=f&ch=c&d="+now.year+"%20"+now.month+"%20"+now.day+"&e=-2&i="+"1"+"&js=f&l="+"6440"+"&lat=&long=&m=m&oed=&raty=a&resoc=&s=t&tit=&ty=e&u="+"m"+"&uto=0"
               # <a href="http://www.hyperlinkcode.com">Hyperlink Code</a> 
 

    app = webapp2.WSGIApplication([
        ('/', MainHandler)
    ], debug=True)

            
                
#class MainPage(webapp2.RequestHandler):
#  
#  def get(self):
#      
#      self.response.headers['Content-Type'] = 'text/html'
#      self.response.write(plot_svg())
#
#app = webapp2.WSGIApplication([('/', MainPage)],
#                              debug=True)
