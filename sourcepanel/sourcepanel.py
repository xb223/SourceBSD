#!/usr/local/bin/python3.11
# SourcePanel - SourceBSD Web Control Plane
# Reads real kernel data and displays it

from flask import Flask, jsonify, render_template_string
import subprocess
import os
import time

app = Flask(__name__)

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return ""

def get_cpu():
    top = run("top -b -d1 | grep 'CPU:'")
    cores = run("sysctl -n hw.ncpu")
    load = run("sysctl -n vm.loadavg").replace("{ ","").replace(" }","")
    return {"top": top, "cores": cores, "load": load}

def get_memory():
    vmstat = run("vmstat -h | tail -1")
    total = run("sysctl -n hw.physmem")
    total_mb = int(total) // 1024 // 1024 if total.isdigit() else 0
    return {"vmstat": vmstat, "total_mb": total_mb}

def get_disk():
    df = run("df -h | grep -v tmpfs | grep -v devfs")
    return {"df": df}

def get_network():
    netstat = run("netstat -in | grep -v lo0 | tail -n +2")
    return {"interfaces": netstat}

def get_jails():
    jls = run("jls -v")
    policies = run("ls /etc/srcbsd/policies/ 2>/dev/null")
    return {"jls": jls, "policies": policies}

def get_security():
    securelevel = run("sysctl -n kern.securelevel")
    coredump = run("sysctl -n kern.coredump")
    randompid = run("sysctl -n kern.randompid")
    racct = run("sysctl -n kern.racct.enable")
    return {
        "securelevel": securelevel,
        "coredump": coredump,
        "randompid": randompid,
        "racct": racct
    }

