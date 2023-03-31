Title: Hack The Box: Weak RSA
Date: 2023-03-31
Category: Blog
Tags: CTF, Cybersecurity, Hack The Box
Author: Matt Spraggs

This is the third in a series of write-ups of challenges from the
[Hack The Box](https://www.hackthebox.com/) Beginner Track.

# The Challenge

The previous challenge,
[Find The Easy Pass]({filename}/hack-the-box-find-the-easy-pass.md), gave us a
Windows executable to reverse engineer. In this sense it didn't align with my
expectations of what a
[CTF](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity)) involves.

This challenge, Weak RSA, is similar in the sense that we're given two files to
download. This time though, neither of them are executable:

```shell
$ file key.pub
key.pub: ASCII text
$ file flag.enc 
flag.enc: data
```

Looking at the contents of `key.pub`, it looks like an RSA public key:

```shell
$ cat key.pub 
-----BEGIN PUBLIC KEY-----
MIIBHzANBgkqhkiG9w0BAQEFAAOCAQwAMIIBBwKBgQMwO3kPsUnaNAbUlaubn7ip
4pNEXjvUOxjvLwUhtybr6Ng4undLtSQPCPf7ygoUKh1KYeqXMpTmhKjRos3xioTy
23CZuOl3WIsLiRKSVYyqBc9d8rxjNMXuUIOiNO38ealcR4p44zfHI66INPuKmTG3
RQP/6p5hv1PYcWmErEeDewKBgGEXxgRIsTlFGrW2C2JXoSvakMCWD60eAH0W2PpD
qlqqOFD8JA5UFK0roQkOjhLWSVu8c6DLpWJQQlXHPqP702qIg/gx2o0bm4EzrCEJ
4gYo6Ax+U7q6TOWhQpiBHnC0ojE8kUoqMhfALpUaruTJ6zmj8IA1e1M6bMqVF8sr
lb/N
-----END PUBLIC KEY-----
```

