#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe Sysinfo - https://github.com/rmed/zoe-sysinfo
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.)

import sys
sys.path.append('./lib')

import base64
import psutil
import zoe
from datetime import datetime
from zoe.deco import *


HTML_HEADER = """
<html>
<head>
<style>
h2 {
    border-bottom: 1px solid #CCCCCC;
    margin-top: 20px;
    width: 100%;
}

table {
    border-collapse: separate;
    border-spacing: 5px;
}
</style>
</head><body>"""
HTML_FOOTER = "</body></html>"


@Agent(name="sysinfo")
class Sysinfo:

    @Message(tags=["report"])
    def complete_report(self, sender, src):
        """ Send a complete report to user by mail. """
        HTML = "" + HTML_HEADER

        # CPU
        cpu_html = "<h2>CPU Information</h2><ul>"
        cpu_info = self.gather_cpu()

        for cpu in cpu_info.keys():
            info = cpu_info[cpu]

            cpu_html += """
                <li>%s<ul>
                    <li>User: %s %%</li>
                    <li>System: %s %%</li>
                    <li>Idle: %s %%</li>
                </ul></li>""" % (
                    cpu.upper(), str(info["user"]),
                    str(info["system"]), str(info["idle"]))

        cpu_html += "</ul>"

        # Disks
        disk_html = "<h2>Disk Information</h2><ul>"
        disk_info = self.gather_disk()

        for disk in disk_info.keys():
            info = disk_info[disk]
            usage = disk_info[disk]["usage"]

            disk_html += """
                <li>%s<ul>
                    <li>Mount point: %s</li>
                    <li>Filesystem: %s</li>
                    <li>Options: %s</li>
                    <li>Usage:<ul>
                        <li>Total: %s</li>
                        <li>Used: %s</li>
                        <li>Free: %s</li>
                        <li>Percentage used: %s %%</li>
                    </ul></li>
                </ul></li>""" % (
                    disk,
                    info["mountpoint"],
                    info["fstype"],
                    info["opts"],
                    self.size_fmt(usage["total"]),
                    self.size_fmt(usage["used"]),
                    self.size_fmt(usage["free"]),
                    str(usage["percentage"]))

        disk_html += "</ul>"

        # Memory
        mem_html = "<h2>Memory Information</h2><ul>"
        mem_info = self.gather_memory()

        for mem_type in mem_info.keys():
            info = mem_info[mem_type]

            mem_html += """
                <li>%s<ul>
                    <li>Total: %s</li>
                    <li>Free: %s</li>
                    <li>Used: %s</li>
                    <li>Percentage used: %s</li>
                </ul></li>""" % (
                    mem_type.title(),
                    self.size_fmt(info["total"]),
                    self.size_fmt(info["free"]),
                    self.size_fmt(info["used"]),
                    str(info["percentage"]))

        mem_html += "</ul>"

        # Processes
        proc_html = "<h2>Running processes Information</h2><table>"
        proc_html += """<tr>
            <th>PID</th>
            <th>Name</th>
            <th>User</th>
            <th>Status</th>
            <th>Exec</th>
            <th>Resident Memory</th>
            <th>Virtual Memory</th></tr>"""
        proc_info = self.gather_proc()

        for proc in proc_info.keys():
            info = proc_info[proc]

            proc_html += """<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td></tr>""" % (
                    str(proc),
                    str(info["name"]),
                    str(info["username"]),
                    str(info["status"]),
                    str(info["exe"]),
                    self.size_fmt(info["memory"]["resident"]),
                    self.size_fmt(info["memory"]["virtual"]))

        proc_html += "</table>"

        HTML += cpu_html + disk_html + mem_html + proc_html + HTML_FOOTER

        attachment = self.attach_html(HTML)

        return (self.feedback("Generating report...", sender, src),
                self.feedback(attachment, sender, "mail"))

    @Message(tags=["cpu"])
    def info_cpu(self, sender, src):
        """ Send basic information on CPU usage jabber or Telegram. """
        cpu_info = self.gather_cpu()

        msg = "CPU usage (%s)\n" % self.current_datetime()

        for cpu in cpu_info.keys():
            info = cpu_info[cpu]

            msg += """  %s  
                --------
                User: %s %%
                System: %s %%
                Idle: %s %%\n\n""" % (
                    cpu.upper(), str(info["user"]), str(info["system"]),
                    str(info["idle"]))

        return self.feedback(msg, sender, src)

    @Message(tags=["disk"])
    def info_disk(self, sender, src):
        """ Send basic information on disk usage by jabber or Telegram. """
        disk_info = self.gather_disk()

        msg = "Disk usage (%s)\n" % self.current_datetime()

        for disk in disk_info.keys():
            info = disk_info[disk]
            usage = disk_info[disk]["usage"]

            msg += """  %s  
                --------
                Mount point: %s
                Filesystem type: %s
                Options: %s
                Usage:
                - Total: %s
                - Used: %s
                - Free: %s
                - Percentage used: %s %%\n\n""" % (
                    disk, info["mountpoint"], info["fstype"], info["opts"],
                    self.size_fmt(usage["total"]),
                    self.size_fmt(usage["used"]),
                    self.size_fmt(usage["free"]),
                    str(usage["percentage"]))

        return self.feedback(msg, sender, src)

    @Message(tags=["mem"])
    def info_memory(self, sender, src):
        """ Send basic information on memory usage by jabber or Telegram. """
        mem_info = self.gather_memory()

        msg = "Memory usage (%s)\n" % self.current_datetime()

        for mem_type in mem_info.keys():
            info = mem_info[mem_type]

            msg += """  %s  
                --------
                Total: %s
                Free: %s
                Used: %s
                Percentage used: %s %%\n\n""" % (
                    mem_type,
                    self.size_fmt(info["total"]),
                    self.size_fmt(info["free"]),
                    self.size_fmt(info["used"]),
                    str(info["percentage"]))

        return self.feedback(msg, sender, src)

    def attach_html(self, html):
        """ Build the attachment file.

            This file is stored in the directory specified in
            ZOE_HOME/etc/sysinfo.conf (the directory must exist previously)
        """
        now = datetime.today()

        filename = "sysinfo_%s_%s_%s_%s_%s_%s.html" % (
            str(now.day), str(now.month), str(now.year),
            str(now.hour), str(now.minute), str(now.second))

        b64 = base64.standard_b64encode(bytes(html, 'utf-8')).decode('utf-8')

        return zoe.Attachment(b64, "text/html", filename)

    def current_datetime(self):
        """ Return the current date and time in human-readable format. """
        now = datetime.today()

        return now.strftime("%d/%m/%Y - %H:%M:%S")

    def feedback(self, data, user, dst):
        """ Send feedback to the user

            data -- may be text or an attachment for e-mail
            user -- user to send the feedback to
            dst  -- either 'jabber', 'tg' or 'mail'
        """
        to_send = {
            "dst": "relay",
            "relayto": dst,
            "to": user
        }

        if dst == "jabber" or dst == "tg":
            to_send["msg"] = data

        else:
            to_send["html"] = data.str()
            to_send["subject"] = "System information report"

        return zoe.MessageBuilder(to_send)

    def gather_cpu(self):
        """ Gather information on system CPU.

            Obtains usage percentage for each CPU present for user,
            system and idle.
        """
        result = {}
        cpu_info = psutil.cpu_times_percent(percpu=True)

        for index, cpu in enumerate(cpu_info):
            result["cpu" + str(index)] = {
                "user": cpu.user,
                "system": cpu.system,
                "idle": cpu.idle
            }

        return result

    def gather_disk(self):
        """ Gather information on system disks.

            Obtains mounted disk partitions and their usage statistics.
        """
        result = {}
        partitions = psutil.disk_partitions(all=True)

        for partition in partitions:
            part_usage = psutil.disk_usage(partition.mountpoint)

            result[partition.device] = {
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "opts": partition.opts,
                "usage": {
                    "total": part_usage.total,
                    "used": part_usage.used,
                    "free": part_usage.free,
                    "percentage": part_usage.percent
                }
            }

        return result

    def gather_memory(self):
        """ Gather information on system memory.

            Obtains physical RAM and swap statistics.
        """
        result = {}
        mem_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()

        result["ram"] = {
            "total": mem_info.total,
            "free": mem_info.available,
            "used": mem_info.used,
            "percentage": mem_info.percent
        }

        result["swap"] = {
            "total": swap_info.total,
            "free": swap_info.free,
            "used": swap_info.used,
            "percentage": swap_info.percent
        }

        return result

    def gather_proc(self):
        """ Gather information on running processes.

            Obtains pid, name, executable, user running the process,
            status of the process and memory usage.
        """
        result = {}

        for proc in psutil.process_iter():
            try:
                process = psutil.Process(proc.pid)

                proc_data = process.as_dict(
                    attrs=["name", "exe", "username", "status"])

                mem_info = process.memory_info()
                proc_data["memory"] = {}
                proc_data["memory"]["resident"] = mem_info.rss
                proc_data["memory"]["virtual"] = mem_info.vms

                result[proc.pid] = proc_data

            except psutil.NoSuchProcess:
                continue

        return result

    def size_fmt(self, num):
        """ Represents amount of bytes in a better human-readable way.

            Obtained from http://stackoverflow.com/a/1094933
        """
        for unit in ['B','KiB','MiB','GiB','TiB','PiB','EiB','ZiB']:
            if abs(num) < 1024.0:
                return "%3.1f %s" % (num, unit)

            num /= 1024.0

        return "%.1f %s" % (num, 'YiB')
