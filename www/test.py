#!/usr/bin/env python

import zlib
import gzip
import os
import json
import uuid
import base64
import struct
import StringIO

import tornado.ioloop
import tornado.web
import couchdb

from rift import combatlog

upload_root="/home/ubuntu/upload"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.html").read())


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        # log is zlib compressed (unfortunately missing headers and crd) and then base64 encoded
        logname = 'log-' + str(uuid.uuid4())
        f = open(os.path.join(upload_root,logname), "w")

        parts = self.request.body.split(chr(13)+chr(10)+chr(13)+chr(10))
        # for now, just assume the data is in the third part
        compressed_b64 = (self.request.body.split(chr(13)+chr(10)+chr(13)+chr(10))[2]).split("\r\n--")[0]
        compressed = base64.b64decode(compressed_b64)

        # http://www.velocityreviews.com/forums/t696109-zlib-correct-checksum-but-error-decompressing.html
        uncompressed = zlib.decompress(compressed, -15)

        f.write(uncompressed)

        len_wire = len(self.request.body)
        len_data = len(uncompressed)
        print "compression: " + `len_wire` + "/" + `len_data` + " = " + `round(100.0 * float(len_wire)/float(len_data),2)` + "%"

        self.finish(logname)


class ResultsHandler(tornado.web.RequestHandler):
    def get(self, logname):
        cl = combatlog.combatlog(name=logname, create=True, overwrite=True)
        cl.store(file(os.path.join(upload_root,logname)).read())
        cl.update_index()

        player_id = cl.get_player_id()
        player_name = cl.get_name(player_id)

        self.write("<p>http://riftreplay.com:8888/results/" + logname + "/[friend_id]/[enemy_id]</p>")

        self.write("<p><b>Friendlies</b></br>")
        for actor_id in cl.get_friend_ids(player_id):
            self.write(cl.get_name(actor_id) + " : " + actor_id + "</br>")
        self.write("</p>")

        self.write("<p><b>Enemies</b></br>")
        for actor_id in cl.get_enemy_ids(player_id):
            self.write("<a href='http://riftreplay.com:8888/results/" + logname + "/"+player_id+"/"+actor_id+"'>")
            self.write(cl.get_name(actor_id) + " : " + actor_id + "</br>")
            self.write("</a>")
        self.write("</p>")

class GraphHandler(tornado.web.RequestHandler):
    def header(self):
        self.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Rift Replay</title>
  <!--[if lte IE 8]><script language="javascript" type="text/javascript" src="/static/flot/excanvas.min.js"></script><![endif]-->
  <script language="javascript" type="text/javascript" src="/static/flot/jquery.js"></script>
  <script language="javascript" type="text/javascript" src="/static/flot/jquery.flot.js"></script>
 </head>
 <body>""")

    def footer(self):
        self.write("""
 </body>
</html>
""")

    def get(self, logname, friend_id, enemy_id):
        self.header()
        

        cl = combatlog.combatlog(name=logname)

        friend_name = cl.get_name(friend_id)
        enemy_name = cl.get_name(enemy_id)

        self.write("<p><b>" + friend_name + " vs " + enemy_name + "</b></p>")
        self.write('<div id="graph_' + enemy_id + '" style="width:600px;height:300px;"></div>')

        self.write("""
<script type="text/javascript">
$(function () {
    var options = {
        lines: { show: true },
        points: { show: false },
        xaxis: { tickDecimals: 0 }
}
""")
#        for enemy_id in cl.get_enemy_ids(friend_id):
        for enemy_id in [enemy_id]:
            dps = cl.get_dps(friend_id, enemy_id, 200)
            self.write("""
    var d = """ + `dps` + """;
    $.plot($("#graph_""" + enemy_id + """"), [ d ], options);
""")

        self.write("""
});
</script>
""")

        self.footer()


if __name__ == "__main__":
    settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

    application = tornado.web.Application(
                [
                    (r"/", MainHandler),
                    (r"/upload", UploadHandler),
                    (r"/results/([-a-z0-9]+)", ResultsHandler),
                    (r"/results/([-a-z0-9]+)/([0-9]+)/([0-9]+)", GraphHandler),
                    ],
                **settings)

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
