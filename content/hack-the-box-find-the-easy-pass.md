Title: Hack The Box: Find The Easy Pass
Date: 2023-01-22
Category: Blog
Tags: CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

This is the second in a series of write-ups of challenges from the
[Hack The Box](https://www.hackthebox.com/) Beginner Track.

In my first write-up, [Lame]({filename}/hack-the-box-lame.md), I talked about
how [capture the flag](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity))
(CTF) challenges can generally be broken down into three phases: enumeration,
gaining a foothold, and privilege escalation.

This challenge, Find The Easy Pass, is a bit different from a regular CTF,
because there is no machine to break into. Instead, we're given a Windows
executable file.

Leaving aside the question of whether it's safe to run random executables you
downloaded from the internet, this is what appears when the file is launched:

![Password prompt]({attach}images/hack-the-box-find-the-easy-pass/main_window.png)

Entering a possible password into the text box and clicking _Check Password_
tells us whether we have the right password:

![Wrong password]({attach}images/hack-the-box-find-the-easy-pass/wrong_password.png)

Given the name of the challenge, it's pretty clear that the password is the flag
we have to find.

We have a program that we can use to test possible passwords, so in theory we
could brute-force our way through all of them, assuming we had some way to
automate the keyboard and mouse clicks. However, we have no idea what format the
password takes. It could be six characters long and composed only of lowercase
letters. It could also be fifty characters long and composed of uppercase and
lowercase letters, numbers and special characters. We have no idea, and in the
latter case there are more password combinations than there are atoms in the
observable universe, so we can expect to be sat brute-forcing our way towards a
solution for quite a while...

There's another quicker, more interesting way to tackle this problem. The
program we've been given must contain some process to determine whether or not a
given password is valid. If we can get a handle on this process, we might be
able to use it to infer the password. We essentially need to
[reverse engineer](https://en.wikipedia.org/wiki/Reverse_engineering) the
program we've been given.

Various tools exist to reverse engineer software, from disassemblers, which
translate the raw binary content of an executable to assembly mnemonics, to
decompilers, which attempt to reconstruct the program's original source code, to
debuggers, which allow the execution flow of the program to be examined in real
time.

For this challenge, I used the [x64dbg](https://x64dbg.com/) debugger, partly
because it's free and open source software (FOSS), and partly because I'd used
it before.

My strategy for locating the password ran along the following lines: after the
user enters a password and clicks the button to have it checked, that password
must be stored in the program's memory somewhere. That memory must be read at
some point prior to checking that the password is valid. If we can pause the
program at the point where it reads this memory, maybe we can examine the
program around this point, see where the candidate password is used and find the
place where this password is compared to the password we need to extract.

I started by looking for possible Windows API calls that could be associated
with the appearance of the message stating whether the password was correct or
not. My first instinct was the
[`MessageBox`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox)
function, but using x64dbg's symbol filter suggested that this function wasn't
used. After a bit of digging around in the Windows API docs, I came across
[`CreateWindowExA`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindowexa),
which spawns a pop-up or child window and is used within the binary:

![x64dbg symbol filtering]({attach}images/hack-the-box-find-the-easy-pass/symbol_filter.png)

Setting a breakpoint on this symbol, I used the memory map pane to search for
the password after the breakpoint on `CreateWindowExA` was hit:

![Memory map]({attach}images/hack-the-box-find-the-easy-pass/memory_map.png)

This gives us a dialog that we can use to search for arbitrary ASCII or UTF-8
strings. In this case we search for the ASCII password we've just entered:

![Finding memory references]({attach}images/hack-the-box-find-the-easy-pass/find_references.png)

This reveals a couple of places where the password is referenced:

![Memory reference results]({attach}images/hack-the-box-find-the-easy-pass/candidate_references.png)

Examining these locations in the memory dump pane, x64dbg allows us to set a
watchpoint on these memory addresses:

![x64dbg hardware watchpoint]({attach}images/hack-the-box-find-the-easy-pass/hardware_breakpoint.png)

Entering the same password again, the watchpoint is triggered, and we see the
password we've just entered to the right of the assembly listing:

![Hardware watchpoint triggered]({attach}images/hack-the-box-find-the-easy-pass/hardware_breakpoint_hit.png)

At this point we can use x64dbg to examine the call stack and get a sense of
where we are within the program:

![Hardware watchpoint triggered]({attach}images/hack-the-box-find-the-easy-pass/hardware_breakpoint_stack.png)

I'll be honest, this isn't particularly helpful. We could move around the
various stack frames here to establish what will happen next, or we could just
step through each instruction until we find the password comparison process.
Taking the latter approach, we eventually arrive at this point in the program:

![Message selection instructions]({attach}images/hack-the-box-find-the-easy-pass/critical_instructions.png)

This looks promising. x64dbg has helpfully extracted the values pointed to by
various memory addresses and registers. Our candidate password, `foobarbaz`, is
located in on the stack forty (28 in hexadecimal) bytes below the base of the
current stack frame, which is stored in the stack base pointer register, `ebp`.
Another string, `fortran!`, is stored four bytes below `ebp`. The pointers for
these bits of memory are moved into registers `eax` and `edx` by the
instructions `mov eax, dword ptr ss:[ebp-28]` and
`mov edx, dword ptr ss:[ebp-4]`, respectively, presumably in advance of a
comparison operation performed by the instruction `call <easypass.sub_404628>`.
Stepping through the next three instructions, we see this:

![Message selection instructions at jump]({attach}images/hack-the-box-find-the-easy-pass/critical_instructions_with_jump.png)

The program is now at a branching instruction, `jne easypass.454144`. `jne`
instructions tell the processor to jump to the specified instruction if a prior
comparison operation identified that the two operands weren't equal. In this
case we can assume that the comparison is the result of comparing the candidate
password with the actual password, probably by comparing the characters of the
two strings in sequence.

The instructions after the branching instruction refer to two strings. The
second is the string we saw in the UI when we entered the incorrect password.
The first must be the message we'll see when we enter the correct password.

In any case, it seems likely that "fortran!" is the password we're after. Trying
this out confirms this:

![Correct password]({attach}images/hack-the-box-find-the-easy-pass/correct_password.png)

With that, we're all done!

In hindsight it would've been equally valid to search memory for the message
that appears when we enter the wrong password. I've seen this approach used in
other walkthroughs. I suspect that if the selection of the message were more
removed from the password comparison process, maybe this approach would require
more work. After identifying the place where the message is selected, you would
then need to work backwards through the execution flow and find where the
password comparison occurred. Fortunately the binary here doesn't make this
necessary.
