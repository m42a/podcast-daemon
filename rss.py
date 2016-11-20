#!/usr/bin/env python3
import calendar
import feedparser
import os
import sqlite3
import subprocess

podcast_dir="/home/m42a/podcasts"

def main():
    feed_dir=os.path.join(podcast_dir, "feeds")
    conn=sqlite3.connect(os.path.join(feed_dir, "rss.sqlite3"))
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS feeds(url TEXT PRIMARY KEY NOT NULL, last_update INT NOT NULL, etag TEXT, modified TEXT)")
    conn.commit()

    urls=set()
    feed_info={}
    for feed in os.listdir(feed_dir):
        if feed == "rss.sqlite3" or feed == "rss.py":
            continue
        print(feed)
        fname=os.path.join(feed_dir, feed)
        url=None
        try:
            with open(fname) as f:
                url=f.read().strip()
        except (OSError, IOError):
            continue
        if not url:
            continue
        cur.execute("INSERT OR IGNORE INTO feeds VALUES (?,?,NULL,NULL)", [url, 0])
        cur.execute("SELECT last_update, etag, modified FROM feeds WHERE url=?", [url])
        (last_update,etag,modified)=cur.fetchone()
        conn.commit()
        feed_update=last_update

        feed=feedparser.parse(url)
        if "etag" in feed:
            etag=feed.etag
        if "modified" in feed:
            modified=feed.modified
        for entry in feed.entries:
            if not 'enclosures' in entry or not 'published_parsed' in entry:
                continue
            entry_time=calendar.timegm(entry.published_parsed)
            if entry_time <= last_update:
                continue
            for enc in entry.enclosures:
                if 'href' in enc:
                    urls.add(enc.href)
            if entry_time > feed_update:
                feed_update=entry_time
        feed_info[url]={"update": feed_update, "etag": etag, "modified": modified}

    if len(urls):
        subprocess.run(["wget", "-c", "--limit-rate=100k", "-P", podcast_dir, "--"] + list(urls), check=True)
    for feed in feed_info:
        f=feed_info[feed]
        cur.execute("UPDATE feeds set last_update=?, etag=?, modified=? WHERE url=?", [f["update"], f["etag"], f["modified"], feed])
    conn.commit()

if __name__ == "__main__":
	main()
