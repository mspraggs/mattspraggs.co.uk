Title: Rust + WebAssembly + JavaScript = Joy
Date: 2020-04-12
Category: Blog
Tags: Rust, JavaScript, WebAssembly, SIR Model
Author: Matt Spraggs

Despite the title, this blog post doesn't start with Rust. Instead, it starts
with the tradgedy of the ongoing global COVID-19 pandemic.
[Numberphile](https://www.youtube.com/channel/UCoxcjq-8xIDTYp3uz647V5A) had
recently uploaded a [video](https://www.youtube.com/watch?v=k6nLfCbAzgo) about
the SIR model, which describes the spread of an infectious disease. The simple
yet powerful nature of the model and its relevance to current events struck a
chord with me: I had to code this up for myself.

Python seemed like the best candidate for the job, given the existence of
numerical libraries such as NumPy and SciPy. My first iteration needed just
35 lines of code, a testament to Python's expressiveness and the well-designed
library interfaces.

The next step seemed clear to me: how cool would it be to put this on the web?
Sure, it's a simple model, but one of great relevance given recent events, so
maybe it might interest some.

I weighed my options. I had a working implementation in Python, so reusing that
made sense. I could host my implementation on a server somewhere and expose it
via a REST API. Hell it might even be cheap to do this if I instead used
something like an [AWS lambda](https://aws.amazon.com/lambda/). This did leave
some questions though, mainly around Python package support and the lambda
taking too long to run and timing out.

Perhaps instead I could compile my Python implementation to
[WebAssembly](https://webassembly.org/) and run it in the browser? Reading
around, it sounded like this boiled down to having a WebAssembly implementation
of the Python interpreter. Turns out there are a few, but after some
experimentation I gave up because of the difficulty of integrating SciPy support
into the project. If I was going to run with WebAssembly, perhaps I'd need to
forego my existing Python implementation and use a language that
better-supported WebAssembly.

Enter Rust. As a long-time C++ user, and a jaded one at that, I'd been aching
for a decent project to apply Rust to for ages. Why not now? WebAssembly support
in Rust is way more mature than Python, and the result would undoubtedly perform
better without the need for Python's virtual machine.

I'm not going to lie: compared to Python, Rust certainly feels less expressive,
but then it'd be hard not to. Compared to C++, however, Rust is just a dream.
Variable declarations and type inference allow me to write code that just
feels cleaner. Perhaps I'm superficial, but after C++ one of the biggest selling
points is the standard library. It just feels more complete and well-thought-out
than that of C++. I'm not trying to downplay the other features of the language.
It was nice to know that I could write code without the risk of using a dangling
reference or causing a segfault.

The biggest difficulty I found was finding a library to solve the SIR model
differential equations. I initially experimented with the
[peroxide crate](https://docs.rs/peroxide/0.21.5/peroxide/), but was quickly
frustrated to find that the interface doesn't allow models that are expressed
via closures, instead requiring a function pointer. This meant I'd either have
to hard-code the model parameters or use global variables, both of which were
enough to rule it out.

I instead settled for the
[diffeq crate](https://docs.rs/diffeq/0.1.0/diffeq/), which permits closures and
has great support for JSON serialisation of the solution it computes. My final
implementation required only 45 lines of Rust.

The documentation on compiling Rust to WebAssembly is great, and provides
multiple sample projects depending on how you plan to ship your project. I ended
up using [wasm-bindgen](https://docs.rs/wasm-bindgen/0.2.60/wasm_bindgen/)
[without a bundler](https://github.com/rustwasm/wasm-bindgen/tree/master/examples/without-a-bundler).

For the UI I went with [Plotly](https://plotly.com/graphing-libraries/) to graph
the solution and [Bootstrap](https://getbootstrap.com/) to style the rest of the
page. You can view the finished result
[here](https://mspraggs.github.io/sir_model/index.html).

The SIR model itself highlights the importance of social distancing: by cutting
the rate at which the virus spreads through tue population we can not only
lessen the peak number of infections but potentially limit the number of people
infected by the virus overall.