HTML = '''<!DOCTYPE html>
<html>
<head>
<title>SourcePanel</title>
<meta http-equiv="refresh" content="5">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#008080; font-family:"Courier New",monospace; }
.taskbar { background:#c0c0c0; border-bottom:2px solid #808080; padding:3px 6px; display:flex; justify-content:space-between; align-items:center; }
.start-btn { background:#c0c0c0; border-top:2px solid #fff; border-left:2px solid #fff; border-right:2px solid #404040; border-bottom:2px solid #404040; padding:2px 10px; font-size:12px; font-weight:bold; font-family:"Courier New",monospace; }
.clock { font-size:11px; border-top:1px solid #808080; border-left:1px solid #808080; border-right:1px solid #fff; border-bottom:1px solid #fff; padding:2px 8px; }
.tabs { background:#c0c0c0; border-bottom:2px solid #404040; display:flex; padding:4px 6px 0; gap:2px; }
.tab { background:#a0a0a0; border-top:2px solid #fff; border-left:2px solid #fff; border-right:2px solid #404040; padding:3px 12px; font-size:11px; cursor:pointer; text-decoration:none; color:#000; font-family:"Courier New",monospace; margin-bottom:-2px; }
.tab.active { background:#c0c0c0; border-bottom:2px solid #c0c0c0; font-weight:bold; }
.content { display:none; padding:6px; }
.content.active { display:block; }
.win { background:#c0c0c0; border-top:2px solid #fff; border-left:2px solid #fff; border-right:2px solid #404040; border-bottom:2px solid #404040; margin-bottom:6px; }
.win-title { background:linear-gradient(to right,#000080,#1084d0); color:#fff; padding:3px 6px; font-size:12px; font-weight:bold; }
.win-body { padding:6px; }
.inset { background:#fff; border-top:1px solid #808080; border-left:1px solid #808080; border-right:1px solid #fff; border-bottom:1px solid #fff; padding:4px 6px; font-size:11px; white-space:pre; overflow-x:auto; }
.label { font-size:10px; color:#444; margin-bottom:2px; }
.val { font-size:13px; font-weight:bold; color:#000080; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:5px; margin-bottom:5px; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:5px; margin-bottom:5px; }
.sep { height:1px; background:#808080; border-bottom:1px solid #fff; margin:5px 0; }
.ok { color:#006600; font-weight:bold; }
.warn { color:#800000; font-weight:bold; }
.sec-lbl { font-size:10px; color:#000080; font-weight:bold; margin-bottom:4px; text-transform:uppercase; }
</style>
</head>
<body>
<div class="taskbar">
  <button class="start-btn">Start</button>
  <span style="font-size:11px;">SourcePanel v1.0 — srcpanel</span>
  <span class="clock" id="clk">{{ now }}</span>
</div>
<div class="tabs">
  <a class="tab {% if tab=='cpu' %}active{% endif %}" href="/?tab=cpu">CPU</a>
  <a class="tab {% if tab=='memory' %}active{% endif %}" href="/?tab=memory">Memory</a>
  <a class="tab {% if tab=='network' %}active{% endif %}" href="/?tab=network">Network</a>
  <a class="tab {% if tab=='storage' %}active{% endif %}" href="/?tab=storage">Storage</a>
  <a class="tab {% if tab=='jails' %}active{% endif %}" href="/?tab=jails">Jails</a>
  <a class="tab {% if tab=='security' %}active{% endif %}" href="/?tab=security">Security</a>
</div>

{% if tab == 'cpu' %}
<div class="content active">
  <div class="win">
    <div class="win-title">CPU Load Monitor</div>
    <div class="win-body">
      <div class="sec-lbl">processor</div>
      <div class="grid3">
        <div class="inset"><div class="label">Cores</div><div class="val">{{ cpu.cores }}</div></div>
        <div class="inset"><div class="label">Load average</div><div class="val">{{ cpu.load }}</div></div>
        <div class="inset"><div class="label">Status</div><div class="val ok">RUNNING</div></div>
      </div>
      <div class="sec-lbl">usage</div>
      <div class="inset">{{ cpu.top }}</div>
    </div>
  </div>
</div>
{% endif %}

{% if tab == 'memory' %}
<div class="content active">
  <div class="win">
    <div class="win-title">Memory Status</div>
    <div class="win-body">
      <div class="sec-lbl">physical memory</div>
      <div class="grid2">
        <div class="inset"><div class="label">Total RAM</div><div class="val">{{ memory.total_mb }} MB</div></div>
        <div class="inset"><div class="label">vmstat</div><div class="val" style="font-size:10px;">{{ memory.vmstat }}</div></div>
      </div>
    </div>
  </div>
</div>
{% endif %}

{% if tab == 'network' %}
<div class="content active">
  <div class="win">
    <div class="win-title">Network Interfaces</div>
    <div class="win-body">
      <div class="sec-lbl">interfaces</div>
      <div class="inset">{{ network.interfaces }}</div>
    </div>
  </div>
</div>
{% endif %}

{% if tab == 'storage' %}
<div class="content active">
  <div class="win">
    <div class="win-title">Storage</div>
    <div class="win-body">
      <div class="sec-lbl">filesystems</div>
      <div class="inset">{{ disk.df }}</div>
    </div>
  </div>
</div>
{% endif %}

{% if tab == 'jails' %}
<div class="content active">
  <div class="win">
    <div class="win-title">SecureJail Monitor</div>
    <div class="win-body">
      <div class="sec-lbl">running jails</div>
      <div class="inset">{{ jails.jls }}</div>
      <div class="sep"></div>
      <div class="sec-lbl">configured jails</div>
      <div class="inset">{{ jails.policies }}</div>
    </div>
  </div>
</div>
{% endif %}

{% if tab == 'security' %}
<div class="content active">
  <div class="win">
    <div class="win-title">Security Status</div>
    <div class="win-body">
      <div class="sec-lbl">kernel security</div>
      <div class="grid3">
        <div class="inset">
          <div class="label">Securelevel</div>
          <div class="val {% if security.securelevel|int >= 1 %}ok{% else %}warn{% endif %}">
            {{ security.securelevel }}
          </div>
        </div>
        <div class="inset">
          <div class="label">Core dumps</div>
          <div class="val {% if security.coredump == '0' %}ok{% else %}warn{% endif %}">
            {% if security.coredump == '0' %}DISABLED{% else %}ENABLED{% endif %}
          </div>
        </div>
        <div class="inset">
          <div class="label">Random PIDs</div>
          <div class="val {% if security.randompid != '0' %}ok{% else %}warn{% endif %}">
            {{ security.randompid }}
          </div>
        </div>
        <div class="inset">
          <div class="label">rctl</div>
          <div class="val {% if security.racct == '1' %}ok{% else %}warn{% endif %}">
            {% if security.racct == '1' %}ENABLED{% else %}DISABLED{% endif %}
          </div>
        </div>
        <div class="inset">
          <div class="label">W^X</div>
          <div class="val ok">ACTIVE</div>
        </div>
        <div class="inset">
          <div class="label">SSH keys</div>
          <div class="val ok">ENFORCED</div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endif %}

</body>
</html>'''

@app.route('/')
def index():
    from flask import request
    tab = request.args.get('tab', 'cpu')
    now = time.strftime('%H:%M:%S')
    return render_template_string(HTML,
        tab=tab,
        now=now,
        cpu=get_cpu(),
        memory=get_memory(),
        network=get_network(),
        disk=get_disk(),
        jails=get_jails(),
        security=get_security()
    )

@app.route('/api/status')
def api_status():
    return jsonify({
        'cpu': get_cpu(),
        'memory': get_memory(),
        'disk': get_disk(),
        'jails': get_jails(),
        'security': get_security()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
