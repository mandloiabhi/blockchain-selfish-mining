class block:
    def __init__(self,bkid,generator,txn_list,parent_bkid,coins_list,time_stamp):
        self.bkid=bkid
        self.generator=generator
        self.txn_list=txn_list
        self.parent_bkid=parent_bkid
        self.coins_list=coins_list
        self.time_stamp=time_stamp