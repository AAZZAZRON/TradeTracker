import pickledb


def isLastTradeShown(data):
    db = pickledb.load('data.db', False)
    if db.exists('last_trade'):
        return db.get('last_trade') == data
    return True  # if key doesn't exist, then it's the first time running the bot


def setLastTradeShown(data):
    db = pickledb.load('data.db', False)
    db.set('last_trade', data)
    db.dump()  # save the db

