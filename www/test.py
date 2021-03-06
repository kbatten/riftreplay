#!/usr/bin/env python

import zlib
import os
import json
import uuid
import base64
import struct
import StringIO
import re
import struct

import tornado.ioloop
import tornado.web
import couchdb

import fastlz
from rift import combatlog

upload_root="./upload"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.html").read())


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        len_wire = len(self.request.body)
        len_data = 0

        # log is base64/fastlz compressed
        logname = 'log-' + str(uuid.uuid4())
        log = ""

        boundary = "yyyyyyyyyyyyyyyyyyyyyyy"

        mime = self.request.body.split("--" + boundary)

        index = 1
        total = 0
        for m in mime:
            part = re.match("\r\nContent-Disposition: form-data; name=\"Filedata\"; filename=\"([0-9]+)/([0-9]+)\"\r\nContent-Type: application/octet-stream\r\n\r\n([0-9a-zA-Z\+/=]+)\r\n", m, re.M)
            if part:
                if int(part.group(1)) != index:
                    raise IndexError
                index += 1
                total = int(part.group(2))
                decoded = base64.b64decode(part.group(3))
                size = struct.unpack(">I", decoded[:4])[0]
                checksum = struct.unpack(">I", decoded[4:8])[0]
                # zlib.adler32 returns a signed checksum
                if checksum > 2147483647:
                    checksum -= 4294967296
                compressed = decoded[8:]
                uncompressed = fastlz.decompress(compressed, size)
                if zlib.adler32(uncompressed) != checksum:
                    raise IndexError ("checksum error")
                log += uncompressed
                len_data += len(uncompressed)

        if (index-1) != total:
            raise IndexError

        if len_data:
            print "compression: " + `len_wire` + "/" + `len_data` + " = " + `int(100.0 * float(len_wire)/float(len_data))` + "%"
        else:
            print "compression: " + `len_wire` + "/" + `len_data` + " = inf%"

        cl = combatlog.combatlog(name=logname, create=True, overwrite=True)
        cl.store(log)
#        cl.update_index()

        self.finish(logname)


class ResultsHandler(tornado.web.RequestHandler):
    def get(self, logname):
        cl = combatlog.combatlog(name=logname, create=False)
        cl.update_index()

        player_id = cl.get_player_id()
        player_name = cl.get_name(player_id)

        self.write("<p>/results/" + logname + "/[friend_id]/[enemy_id]</p>")

        self.write("<p><b>Friendlies</b></br>")
        for actor_id in cl.get_friend_ids(player_id):
            self.write(cl.get_name(actor_id) + " : " + actor_id + "</br>")
        self.write("</p>")

        self.write("<p><b>Enemies</b></br>")

        self.write("<a href='/results/" + logname + "/"+player_id+"/0'>")
        self.write("all</br>")
        self.write("</a>")

        for actor_id in cl.get_enemy_ids(player_id):
            self.write("<a href='/results/" + logname + "/"+player_id+"/"+actor_id+"'>")
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


        if enemy_id == "0":
            enemy_id = friend_id

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
            if enemy_id == friend_id:
                dps = cl.get_dps_by_time(friend_id, None, None, 200)
            else:
                dps = cl.get_dps_by_enemy_id(friend_id, enemy_id, 200)
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

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
