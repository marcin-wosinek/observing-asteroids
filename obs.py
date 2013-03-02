'''
Created on Jan 3, 2013

'''

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime
import StringIO

def getEphemerisMPC(asteroid_id, observatory_code, start_date, step_size, step_type, nr_steps):   
	'''
	(str, str, str, str, str, str) -> None
	Downloads the ephemeris for given asteroid_id, observatory code, starting date,
	and step (specify step size and type).
    
	Precondition: Step type: h for hours, m for minutes, s for seconds.
	Start date has to be in format: year month day, for example "2013 05 01" .
	Always starts computing from noon 12:00.
    
	>> getEphemerisMPC("1", "B31", "2013 05 01", "2", "h", "31")
	% Total	% Received % Xferd  Average Speed   Time	Time 	Time  Current
                             	Dload  Upload   Total   Spent	Left  Speed

	0	73	0	73	0 	0	295  	0 --:--:-- --:--:-- --:--:--   295
	100 13807	0 13807	0 	0  53855  	0 --:--:-- --:--:-- --:--:-- 1490k
	'''
	print "getEphemerisMPC date ", start_date
	year = start_date.split()[0]
	month = start_date.split()[1]
	day = start_date.split()[2]
	import urllib2
	#text = StringIO.StringIO()
    
    
                       	 
	text = urllib2.urlopen("http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea="+asteroid_id+"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+"%20"+day+"&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty=a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0")
	print "http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea="+asteroid_id+"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+"%20"+day+"&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty=a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0"
	#text = urllib2.urlopen("http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea=" + "%0D%0A" +
	#      	asteroid_id +"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+
	#      	"%20"+day+"%2012%3A00&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty="+
	#      	"a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0")
    
#	text.write(os.system("curl 'http://scully.cfa.harvard.edu/cgi-bin/mpeph2.cgi?TextArea=" + "%0D%0A" +
#          	asteroid_id +"&adir=S&alt=&bu=&c="+observatory_code+"&ce=f&ch=c&d="+year+"%20"+month+
#          	"%20"+day+"%2012%3A00&e=-2&i="+step_size+"&js=f&l="+nr_steps+"&lat=&long=&m=m&oed=&raty="+
#          	"a&resoc=&s=t&tit=&ty=e&u="+step_type+"&uto=0'"))
    
   #
    
	return text
	#os.system("mv mpc.eph.html " + asteroid_id + ".html")
    
    

def readAltitude(text):    
    
	altitude = []
	dates = []
    
	SOE = False # start of ephemeris
	EOE = False # end of ephemeris
	ready = False
    
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
       	 
        	if(int(hours)>16):
            	altitude.append(float(next.split()[18]))
            	dates.append(datetime.datetime(year, month, day, hour=hours, minute=minutes))
       	 
       	 
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
	asteroid_IDs = "1 2 3".split()
 
	print "obs_date", obs_date
    
	plots = []
	try:
    	for current in chunk(asteroid_IDs, 10):
        	fig = plt.figure()
        	ax = fig.add_subplot(111)
   	 
        	import matplotlib.dates as mdates
        	date = []
        	for asteroid in current:
           	 
         	#   print asteroid
            	dates, altitudes = readAltitude(getEphemerisMPC(asteroid, obs_code, obs_date+" 17:00", "1", "m", "5")) #780
            	#dates, altitudes = readAltitude(asteroid+".html")
            	alt = altitudes[::30]
            	maxalt = max(alt)
            	maxdate = dates[altitudes.index(maxalt)]
            	ax.text(maxdate, maxalt, asteroid, color="black", weight='bold', size=10)
           	 
            	plt.plot_date(dates[::30], altitudes[::30], linestyle='dashed', label=asteroid, color="red")
            	date = dates[0]
       	 
            	print date
        	#plt.legend()
        	plt.grid(True)
        	plt.title("Visibility plot for observatory code " + obs_code)
        	#plt.xlabel("Universal time, starting night " + str(date))
        	plt.xlabel("Universal time, starting night " + obs_date + " " + str(dates[1]))
        	plt.ylabel("Altitude [degrees]")
        	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
       	 
        	from matplotlib.ticker import MaxNLocator
        	ax.xaxis.set_major_locator(MaxNLocator(10))
        	ax.set_ylim(bottom = 0)
        	ax.set_ylim(top = 95)
        	fig.autofmt_xdate(rotation=25)
       	# imgdata = StringIO.StringIO()
       	# fig.savefig(imgdata, format='svg')
       	# imgdata.seek(0)  # rewind the data
        	#svg_dta = imgdata.buf  # this is svg data
        	rv = StringIO.StringIO()
        	plt.savefig(rv, format="svg")
        	plots.append(rv.getvalue().partition("-->")[-1])
    	return plots
	finally:
    	plt.clf()


plots = plot_svg()
