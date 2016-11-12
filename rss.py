#!/usr/bin/env python3
import feedparser
import os

podcast_dir="/home/m42a/podcasts"

def main():
    feed_dir=os.path.join(podcast_dir, "feeds")
    urls=set()
    for feed in os.listdir(feed_dir):
        fname=os.path.join(feed_dir, feed)
        url=None
        try:
            with open(fname) as f:
                url=f.read().strip()
        except (OSError, IOError):
            continue
        if not url:
            continue
        feed=feedparser.parse(url)
        for entry in feed.entries:
            if not 'enclosures' in entry:
                continue
            for enc in entry.enclosures:
                if 'href' in enc:
                    urls.add(enc.href)
    os.execvp("wget", ["wget", "-c", "--limit-rate=100k", "-P", podcast_dir, "--"] + list(urls))

if __name__ == "__main__":
	main()
