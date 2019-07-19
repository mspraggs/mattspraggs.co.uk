Title: Coming to you Live from a Cloudfront Server Near you!
Date: 2019-07-18 23:36:00
Category: Blog
Tags: AWS, Engineering
Author: Matt Spraggs

Wow... it's been a year since I last wrote here.

Awkward.

I do have some excuses. This time last year I was in the middle of getting ready
to get married. It's not exactly something you can do over a weekend. Unless you
get married in Vegas. Maybe. Anyway, we didn't go to Vegas. 

Not long after that I started job-hunting again after feeling the urge for
something new. Like so many things, this expanded to fill almost all of my free
time, since the application process for development roles is apparently more
stressful than doing a presentation in front of thousands of people. Or maybe
that's just me? Not sure. In any case, it was a big time sink.

Then we moved flat. I was offered a job in London, and commuting from
Southampton was about as much fun as trimming your toenails with a hammer, so
my wife and I decided to move closer to London. More stress. Yay.

So I've been busy.

Anyway, if you're a regular here (I like to flatter myself with idea that I have
a regular readership...) you'll notice that the site looks a bit different. Yep,
I got bored with the old design and decided to strip things down to something
simpler. Gone are superfluous portfolio pages I'll never have the patience to
write, along with the history section that was hopelessly out-of-date.
(Like seriously, who needs that kind of stuff when there's GitHub and LinkedIn
buttons to take you directly to my relevant pages?)

The other motivation for throwing out the old design was more technical. See,
the old site was built on Django. Django's nice. Django's lovely. Perfect for a
global news outlet or some other enterprise-scale website. However, I'm the sole
content-creator here. Couple that with the fact that I was writing all my posts
in markdown anyway, I figured I may as well cut out the middle-man and use a
static site generator. No server-side stuff, so nothing to hack or otherwise
break.

I plumped for [Pelican](https://docs.getpelican.com/en/stable/), which is
written in Python and uses the Jinja2 template engine. Around a day of writing
a custom theme and _boom_, here we are.

The massive advantage of having a static site is that I can now host it on
static storage services like AWS S3 or GCP Cloud Storage, which cuts my
maintenance workload to zero. The old site used to run on AWS Lightsail, which
essentially involved maintaining an entire machine, including all the faff that
goes with keeping packages up-to-date and so on. Now all I have to do is throw a
load of files at Amazon and let them deal with it. What's more, the site costs
virtually nothing to host now, because I'm only paying for storage space, of
which I use almost nothing.

At the risk of gushing over AWS, it gets even better. Whereas before I had one
server running _somewhere_ in the UK, I can now leverage Cloudfront to host my
site in multiple locations worldwide. That's right, you can view my tedious
ramblings at the same great download speeds wherever you are. And because I'm
using Cloudfront, I can take advantage of Amazon's SSL/TLS certificate signing,
where before I was using LetsEncrypt.

Okay. Time to stop providing Amazon with free advertising. Jeff Bezos is rich
enough without my help. I promise I'll try to write here again soon. Okay, so I
can't promise I'll try, but I'll try to try.
