Title: Loxx: Implementing Bob Nystrom's Lox in C++14
Date: 2018-05-29 22:24:03.756431
Modified: 2018-10-22 21:49:46.927009
Category: Blog
Tags: Compilers, C++

Last autumn I discovered [Crafting
Interpreters](https://craftinginterpreters.com), a book by Bob Nystrom that gives readers a comprehensive guide to writing interpreters for a toy programming language, Lox. To me the world of compilers and interpreters has always been a total mystery. Okay, so I know what a syntax tree is, and I've occassionally even been brave enough to look at the assembly output for a program I've written. Also doesn't parsing need to happen at some point? Anyway, I was pretty intrigued, so in I dived.

Bob's book is divided into two parts. The first details how to write a tree-walking interpreter in Java. Code is parsed and a syntax tree is generated from it, which is then evaluated in-place. By his own admission, this isn't a particularly efficient way to evaluate code, so the second part of the book describes how to write a stack-based virtual machine in C, which is considerably faster.

To make things interesting, and because I don't know Java too well, I figured I'd use C++ instead. Unlike Java, C++ isn't a garbage-collected language. Throwing caution to the wind, I decided that objects in [my C++ interpreter](https://github.com/mspraggs/loxx) would be encoded using `std::shared_ptr`, which uses reference counting to determine when the objects they point to should be removed from memory. Ignoring the fact that `std::shared_ptr` can produce memory leaks through cyclic dependencies (e.g. object A depends on object B and B depends on A, so the objects are never deleted), I ploughed into the first chapter.

The book is very practical, with the specified aim of walking readers through every single line of code required to write an interpreter. On top of this, Bob refrains from using any dependencies, with the result being that every aspect of the compilation process is implemented from scratch. As a reader I was walked through the process of tokenising the source code. These tokens were then used to build syntax trees using a recursive descent parser. The resulting tree was then handed over to an interpreter, which walked it, evaluating expressions from the bottom up.

Bob is writing the book and publishing it online a chapter at a time. When I started reading, the entire first half was online bar the last chapter, and I was slow enough in implementing my C++ version that this last chapter came out when I wanted to start reading it. As a result I was able to fully implement a tree-walking interpreter based entirely on the one described in the first half of the book.

I wasn't content with stopping there though. Apart from anything else my interpreter was painfully slow. On top of this it also had a glaring memory leak, which could easily be recreated using the following code:

    class Foo {}
    
    for (var i = 0; i < 1000000; i = i + 1) {
      var foo = Foo();
      var bar = Foo();
      foo.bar = bar;
      bar.foo = foo;
    }

Inside each for loop iteration, two objects are created and given references to each other. At the end of the iteration, the two objects go out of scope, so in theory the memory they use should be deallocated by the interpreter. However, because I'd used `std::shared_ptr` as the mechanism by which references to objects were stored, a situation arose where two shared pointers effectively pointed at each other, meaning their associated memory was never deallocated. The result being that the memory used by the interpreter would grow and never get deallocated.

I knew the next part of the book was on writing a bytecode virtual machine. The only problem was it didn't exist yet. *Never mind*, I thought, *I'll plough on and do it anyway*. I continued to use C++, and was already at a huge advantage because I had all the parsing infrastructure in place from the tree-walking interpreter. I needed to create two classes on top of that: a `Compiler`, which would generate a bytecode representation of the program, and a `VirtualMachine`, which would take that bytecode and execute it. On top of this, I also needed to sort out the aforementioned memory leak, meaning I probably needed to implement a garbage collector.

Without Bob's dulcet words to guide me, things became a lot more challenging. Instead of reading the book, I had to cobble together a half-baked understanding from various other resources: the [Dragon Book](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools), source code for other interpreters (e.g. Python, Lua, [clox](https://github.com/munificent/craftinginterpreters/tree/master/c)), and good old Wikipedia. Some parts of the interpreter were certainly more challenging than others. Variable resolution and closures, in particular, were a lot of hard work at first. Other areas, such as control flow, were comparatively straightforward.

I initially had the `Compiler` class generate bytecode in one amorphous blob, with the bytecode for functions sprinkled in amongst bytecode for code in the global scope. This worked fine when running code in scripts, since every statement was compiled at once and the bytecode for each function was immediately available where it was required. I ran into problems, however, inside the interpreter's interactive session, since bytecode wasn't preserved from one statement to the next, and so functions that had previously been compiled wouldn't be available to execute later. Eventually I had to refactor my code to have each function object take ownership of its associated bytecode. This made it possible for the code to persist and hence let the virtual machine execute it when necessary.

Variable resolution and closures took a lot of effort to understand and implement, and I admit that I did refer a lot to [Bob's C implementation](https://github.com/munificent/craftinginterpreters/tree/master/c) to try and understand how to get this stuff working properly. In my solution, which follows Bob's implementation fairly closely, variables are handled in several stages. When a `var` token is encountered in the syntax tree, the compiler checks to see if a variable with the corresponding name already exists and declares it if needed (if not, a compile error is thrown). Whenever a variable name is encountered, the compiler then tries to resolve it as a local variable in the current scope. If the variable is found, its associated index is used to refer to it in the generated bytecode.

If the variable can't be resolved locally, the compiler next tries looking in outer scopes, working outwards from the current one. If the variable is found there, the compiler tags it as an "upvalue" and adds it to a list of outstanding upvalues to be captured whenever it next encounters a return statement. This mechanism allows nested functions to close over variables in outer scopes, for example:

    fun make_printer(str)
    {
        fun printer()
        {
            print str;
        }
        return printer;
    }
    
    var hello_world_printer = make_printer("Hello, world!");
    hello_world_printer(); // Hello, world!

If the interpreter had no mechanism to allow it to capture `str` on the fifth line, then in the best case calling `hello_world_printer` would print a null value (`nil` in Lox land), and in the worst case you could end up with some crazy undefined behaviour.

If the compiler cannot resolve a variable in a local scope or an outer scope, the next thing it tries is looking in the global scope. If it still can't find a matching variable, it generates a compiler error and moves to compiling the next statement. This may sound pointless, but as [Bob explains](http://craftinginterpreters.com/parsing-expressions.html#syntax-errors) so well in his book, this allows users to identify further erroneous code.

I tackled my memory leak by implementing a tracing garbage collector that used [tri-colour marking](https://en.wikipedia.org/wiki/Tracing_garbage_collection#Tri-color_marking) to provide reachability-based leak detection. The basic premise is that all objects are initially assumed to be unreachable. One or more collections of objects are then specified as external interfaces that provide access to allocated objects. Examples of these include the virtual machine's stack and the hash table of global variables. These external interfaces are then used to determine which objects the virtual machine can reach by following any references objects have to each other. Objects that are still unreachable at the end of the garbage collection cycle are then deallocated.

At times it was a bit of a slog, but having completed my own stack-based VM I'm pretty pleased with the result. I learnt a lot, even in the absence of the second half of Bob's book. If I wanted to take it further I could try and up the ante by adding a just-in-time (JIT) compiler, but the amount of effort involved would probably be an order of magnitude larger. It's going to be interesting enough reading the remaining chapters of Bob's book and seeing how my interpreter compares with his C implementation.
