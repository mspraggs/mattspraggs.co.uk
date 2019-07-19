Title: Upgrading Mesa on Debian Stable (Jessie)
Date: 2016-01-06 17:45:13.508682
Modified: 2017-02-14 13:11:14.351174
Category: Blog
Tags: Tech Help, Gaming, Linux
Author: Matt Spraggs

Hello! Belated merry Christmas and a very happy New Year!

Right, now the social niceties are out the way let's get down to it. I play World of Warcraft (WoW). There, I said it. No/some shame. I also run Linux. LMDE 2 Betsy to be exact. That's Linux Mint but based on the Debian repositories, so I'm not shackled to the whims of Canonical. WoW is targetted at Windows and OSX, but that's okay, as Wine [handles WoW fairly well](https://appdb.winehq.org/objectManager.php?sClass=version&iId=32314).

LMDE Betsy is currently based on Debian stable (Jessie), which uses Mesa 10.3.2. Let's see how the Battle.net desktop client renders with this setup:

![Battle.net rendered poorly](https://i.imgur.com/T5QK36j.png)

Erm... right... obviously some issues there. Reading around a while back, I learned that this is because I'm running an Intel chipset with an old version of Mesa. To get things looking pretty, I'd need Mesa 10.4 or later. So now I have two options:

* go crawling back to a distro that tracks upstream packages more closely (e.g. Ubuntu);
* upgrade Mesa.

The latter sounds easy, but there are a few complications, since Mesa is composed of a fair few packages, e.g. libgl1-mesa-dri and libgl1-mesa-glx. There is a fairly complex web of dependencies between these packages, and several other packages need to be upgraded at the same time in order to be able to upgrade Mesa. However, I'm very happy with LMDE and have absolutely no desire to jump ship to another distro, and I figured I might learn something along the way, so I plumped with trying to upgrade Mesa manually.

I mucked around with downloading the source code from the Mesa website and compiling it all myself. This ended with me installing the libraries to the wrong place on my computer then trying to be clever with some soft links to overwrite the existing files, with the result being a broken desktop, misery, fire and death.

In an ideal world there would be backports of Mesa and all the other required packages in jessie-backports. No such luck unfortunately. Trawling the Debian package pages revealed that nobody'd tried to add them in. However, [I learnt](https://www.reddit.com/r/linuxquestions/comments/3uma0p/debian_backports_on_lmde/) that there's [some documentation](https://wiki.debian.org/SimpleBackportCreation) on how to create the backport packages. In the first paragraph of this article, there's a [link](https://wiki.debian.org/CreatePackageFromPPA) to some other instructions on how to create packages from a Ubuntu PPA. For some reason, probably because I vaguely remember PPAs to be quite straightforward, and I knew there were new-ish versions of Mesa in the PPA [here](https://launchpad.net/~oibaf/+archive/ubuntu/graphics-drivers), I decided this would be easier than creating the backport package.

The article details how to create deb package files (\*.deb) from the packages in the PPA, which you *should* just be able to download and install using gdebi/dpkg (see below), so I'm not going to write a detailed step-by-step how-to on how they were created. Instead I'll add links to the pages I found useful and summarise the pitfalls I found along the way.

The first problem I ran into was having both 32- and 64-bit versions of some of the packages installed on my system. When you try to install a newer version of only one of these packages, APT complains that the architecture that you're *not* upgrading is dependent on the old version of the architecture that you *are* upgrading. So what I needed was a way to compile the 32-bit versions of the packages in the PPA. The solution? [PBuilder!](https://wiki.ubuntu.com/PbuilderHowto) This is basically a set of tools to create an isolated system with its own set of packages that sources can be compiled against to generate deb files. In hindsight if I'd know this in advance I would have compiled both architectures using PBuilder, as having an isolated package database means that you completely remove the difficulties of not having the right versions of each architecture installed when compiling from source.

The second problem I had was the circular dependency between libva and the Mesa packages. After some Googling I came across [this](http://www.linuxfromscratch.org/blfs/view/systemd/multimedia/libva.html), which explains that the circular dependency is a result of the libva source tree having some optional packages (libva-glx1 and libva-egl1) that depend on elements of Mesa. The solution in this case was to go into the source tree's `debian` directory and remove the *.install files for these packages. That way, when the build script goes to create the deb files, it doesn't try to make the packages that are going to cause errors. The proviso here is that once the Mesa packages are installed, these optional elements of libva are compiled again to include the Mesa dependency.

The third issue I ran into was how to get the newly generated deb files into the set of packages that PBuilder compiles against so that they can be used when building the remaining packages. After trying various things I discovered the easiest thing to do was just to log in to the virtual system and run dpkg to install these packages manually. By including the `--save-after-login` flag, any changes that were made to the package database are saved when you exit the session.

One of the dependencies required to build these packages is version 3.6 of the LLVM toolchain. Building this from source takes (a) a lot of disk space (~20GB) and (b) the rest of your natural life. Luckily I have a relatively new dual-core CPU with hyperthreading enabled, and some searching revealed I could parallelize the build by running `export DEB_BUILD_OPTIONS='parallel=4'` before executing the PBuilder build command, 4 being the number of build processes I wanted to run in parallel.

The last problem I ran into was trying to install the resulting packages using dpkg in a sequential fashion. I wanted to install each package individually so that I could ensure that the deb files worked as expected. In most cases this worked fine without issue. However, when it came to installing the Mesa deb files, the dependencies between the packages were so strong that they had to be installed together as part of the same dpkg command.

After several days of fiddling/researching/compiling/getting stuck/fixing, I finally managed to generate a set of deb files that should allow anyone on Debian Jessie or its derivatives to install Mesa 11.2. In my case, Battle.net now looks like this:

![Battle.net rendered properly](https://i.imgur.com/rQpnuUH.png)

Hurrah! Victory! Now I can just load Battle.net and launch WoW without the fuss of having to login within WoW itself.

I've uploaded the deb files as a tarball to my public Dropbox, which you can access [here](https://dl.dropboxusercontent.com/u/59986210/mesa-11.2-debs.tgz). The file is around 1GB in size, so depending on your internet connection it may take some time to download. I strongly recommend checking which packages you have installed first by running `aptitude search <package name>` or similar, so that you don't end up installing packages you don't need. Once you've got the list of packages you want to install, I'd recommend listing all the corresponding deb files in a single dpkg command, in order to escape the dependency issues I've mentioned above. If you have any problems installing these packages, please use the contact form on this website to let me know, and if there are issues that keep cropping up I'll post an update here.

EDIT: I guess this should go without saying. I haven't thoroughly tested these deb files on a range of systems, so if you do try to install them, you do so at your own risk. I can't take any responsibility for damage to your system resulting from trying to install these deb files.

UPDATE (15/02/2016): Looks like some kind soul has backported the right packages from stretch to [jessie-backports](https://packages.debian.org/jessie-backports/libgl1-mesa-glx), so now it's easier to stay up-to-date with the newer version :-).
