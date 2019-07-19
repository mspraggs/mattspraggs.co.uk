Title: Embedded Software Practices: My Take
Date: 2017-10-25 19:55:32.421130
Modified: 2017-10-25 19:55:32.421260
Category: Blog
Tags: Engineering, LabVIEW
Author: Matt Spraggs

A friend and I were discussing the relative merits of LabVIEW the other day. Coming from a theoretical, software-focused background, I struggle with LabVIEW, which I think hides too many of the underlying workings of a program from the user for the sake of simplicity. My friend, on the other hand, does a lot of experimental engineering work and loves that LabVIEW frees him from the need to look at line after line of code.

This got me thinking: should engineers, particularly those working in electronics, be more prepared to work with low-level code? I mean obviously they work with it already, but my (admittedly limited) experience so far is that few engineers take the time to engineer software that is clear, testable and maintainable. In a world where both hardware and software are advancing at an exponential rate, shouldn't we be cultivating engineers who at least appreciate the need to excel at both?

As a software engineer I'm used to the various procedures and practices required to devise unit tests: encapsulate functionality to create a software unit; test isolated units by mocking other components; specify behaviour required of the unit as a test. A quick google seems to indicate that the concept of unit testing is far less pervasive in the realm of embedded software (though [this guy](http://www.electronvector.com/about/) looks like he's trying to change that). When you think about it this is crazy. Embedded software is often a mission critical component of modern technology, so it surely makes sense to devise tests wherever and whenever you can. Certainly if embedded software is tested in a systematic and rigorous manner in industry, there is no clear specification for how this is done or how to go about doing it.

Perhaps the problem is a difference in mindset between electronic and software engineers. Electronic engineering is an inherently tangible activity, whereas software engineering need not have any physical manifestation at all. Budding electronic engineers are therefore more likely to seek out the tangible aspects of any design and implementation task, whilst seeing any software development as a necessary evil, rather than a task to take pride in. To overcome this we should really be encouraging engineers to show an interest in designing software that is robust via rigorous implementation processes.

There is clearly some movement within the embedded software community to establish good software development principles and practice. The community over at [Throw The Switch](http://www.throwtheswitch.org/), for example, offers courses on how to design robust, effective embedded software and implement unit tests. They've even taken the time to create a set of tools to accelerate the process of [devising](http://www.throwtheswitch.org/unity) and [building](http://www.throwtheswitch.org/ceedling) unit tests, as well as [mocking](http://www.throwtheswitch.org/cmock) hardware interfaces.

I really hope this movement grows. I'm very much in favour of well-designed software and would really like to see software engineering best practice become pervasive within the field of embedded development.
