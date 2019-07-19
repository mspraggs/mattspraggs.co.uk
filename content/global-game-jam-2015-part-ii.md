Title: Global Game Jam 2015 (Part II)
Date: 2015-02-07 23:01:40.644312
Modified: 2015-03-19 08:13:45.841263
Category: Blog
Tags: Global Game Jam, Gaming, SDL, C++
Author: Matt Spraggs

Click [here]({filename}./global-game-jam-2015-part-i.md) for part I.

Much of Saturday was spent laying down the game code. I worked on some of the game backend, creating an object-orientated interface to the game world and levels. The world would be split into several rooms, and each room would contain a series of blocks, some of which the player could interact with. Inspired by [Spelunky](http://www.spelunkyworld.com/), we decided to store our level layouts in ASCII files to simplify level editing.

At 6pm on Saturday a mini-showcase was held. This was supposed to be an intermediate deadline to work towards to try and get something playable that could be worked with over the next 21 hours. By this point we had code that compiled and a character that could be moved around the screen. But the rest of world and all the game physics were missing, so we still had some way to go. In actuality it didn't take many more hours to link the world into the game loop so that the player had some interaction with the environment. Our artist did an amazing job coming up with some sprites for the background, character, weapons and environment, and before long we had something that looked and handled pretty well.

We still had a lot to do in the time remaining. I spent the early hours trying to pin down bugs in the game physics, which at this point allowed the player to jump and stick to walls, amongst other things. Hardly ideal. It was at this point that I realised I'd made a grave error in not bringing along any snacks to see me through the night. The combination of mild hunger and tiredness meant that by around four or five in the morning my energy levels were waaaay down.

Still, we pushed on. I added some extra features to the world files, allowing some blocks to be spawned at random moments during the level. My collaborators had also been doing an amazing job adding extra weapons, player-level interaction and sprites to the game, so that by the time the sun rose, we had something that looked pretty decent. With the showcase at 3pm fast approaching, we added some extra features to make the game more of an actual game: new levels, a win condition and menu levels, amongst other things. With about an hour and a half to go and the deadline looming, we battled against several bugs that would occasionally bring our player's game to a crashing halt. Finally, three o'clock rang out, meaning showcase time. With our game near-complete, but with a few rough edges, we left our game to be judged by others at the Jam.

It was actually pretty amazing to see how much people had managed to produce in the 48 hours available. Highlights for me had to be *[Funky Boys in Whack Times](http://globalgamejam.org/2015/games/funky-boys-whack-times)* (the eventual Jam winners), a GameBoy-style four-player co-op; *[U WOT M8](http://globalgamejam.org/2015/games/u-wot-m8)*, which described itself as a "headbutting simulator" using Oculus Rift and *[We've Lost The Game](http://globalgamejam.org/2015/games/weve-lost-game)*, a 2D open-level survival game. You can check out the full list of contributions from Southampton [here](http://globalgamejam.org/2015/jam-sites/university-southampton/games).

Overall it was an amazing experience and an absolutely fantastic way to get a project off the ground in a short space of time. The collaborative atmosphere was just incredible, and it was amazing to see your ideas come to fruition in such a short space of time. I will definitely be attending the next game jam, global or not. Perhaps next time I'll remember to bring snacks, and get my head down for a couple of hours on the Saturday night.
