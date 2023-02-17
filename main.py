'''
TODO:
1. add album downloader (no cache, dont bother, maybe mark individual songs, though) 
2. let @LiamDonohue know i added it in the comments of my post
3. fix poorly implemented cache - two input boxes for song name & artist name, search
4. better cache view - rename to fast downloads idk searchable
'''

from flask import Flask, request, send_file, jsonify, Response, stream_with_context
from flask_cors import CORS
from youtube_search import YoutubeSearch
import os, uuid, urllib, requests

os.system("python3 -m pip install spotdl youtube_dl")

cache = {}

folders = os.listdir(".")
for folder in folders:
    try:
        for fn in os.listdir(folder):
            if fn.endswith(".m4a") or fn.endswith(".mp3"):
                s = fn.split(".")[0].lower()
                cache[s] = folder+"/"+fn
    except NotADirectoryError:
        pass

def getsong(s, yt=False):
    global cache
    if s in cache:
        return cache[s]
    else:
        if yt:
            fn = download_yt(s)
        else:
            fn = download(s)
        cache[s] = fn
        return fn

def download(s):
    d = ''.join(str(uuid.uuid4()).split("-"))
    os.mkdir(d)
    os.system('spotdl "%s" --overwrite skip -f %s' % (s,d))
    fn = d+"/"+os.listdir(d)[0]
    return fn

def download_yt(id):
    d = ''.join(str(uuid.uuid4()).split("-"))
    os.mkdir(d)
    os.system('youtube-dl --extract-audio --audio-format m4a "https://youtube.com/watch?v=%s" -o %s' % (id, '%s/%s.m4a' % (d, id)))
    fn = d+"/"+os.listdir(d)[0]
    return fn

app = Flask(__name__)
CORS(app)

@app.route("/")
def app_index():
    return send_file("index.html")

@app.route("/download", methods=['GET','POST'])
def app_download():
    s = request.form.get("s") or request.args.get("s")
    if s is None:
        return "err: no song specified, arg name 's'"
    fn = getsong(s.lower())
    return send_file(fn, attachment_filename=fn, as_attachment=True)

@app.route('/download/id', methods=['GET', 'POST'])
def app_download_id():
    s = request.form.get('s') or request.args.get('s')
    if s is None:
        return 'err: no song specified, arg name "s"'
    fn = getsong(s, yt=True)
    return send_file(fn, attachment_filename=fn, as_attachment=True)

@app.route("/cache")
def app_cache():
    return '<br>\n'.join([
        ("<a href='https://spotdl.marcusweinberger.repl.co/download?s=%s'>%s</a>" % (urllib.parse.quote(x,safe=''),x))
    for x in cache])

@app.route('/search')
def app_search():
    q = request.args.get('q')
    if not q:
        return 'q=?'
    
    f = int(request.args.get('from', '0'))
    t = int(request.args.get('to', '20'))

    res = YoutubeSearch(q, max_results=t).to_json()[f:]
    return jsonify(res)

@app.route('/img')
def app_img():
    url = request.args.get('u')
    if not url:
        return 'u=?'
    if not url.startswith('https://i.ytimg.com'):
        return 'u=https://i.ytimg.com/*'
    
    r = requests.get(url, stream=True)
    return Response(stream_with_context(r.iter_content(chunk_size=2048)), headers=dict(r.headers))


app.run(host="0.0.0.0", port=8080) if __name__ == "__main__" else None