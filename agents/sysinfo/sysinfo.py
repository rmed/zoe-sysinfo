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

import datetime
import os
import psutil
import zoe
from os import environ as env
from os.path import join as path
from zoe.deco import *


@Agent(name="sysinfo")
class Sysinfo:

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
        partitions = psutil.disk_partitions()

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

        # RAM
        result["ram"] = {
            "total": mem_info.total,
            "free": mem_info.available,
            "used": mem_info.used,
            "percentage": mem_info.percent
        }

        # SWAP
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
                    attrs=["name", "exe", "username"])
                
                mem_info = process.memory_info()
                proc_data["memory"] = {}
                proc_data["memory"]["resident"] = mem_info.rss
                proc_data["memory"]["virtual"] = mem_info.vms

                result[proc.pid] = proc_data

            except psutil.NoSuchProcess:
                continue

        return result
