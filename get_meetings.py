#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### to use this script you will need to ###
# apt install pip3
# pip3 install bigbluebutton_api_python
# pip3 install pyyaml

import argparse, sys, os, logging, yaml, urllib, json
from bigbluebutton_api_python import BigBlueButton

def get_meetings(bbb, server):
    logging.info("fetching meetings from {}".format(server))
    try:
        meetingsXML = bbb.get_meetings()
        if meetingsXML.get_field('returncode') == 'SUCCESS':
            if  meetingsXML.get_field('meetings') == '':
                logging.info("no meetings running on {}".format(server))
                return []
            else:
                rawMeetings = meetingsXML.get_field('meetings')['meeting']
                if isinstance(rawMeetings, list):
                    logging.info("meetings found on {}".format(server))
                    return json.loads(json.dumps(rawMeetings))
                else:
                    logging.info("meeting found on {}".format(server))
                    return [json.loads(json.dumps(rawMeetings))]
        else:
            logging.error("api request failed")
            return []
    except urllib.error.URLError as ERR:
        logging.error(ERR)
        return []

def get_join_url(bbb, id, name, role='attendee', pw=None):
    pwd = None
    if pw:
        pwd = pw
    elif bbb.get_meeting_info(id):
        minfo = bbb.get_meeting_info(id)
        if role == 'moderator':
            pwd = minfo.get_meetinginfo().get_moderatorpw()
        elif role == 'attendee':
            pwd = minfo.get_meetinginfo().get_attendeepw()
    if pwd:
        return bbb.get_join_meeting_url(name, id, pwd)

def show_meetings(bbb, server, user):
    res = ""
    meetings = get_meetings(bbb, server)
    for meeting in meetings:
        res += (meeting['meetingName'])
        res += ("ID: {}\n".format(meeting['meetingID']))
        res += ("ATTENDEE_PASSWORD: {}\n".format(meeting['attendeePW']))
        joinAttendeeUrl = get_join_url(bbb, meeting['meetingID'], user, 'attendee')
        res += ("JOIN_ATTENDEE_URL: {}\n".format(joinAttendeeUrl))
        res += ("MODERATOR_PASSWORD: {}\n".format(meeting['moderatorPW']))
        joinModeratorUrl = get_join_url(bbb, meeting['meetingID'], user, 'moderator')
        res += ("JOIN_MODERATOR_URL: {}\n".format(joinModeratorUrl))
        res += ("\n")
    return res

def get_running_meetings(server, secret):
	bbb = BigBlueButton(server, secret)
	meetings = get_meetings(bbb,server)
	return map(lambda x: x['meetingID'], meetings)

def get_meeting(server, secret, meetingId):
	bbb = BigBlueButton(server, secret)
	for meeting in get_meetings(bbb, server):
		if(meeting['meetingID'] == meetingId):
			return meeting
	return
			

def main(server, secret, user):
	bbb = BigBlueButton(server,secret)
	return show_meetings(bbb, server, user)
