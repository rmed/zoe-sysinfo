#!/usr/bin/env perl
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
# SOFTWARE.

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $cpu;
my $disk;
my $mem;
my $report;

my $sender;

GetOptions("get" => \$get,
           "run" => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "c" => \$cpu,
           "d" => \$disk,
           "m" => \$mem,
           "r" => \$report);

if ($get) {
  &get;
} elsif ($run and $cpu) {
  &cpu;
} elsif ($run and $disk) {
  &disk;
} elsif ($run and $mem) {
  &mem;
} elsif ($run and $report) {
  &report;
}


#
# Commands in the script
#
sub get {
  print("--c /show cpu usage\n");
  print("--d /show disk usage\n");
  print("--m /show memory usage\n");
  print("--r /send /complete report\n");

  print("--c /muestra uso /de cpu\n");
  print("--d /muestra uso /de disco\n");
  print("--m /muestra uso /de memoria\n");
  print("--r /manda informe /completo\n");
}

#
# Basic information on CPU usage
#
sub cpu {
  print("message dst=sysinfo&tag=cpu&user=$sender\n");
}

#
# Basic information on disk usage
#
sub disk {
  print("message dst=sysinfo&tag=disk&user=$sender\n");
}

#
# Basic information on memory usage
#
sub mem {
  print("message dst=sysinfo&tag=mem&user=$sender\n");
}

#
# Complete report send to email
#
sub report {
  print("message dst=sysinfo&tag=report&user=$sender\n");
}
