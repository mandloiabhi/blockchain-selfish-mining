class Event:
    def __init__(self,sender,receiver,type,time,message,parent):
        self.sender=sender
        self.receiver=receiver
        self.type=type
        self.time=time
        self.message=message
        self.parent_id=parent
        