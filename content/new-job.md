Title: "New" Job!
Date: 2017-02-21 17:38:51.706789
Modified: 2017-02-21 17:38:51.706913
Category: Blog
Tags: Employment, C#
Author: Matt Spraggs

So the title of this post was originally going to be "New Job!", but since I've been in my current post since September I figured that might be a bit misleading, so I added some lovely quotes to make it feel less like a blatant lie.

Since the end of my PhD I've been working in the department of Electronics and Computer Science at the University of Southampton, doing software engineering as part of a project called [SMARTmove](https://smartmove.soton.ac.uk). The project aims to rehabilitate the upper limbs of stroke patients using a technique known as [functional electrical stimulation](https://en.wikipedia.org/wiki/Functional_electrical_stimulation) (FES). By electrically stimulating the arm muscles of stroke patients as they attempt a series of functional tasks it is anticipated that they will recover some control over the arm that was debilitated by the stroke.

The electrical stimulation is provided via an electrode array printed onto a wearable sleeve, and the patient's movements are monitored using a Microsoft Kinect. This data is then fed into an [iterative learning control](https://en.wikipedia.org/wiki/Iterative_learning_control) (ILC) algorithm that determines the required level of stimulation to give the patient in order to help them achieve the task.

My job is to develop software that provides feedback to the patient on how well they've done a given task. Besides this, it must also handle data from the Kinect and relay it to the ILC controller. As a result, the development work is quite varied, involving not only development of a graphical user interface but also data processing, network programming, and more besides.

The decision to use the Kinect has introduced some constraints as far as the platform and programming language are concerned. Currently the best skeletal tracking library available for the Kinect is the official SDK provided my Microsoft. Since this can only run on Windows 8.1 and 10, this means I'm restricted to developing software for these platforms. I'm not exactly the biggest fan of Windows, but on the plus side this gave me the opportunity to check out Microsoft's latest offering on the OS front (more on this later).

So anyway that's my employment stituation at the moment. Overall I think things are going pretty well. Here's hoping that trend continues.
