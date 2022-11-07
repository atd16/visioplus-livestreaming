from flask import Flask, Response, request
from flask_caching import Cache
import get_meetings
import subprocess
import shlex
import psutil
import random
import unidecode

cache = Cache()
app = Flask(__name__)

cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': '/tmp', 'CACHE_DEFAULT_TIMEOUT': 0})

cache.set("rooms", {})

@app.route('/stream/start/<roomid>', methods = ['POST'])
def start(roomid):
	bbb_stream_url = request.form.get('url')
	if not bbb_stream_url:
		return "No URL"

	rooms = cache.get("rooms")

	for rid in rooms:
		if rid == roomid:
			return "Already running" 
		if rooms[rid]['url'] == bbb_stream_url:
			return "URL already in use"

	bbb_url = "https://visioplus.atd16.fr/bigbluebutton/"
	bbb_api_url = bbb_url+"api/"
	bbb_meeting_id = roomid
	bbb_secret = "2UdcpGNnjp4L49AXSYaqTgI4nwBI1FbJJ5TKrX3a0"
	meeting = get_meetings.get_meeting(bbb_url, bbb_secret, roomid)	
	bbb_meeting_title = unidecode.unidecode(meeting["meetingName"])
	bbb_user_name = "LIVE"
	
	canal_ok = False
	while canal_ok == False:
		canal = random.randint(99,199)
		canal_ok = True
		for rid in rooms:
			if rooms[rid]['canal'] == canal:
				canal_ok = False	

	cmd = 'xvfb-run -n '+str(canal)+' --server-args="-screen 0 1920x1080x24" python3 /usr/src/app/stream.py -s '+bbb_api_url+' -p '+bbb_secret+' -i "'+bbb_meeting_id+'" -u "'+bbb_user_name+'" -r "1920x1080" --browser-disable-dev-shm-usage -T "'+bbb_meeting_title+'" -l -t '+bbb_stream_url+' --canal '+str(canal)

	proc = subprocess.Popen(shlex.split(cmd))
	pid = proc.pid
	rooms[roomid] = {}
	rooms[roomid]['pid'] = pid
	rooms[roomid]['url'] = bbb_stream_url
	rooms[roomid]['canal'] = canal
	print(rooms)
	cache.set("rooms", rooms)
	return "Processing"

@app.route('/stream/stop/<roomid>', methods=['POST'])
def stop(roomid):
	rooms = cache.get("rooms")
	if roomid not in rooms:
		return "Not running"	
	pid = rooms[roomid]['pid']
	if isinstance(pid, int):
		print(pid)
		p = psutil.Process(pid)
		for proc in p.children(recursive=True):
			proc.kill()
		p.kill()
		del rooms[roomid]
		cache.set("rooms", rooms)
		return "Stopped"
	return "Error"