We can confirm this with [OpenSSL](https://www.openssl.org/):

```shell
$ openssl rsa -pubin -in key.pub -text -noout
RSA Public-Key: (1026 bit)
Modulus:
    03:30:3b:79:0f:b1:49:da:34:06:d4:95:ab:9b:9f:
    b8:a9:e2:93:44:5e:3b:d4:3b:18:ef:2f:05:21:b7:
    26:eb:e8:d8:38:ba:77:4b:b5:24:0f:08:f7:fb:ca:
    0a:14:2a:1d:4a:61:ea:97:32:94:e6:84:a8:d1:a2:
    cd:f1:8a:84:f2:db:70:99:b8:e9:77:58:8b:0b:89:
    12:92:55:8c:aa:05:cf:5d:f2:bc:63:34:c5:ee:50:
    83:a2:34:ed:fc:79:a9:5c:47:8a:78:e3:37:c7:23:
    ae:88:34:fb:8a:99:31:b7:45:03:ff:ea:9e:61:bf:
    53:d8:71:69:84:ac:47:83:7b
Exponent:
    61:17:c6:04:48:b1:39:45:1a:b5:b6:0b:62:57:a1:
    2b:da:90:c0:96:0f:ad:1e:00:7d:16:d8:fa:43:aa:
    5a:aa:38:50:fc:24:0e:54:14:ad:2b:a1:09:0e:8e:
    12:d6:49:5b:bc:73:a0:cb:a5:62:50:42:55:c7:3e:
    a3:fb:d3:6a:88:83:f8:31:da:8d:1b:9b:81:33:ac:
    21:09:e2:06:28:e8:0c:7e:53:ba:ba:4c:e5:a1:42:
    98:81:1e:70:b4:a2:31:3c:91:4a:2a:32:17:c0:2e:
    95:1a:ae:e4:c9:eb:39:a3:f0:80:35:7b:53:3a:6c:
    ca:95:17:cb:2b:95:bf:cd
```

So it's definitely an RSA key. At this point it's fairly clear what we need to
do. `flag.enc` must contain the encrypted flag. We need to decrypt that by
finding the private key that matches the public key we've been provided.

# RSA

[RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) is an asymmetric
encryption algorithm. This means that there are two keys: one to encrypt, the
public key, and one to decrypt, the private key. As their names suggest, the
public key is intended to be shared, whilst the private key must be kept secret.
Together they form a key pair.

Before we get into the nitty gritty, here's a little warning. The security of
RSA involves quite a lot of maths. I've tried to keep this brief and relevant to
the current problem, but a bit of maths is unavoidable, so apologies in advance
if this isn't your jam.

An RSA key pair is defined by a modulus, $N$, a public key exponent, $e$, and a
private key exponent, $d$. $N$ is the product of two large, prime numbers $p$
and $q$. The security of RSA is founded on the difficulty of determining $p$ and
$q$, given only $N$ and $e$. If RSA is used correctly, factoring $N$ into $p$
and $q$ is essentially impossible. $e$ and $d$ are then related via

$$
e d \equiv 1 \quad \left(\text{mod} \space \varphi(N)\right) \tag{1}
$$

where $\varphi$ is
[Euler's totient function](https://en.wikipedia.org/wiki/Euler_totient_function).
Within the realm of RSA, $\varphi(N) = (p-1)(q-1)$. $\text{mod}$ is short for
[_modular arithmetic_](https://en.wikipedia.org/wiki/Modular_arithmetic), which
effective means that we require the remainder when we divide the product of $e$
and $d$ by $\varphi(N)$ is $1$. $d$ is said to be the
[_modular multiplicative inverse_](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
of $e$, and vice versa. $e$ is normally picked, and $d$ is then calculated using
something like the
[extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
or
[Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem).

# Finding a Weakness

Our public key's modulus is 1026 bits long according to OpenSSL. Given that it
took 2700 CPU-years of compute time on state-of-the-art hardware just to break a
public key with an 829-bit modulus
[back in 2020](https://web.archive.org/web/20200228234716/https://lists.gforge.inria.fr/pipermail/cado-nfs-discuss/2020-February/001166.html),
we can safely assume this approach won't work here.

The time required to encrypt a plaintext message or decrypt a ciphertext is a
function of the size of the public and private key exponents, respectively.
Implementations generally favour smaller values of $e$, and
$2^{16} + 1 = 65537$, or `0x10001`, is a common public key exponent. Smaller
values weaken the security of the cryptosystem, whilst larger values result in
longer encryption times without any further security benefit.

The public key above has an exponent that is far greater than 65537, which is a
bit strange.
[Googling](https://www.google.com/search?q=rsa+public+key+large+exponent) "rsa
public key large exponent" produced results that suggest a large exponent like
ours may be symptomatic of a correspondingly small private key exponent. When
the private exponent is small relative to the modulus, the former can be
recovered relatively easily using
[Wiener's attack](https://en.wikipedia.org/wiki/Wiener%27s_attack).

# Wiener's Attack

Wiener's attack uses Wiener's theorem to let us efficiently determine $d$. The
theorem states that, given the following:

$$
\begin{gather}
N = pq\\\\
q < p < 2q\\\\
e d \equiv 1 \space \left(\text{mod} \space \varphi(N)\right)\\\\
d < \frac{1}{3}N^\frac{1}{4}\\
\end{gather}
$$

we can efficiently compute $d$ using approximations of $\frac{e}{N}$.

But how? What does it mean to approximate $\frac{e}{N}$?

Revisiting the relationship between the public and private exponents, $e$ and
$d$, we can say that there must be some integer $k$ such that

$$
e d - k \varphi(N) = 1\tag{2}
$$

Here $k$ is essentially the [quotient](https://en.wikipedia.org/wiki/Quotient)
we would obtain if we divided $ed$ by $\varphi(N)$. Using
$\varphi(N) = (p - 1)(q - 1)$ allows us to write

$$
e d - k (p - 1)(q - 1) = 1
$$

With a bit of massaging this can be rewritten as

$$
\frac{e}{pq} = \frac{k}{d}(1 - \delta); \quad \delta = \frac{p + q - 1 - \frac{1}{k}}{pq}\tag{3}
$$

So we expect $\frac{e}{pq}$ to be slightly smaller than $\frac{k}{d}$, up to
some fraction $\delta$. We know $e$ and $pq$ as they define the public key, but
how can we use (3) to determine $\frac{k}{d}$?

In the paper orignally describing this attack, Wiener outlines how we can find
$\frac{k}{d}$ using
[continued fractions](https://en.wikipedia.org/wiki/Continued_fraction). A
continued fraction takes the form

$$
\frac{m}{n} = a_0 + \frac{1}{a_1 + \frac{1}{a_2 + \frac{1}{\ddots + \frac{1}{a_n}}}}
$$

The various values $a_i$ are known as the _quotients_. These can be calculated
using an iterative process. We determine the quotient and remainder of
$\frac{m}{n}$. The quotient is our $a_i$, and the reciprocal of the remainder
becomes our new $\frac{m}{n}$. We repeat this process until the remainder is
zero. $\frac{m}{n}$ is approximated by the _convergents_, $c_i$, of the
continued fraction:

$$
c_i = a_0 + \frac{1}{a_1 + \frac{1}{a_2 + \frac{1}{\ddots + \frac{1}{a_i}}}}
$$

Wiener's [paper](https://ieeexplore.ieee.org/document/54902) explains that, if
the value of $d$ is sufficiently small relative to $N$, we can find
$\frac{k}{d}$ amongst the convergents of $\frac{e}{pq}$.

Computing the convergents of $\frac{e}{pq}$ gives us some potential values of
$\frac{k}{d}$, but we're not quite done yet. To complete the attack, we need a
way of determining which of these convergents is indeed $\frac{k}{d}$. From (2),
we can determine $\varphi(N)$ given some candidate values for $k$ and $d$. At
the same time, we can use the relationship between $\varphi(N)$, $p$ and $q$ to
derive a quadratic equation in $p$:

$$
\begin{align}
\varphi(N) & = (p - 1)(p - 1) &\\
& = p q - p - q + 1 &\\
& = N - p - \frac{N}{p} + 1 &\\
\end{align}
$$

Multiplying both sides by $p$ and collecting terms gives

$$
p^2 + (\varphi(N) - N - 1) p + N = 0 \;.\tag{4}
$$

We know $N$, and we have a candidate value for $\varphi(N)$. Plugging these in,
we can solve this equation for $p$. If the value of $\varphi(N)$ is correct, we
should end up with two roots, $p_1$ and $p_2$, whose product is $N$. (Because
$p_1$ and $p_2$ must be integers, it does not automatically hold that
$p_1 p_2 = N$.)

# Putting it All Together

With an understanding of Wiener's attack in hand, we can try to break the public
key we've been provided with the following steps:

1. Compute the quotients of $\frac{e}{N}$.
2. Compute the convergents of $\frac{e}{N}$ from the quotients in step 1.
3. For each convergent in step 3, use the numerator as a candidate for $k$ and
   the denominator as a candidate for $d$ and compute a candidate for
   $\varphi(N)$ using equation (2).
4. Calculate the roots of equation (4) for each candidate $\varphi(N)$. For a
   given $\varphi(N)$, if the product of these roots is equal to $N$, the
   candidate $d$ from step 3 will satisfy equation (1).

I coded
[this](https://gist.github.com/mspraggs/f1ccca8bc6f852186efa63adf2d8a8b4)
up using Go. Unfortunately, Go's standard library doesn't support
RSA public keys with large exponents, so I had to cook up a few custom types.
Running my code against the provided public key gives the following:

```shell
$ cat key.pub | go run main.go
-----BEGIN RSA PRIVATE KEY-----
MIICOQIBAAKBgQMwO3kPsUnaNAbUlaubn7ip4pNEXjvUOxjvLwUhtybr6Ng4undL
tSQPCPf7ygoUKh1KYeqXMpTmhKjRos3xioTy23CZuOl3WIsLiRKSVYyqBc9d8rxj
NMXuUIOiNO38ealcR4p44zfHI66INPuKmTG3RQP/6p5hv1PYcWmErEeDewKBgGEX
xgRIsTlFGrW2C2JXoSvakMCWD60eAH0W2PpDqlqqOFD8JA5UFK0roQkOjhLWSVu8
c6DLpWJQQlXHPqP702qIg/gx2o0bm4EzrCEJ4gYo6Ax+U7q6TOWhQpiBHnC0ojE8
kUoqMhfALpUaruTJ6zmj8IA1e1M6bMqVF8srlb/NAiBhwngxi+Cbie3YBogNzGJV
h10vAgw+i7cQqiiwEiPFNQJBAYXzr5r2KkHVjGcZNCLRAoXrzJjVhb7knZE5oEYo
nEI+h2gQSt1bavv3YVxhcisTVuNrlgQo58eGb4c9dtY2blMCQQIX2W9IbtJ26KzZ
C/5HPsVqgxWtuP5hN8OLf3ohhojr1NigJwc6o68dtKScaEQ5A33vmNpuWqKucecT
0HEVxuE5AiBhwngxi+Cbie3YBogNzGJVh10vAgw+i7cQqiiwEiPFNQIgYcJ4MYvg
m4nt2AaIDcxiVYddLwIMPou3EKoosBIjxTUCQQCnqbJMPEQHpg5lI6MQi8ixFRqo
+KwoBrwYfZlGEwZxdK2Ms0jgeta5jFFS11Fwk5+GyimnRzVcEbADJno/8BKe
-----END RSA PRIVATE KEY-----
```

Pasting this into a file, we can use OpenSSL to decrypt the provided flag:

```shell
$ cat flag.enc | openssl rsautl -decrypt -inkey key
HTB{s1mpl3_Wi3n3rs_4tt4ck}
```

And that's it! We've recovered the flag.
