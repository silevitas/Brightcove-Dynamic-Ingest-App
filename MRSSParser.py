#! /usr/bin/python
# -*- coding: utf-8 -*-
print "Content-type: application/json\n\n"

#For Dynamic Ingest API, see here: http://docs.brightcove.com/en/video-cloud/di-api/samples/batch-dynamic-ingest.html

#Importing the other script in our app: brightcove.py — this contains all the logic for creating a video
#object in the Brightcove CMS and using the Dynamic Ingest API to ingest the video asset via its
#source URL

import BC_01

import json

import feedparser 


d = feedparser.parse('[Inset Your Feed URL here]')
response_array = []


#For each item in the feed

for index, post in enumerate(d.entries): 
    if index >= 12:
        break             
    print post.title+":"
    #print post.link+""
    print post.description+":"
    #print post.media_keywords+":"
    
    
    #Here we set up a dictionary in order to extract selected data from the original brightcove "post" result
    
    item = {}
    item['name'] = post.title
    item['description'] = post.description
    #item['url'] = u"%s" % post.link       
    item['tags'] = post.media_keywords.split(",")
    

    #Below is a for loop that iterates through an MRSS or JSON feed that has multiple-bitrate video renditions.
    #If you're feed doesn't have multiple rendention, you can delete or comment out the loop below and just use
    #the element with the video URL in your feed, usually called "link" or "url"
    
    # -- initially we say the highest bitrate is 0 (since we dont have any video yet)
    max_bitrate = 0
    vid_url = None 
    videos = post.media_content
    
    # -- For each video in the item
    for video in videos:
        # -- If the video has a value for its bitrate
        if 'bitrate' in video:
            # -- Extract the value of this video's bitrate
            bitrate_str = video['bitrate']
            # -- and convert it to an integer (by default it is a string in the XML)
            curr_bitrate = int(bitrate_str)
            # -- If the bitrate of this video is greater than
            # -- the highest bitrate we've seen, mark this video as the one with
            # -- the highest birate.
            if curr_bitrate > max_bitrate:
                max_bitrate = curr_bitrate
                vid_url = video['url']
            # -- This line simply prints out the maximum bitrate and current video URL for each iteration
    #print "{} url {}".format(max_bitrate, vid_url)
    #print "highest bitrate {} url {}".format(max_bitrate, vid_url)
    
    item['url'] = vid_url
    
    response_array.append(item)

refactored = []
for entity in response_array:
    new_el = entity
    new_el["name"] = entity["name"]
    new_el["description"] = entity["description"]

    refactored.append(new_el)
print json.dumps(response_array, indent=4)

#Here's our response_array that contains all the necessary information about our video. We then call our dedupe function and
#Dynamic Ingest function. 

for item in response_array:
    name, url = item['name'], item['url']
    tags = item["tags"] if "tags" in item else []
    desc = item["description"] if "description" in item else ""
    if not BC_01.videoNameExists(name):     #Calling our dedupe function
        print "did not see", name, "in brightcove, ingesting..."
        BC_01.createAndIngest(name, url, tags, desc)  #If no duplicates, call our Brightcove Dynamic Ingest function
    else:
        print "already saw", name, "skipping..."
