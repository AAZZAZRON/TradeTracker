'''
database functions to get/set from pickledb
'''

import pickledb


def init_db():  # remove keys from previous runs
    db = pickledb.load('data.db', False)
    if db.exists('last_trade'):
        db.rem('last_trade')
    if db.exists('last_signing'):
        db.rem('last_signing')
    db.dump()  # save the db



def getLastTradeShown():
    db = pickledb.load('data.db', False)
    if db.exists('last_trade'):
        return db.get('last_trade')
    return None  # if key doesn't exist, then it's the first time running the bot


def setLastTradeShown(data):
    db = pickledb.load('data.db', False)
    db.set('last_trade', data)
    db.dump()  # save the db


def getLastSigningShown():
    db = pickledb.load('data.db', False)
    if db.exists('last_signing'):
        return db.get('last_signing')
    return None  # if key doesn't exist, then it's the first time running the bot


def setLastSigningShown(data):
    db = pickledb.load('data.db', False)
    db.set('last_signing', data)
    db.dump()  # save the db



# channel stuff
def getChannels():
    db = pickledb.load('data.db', False)
    if db.exists('channels'):
        return db.get('channels')
    return []


def addChannel(channel_id):
    db = pickledb.load('data.db', False)
    channels = db.get('channels') or []
    if channel_id not in channels:
        channels.append(channel_id)
        db.set('channels', channels)
        db.dump()  # save the db
        return True
    return False


def removeChannel(channel_id):
    db = pickledb.load('data.db', False)
    channels = db.get('channels') or []
    if channel_id in channels:
        channels.remove(channel_id)
        db.set('channels', channels)
        db.dump()  # save the db
        return True
    return False