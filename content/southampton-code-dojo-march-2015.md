Title: Southampton Code Dojo - March 2015
Date: 2015-03-19 20:26:53.424749
Modified: 2015-03-24 00:21:01.422745
Category: Blog
Tags: Python
Author: Matt Spraggs

I went along to the most recent [Southampton Code Dojo](https://www.southamptoncodedojo.com/) last week (12th March). I'd been meaning to go along for a while, and given how much I enjoyed the Game Jam in January (see [here](http://mattspraggs.co.uk/blog/posts/global-game-jam-2015-part-i)), I signed up earlier this month. The Dojo is basically a meet-up in the Southampton area for those interested in programming/coding, taking place on the second Thursday of each month. Unlike the Game Jam, which lasts all weekend, the Dojo takes place in two hours on one evening.

I managed to get off to a good start by showing up a bit late, a result of me being under the strange notion that the event was being held in the Nuffield Theatre. The first twenty minutes were dedicated to mingling, getting to know people and having some free pizza and beer. During this time, we generated a list of potential projects for the evening. After coming up with around a dozen ideas, ranging from an image-to-ascii converter to a traffic-light simulator, we ended up voting to create a maze generator.

The next 80 minutes were spent trying to implement a basic maze generator in Python, the chosen language for the evening. We split into groups of four, with each group making a separate attempt at the solving the problem. Within the group I was in, we sub-divided the task into two: one pair would work on visualizing the maze, whilst the other would work on the algorithm to actually generate the maze.

Our first problem was defining how we would store the maze data. We ended up settling on considering the maze as a series of cells with walls at the edges of each cell. We then needed to store whether each of these walls was present or not using boolean values. As a result, for an N x N grid of cells, we needed an N+1 x 2N+1 array of booleans to encode the present/not present states of the walls. The 2N+1 rows were needed because the states of the vertical and horizontal walls were stored on separate rows of the matrix.

Once we had our data structure defined, we split into our sub-teams. I worked with my sub-team partner on visualizing the maze using [pygame](http://pygame.org/). I'd used pygame a bit before when I started at Southampton, so we were able to tap into this existing code and come up with something new. It was fairly basic, just drawing lines to the screen, but we did have some difficulty at one point translating the row/column indices in our data structure to the screen coordinates. After some fiddling, we got it working, and it looked presentable. Even when populating the input data with random values, we got something that looked like it could keep a drunk person entertained for quarter of an hour. You can check out the source code [here](https://gist.github.com/jscott1989/cc874906c0a839473a7d).

![Our maze visualizer][screenshot-180315-003130png]

Once the 80 minutes were up, each group presented what they'd achieved in the time available. Our maze generation code wasn't complete, though we did have the visualization front-end working. We weren't alone in not having a fully functioning maze generator, though all groups had code that did something, and it was interested to see the different approaches. It turned out our group was unusual in that we had decided to encode the states of the walls, rather than just treat the world as a series of cells that were either empty or occupied. One group had managed to see the task through to completion using a recursive algorithm to generate the maze, and the results looked quite spectacular.

![A more complete maze](https://scd-media.s3.amazonaws.com/media/event_images/t.png)

I'd thoroughly recommend the Dojo to anyone with an interest in coding and who wants to practice their skills in a collaborative environment, as well as meet and network with others (I myself came away with a business card). The free pizza and refreshments don't hurt either!

P.S. I should mention that the Dojo is free for attendees because it is typically sponsored by a company or institution. The event costs around £130 to run, so on the off chance that you read this and are interested in sponsoring an event, do [get in touch with the event organisers](https://www.southamptoncodedojo.com/pages/sponsorship).
[screenshot-180315-003130png]: /media/content_images/Screenshot_-_180315_-_003130.thumb.png
