import random
import numpy
import sys
import time as ttt
from transaction_object import transaction
#from global_data import data
import global_data
from event import Event
from Block import block
class node:
    def __init__(self,id1,ttx,adjacent,coins_list):
        self.id1=id1
        self.ttx=ttx #ttx us mean for transaction generation
        self.adja=adjacent #list of neighbours of this node
        self.pending_transaction_list=[]
        self.Block_tree_dict={}  # dictionary where key is block_id and value is list of three thing : block object,length,coins_list and time at which this block is added into tree
        self.leaf_blocks_list=[] # contains all leaf blocks id 
        self.coins_list=coins_list
        #self.global_data_obj=global_data_obj
        #create genesis block
        self.genesis_block=block(0,self.id1,[],-1,self.coins_list,0)  #creating genesis block
        lis=[]
        lis.append(self.genesis_block)
        lis.append(1)
        lis.append(coins_list)
        lis.append(0)
        # print("coins list in genesis block at node ",self.id1)
        # print(coins_list)
        self.Block_tree_dict.update({0:lis})
        self.leaf_blocks_list.append((self.genesis_block).bkid)  
        global_data.block_id_list[self.id1].append(0)
        if self.id1==0:
            self.private_chain=[]
            self.public_chain=[]
            self.lead=0
            self.public_chain.append(self.genesis_block)
        self.new_block_formed_but_not_mined=[]
        self.pending_block_list=[]  #list of blocks which are arrived but not added into blockchain at node i
        self.pending_block_id_list=[]
        self.created_block_list_id=[]# list of blocks id which are created by node 
        # print("coins list in genesis block at node ",self.id1)
        # print(self.Block_tree_dict[0][2])

    def validate_block(self,blk):  # this function will validate the block before adding into block chain if it is valid then new modified list of coins it have would be return otherwise empty list would be returned
        #print("iam n validate function")
        parent_blk_coins_list=[]  #this list holds coins information of all nodes that parents blocks have 
        pa=blk.parent_bkid
        #print(pa)
        parent_blk_coins_list=list(self.Block_tree_dict[pa][2])
        # if pa==0:
        #     print("genesis coin list")
        #     print(parent_blk_coins_list)
        flag=0
        global_data.arun=global_data.arun+1
        for i in blk.txn_list:
            #print("number of coins")
            #print(i.coins)
            #print(i.sender1)
            sender_id1=i.sender1
            receiver_id=i.receiver1
            amount=i.coins
            #print(sender_id1)
            if parent_blk_coins_list[sender_id1]-amount<0:  # invalid condition
                flag=1
                x=pa
                temp_li=[]
                while x!=0:
                    temp_li.append(self.Block_tree_dict[x][2][sender_id1])
                    x=self.Block_tree_dict[x][0].parent_bkid
                temp_li.append(self.Block_tree_dict[x][2][sender_id1])
                # print(temp_li)    
                # print("parent amount and this amount",parent_blk_coins_list[sender_id1],amount)
                break
            if sender_id1==receiver_id:  # for coinchain mining fee transaction
                parent_blk_coins_list[sender_id1]=parent_blk_coins_list[sender_id1]+50
            else:   
                parent_blk_coins_list[sender_id1]=parent_blk_coins_list[sender_id1]-amount
                parent_blk_coins_list[receiver_id]=parent_blk_coins_list[receiver_id]+amount
        if flag==1:
            if flag==1:
              global_data.total_invalid=global_data.total_invalid+1
              
                
              return []
        return parent_blk_coins_list

    
    def transaction_generate(self,time,type,coins,txid,n): 
        temp_event_list=[]  # this list stores all event object which will be made due to this function
        x=numpy.random.exponential(self.ttx,1)  # randomly generateing transaction cycle time for next transaction generation
        tk=time+x[0]
        ev=Event(self.id1,self.id1,'TXN_GEN',tk,'abhijeet','123')  # this event is special for starting the next  transaction generation process i am not sending any transaction
        temp_event_list.append(ev)

        if type=='intial':
            tx=transaction(self.id1,self.id1,coins,'i',txid) # transaction object is created
            
            self.pending_transaction_list.append(tx) # adding into pending transaction
            global_data.transaction_list[self.id1].append(tx)
            global_data.transaction_id_list[self.id1].append(tx.txn_id)
            # now we will broad cast the tx transaction to its neighbours
            for i in self.adja:
                 
                Cij=100000
                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                    Cij=5000
                x=x=numpy.random.exponential(0.096/Cij,1)
                dij=x[0]
                p=sys.getsizeof(tx)/Cij
                Lij=global_data.pij+p+dij
                ti=time+Lij  # so at ti time this evenet will be executed by the node i
                ev=Event(self.id1,i,'TXN_REC',ti,tx,'123')   # creating event for receiveing tranasaction tx by node i passed node self.id1
                temp_event_list.append(ev)                    
        else:
            rc=random.randint(0,n-1)    # rc will be the receiver of the transaction 
            while(rc==self.id1):
                rc=random.randint(0,n-1)
            tx=transaction(self.id1,rc,coins,'n',txid)  # tranasaction object is created where sender is id1 and receiver of coins will be rc
            global_data.transaction_list[self.id1].append(tx)
            global_data.transaction_id_list[self.id1].append(tx.txn_id)
            self.pending_transaction_list.append(tx)
           
            #broad cast to every_one
            # to send this tx to neighbour we will create an event 
            for i in self.adja:
                   
                Cij=100000
                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                    Cij=5000
                x=x=numpy.random.exponential(0.096/Cij,1)
                dij=x[0]
                p=sys.getsizeof(tx)/Cij
                Lij=global_data.pij+p+dij
                ti=time+Lij   # this Lij is time of delay for sending to other node neighbour
                ev=Event(self.id1,i,'TXN_REC',ti,tx,'123')
                temp_event_list.append(ev)
        return temp_event_list

    def receive_transaction(self,receiver1,sender1,time,n,tx):
        # tx is transaction object that receiver has received from sender
        temp_event_list=[]
        if tx.txn_id in global_data.transaction_id_list[self.id1]:  # transaction already arrived so negelect this event now
            return temp_event_list
        
        self.pending_transaction_list.append(tx)  # adding into pending transaction  
        global_data.transaction_list[self.id1].append(tx)  # adding into transaction list of this node which means he has received transaction
        global_data.transaction_id_list[self.id1].append(tx.txn_id)
        #broadcast or forward tx to neighbours
        for i in self.adja:
            if i!=sender1:
                 
                Cij=100000
                x=numpy.random.exponential(0.096/Cij,1)
                dij=x[0]
                p=sys.getsizeof(tx)/Cij
                Lij=global_data.pij+p+dij
                ti=time+Lij
                ev=Event(self.id1,i,'TXN_REC',ti,tx,'123')
                temp_event_list.append(ev)
        return temp_event_list    

    def receive_block(self,sender,receiver,time,n,blk): # this function will receive block
        #print("i am receiving")
        temp_event_list=[]
        x=blk.bkid
        if  x in global_data.block_id_list[self.id1]:  # already block receicved so return or stop here
            #print("already present in the ")
            return temp_event_list    
 # first time received block blk
        global_data.block_list[receiver].append(blk)     # store block blk in list of received block
        global_data.block_id_list[receiver].append(x)
        if blk.parent_bkid not in self.Block_tree_dict.keys():  # adding block into pending blocks if its parent is not their in blockchain tree we are not checking wether block is valid or not this we will check at block to be added in blockchain
            self.pending_block_list.append(blk)
            self.pending_block_id_list.append(blk.bkid)
            return temp_event_list
        # if blk.parent_bkid==0:
        #     print("before validating genesis block amount is ")
        #     print(self.Block_tree_dict[0][2])
        x1=node.validate_block(self,blk)  # validating wether block is valid or not and it return modified coin_list that is to be present with this block in the chain
        # if blk.parent_bkid==0:
        #     print("just validated the genesis block")
        #     print(self.Block_tree_dict[0][2])


        if len(x1)==0:
                print("invalid block",blk.bkid," in node ",self.id1)
                #global_data.invalid_blocks_id[self.id1].append(blk.bkid)
                return temp_event_list
              
              # if block is invalid 
            #print("recieved block is invalid")
            
        # blk is valid to be for added in chain
        if self.id1==0:
            height_of_new_received_block=self.Block_tree_dict[blk.parent_bkid][1]+1
            flag_for_=0
            if height_of_new_received_block>len(self.public_chain):# action will be taken because arrived block is part of public chain
                if blk.parent_bkid!=self.public_chain[-1].bkid:  # created or modify public chain
                    self.public_chain.clear()
                    x=blk.parent_bkid
                    while x>=0:
                        self.public_chain.append(self.Block_tree_dict[x][0])
                        x=self.Block_tree_dict[x][0].parent_bkid
                    self.public_chain.reverse()
                    self.public_chain.append(blk)
                else:
                    self.public_chain.append(blk)    
                print("block ",blk.bkid," whose parent is ",blk.parent_bkid," is received by selfish minner")
                if self.lead==-1:
                    print("lead is -1 ,no private chain is there and honest block is receive and after public chain is")
                    #self.public_chain.append(blk)
                    self.lead=0
                    for j in self.public_chain:
                        print(j.bkid)
                    print(" lead is 0 due to honest block received")    
                elif self.lead==0:
                    print("lead == 0  , no private chain and public chain is: ")
                    for j in self.public_chain:
                        print(j.bkid)
                    print("public chain finished and lead remains 0")    
                    self.lead=0
                    self.private_chain.clear()  # as lead =0 therefore no selfish mining is started so private chain will be empty
                elif self.lead==1: # doubt whetere it will go to 0^' state or just o state only
                    print("lead ==1 , no private chain and final public chain is ")
                    released_block=self.private_chain[-1]
                    self.public_chain=list(self.private_chain) # as the private chain becomes public chain now
                    self.private_chain.clear()
                    self.lead=-1
                    for j in self.public_chain:
                        print(j.bkid)
                    print("public chain finished and lead becomes -1")

                    # broadcast released block
                    blk1=released_block
                    for i in self.adja:
                            if i!=sender and blk1.bkid not in global_data.block_id_list[i]:
                                 

                                Cij=100000
                                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                    Cij=5000
                                x=x=numpy.random.exponential(0.096/Cij,1)
                                dij=x[0]
                                p=sys.getsizeof(blk1)/Cij
                                Lij=global_data.pij+p+dij
                                
                                ti=time+Lij
                                ev=Event(self.id1,i,'BLK_REC',ti,blk1,blk1.parent_bkid)
                                temp_event_list.append(ev)
                elif self.lead==2:
                    print("lead is 2 ,no final private chain after this and public chain is: ")
                    # broadcast all blocks of private chain
                    for j in self.private_chain:
                        blk1=j
                        for i in self.adja:
                            if i!=sender and blk1.bkid not in global_data.block_id_list[i]:
                                 

                                Cij=100000
                                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                    Cij=5000
                                x=x=numpy.random.exponential(0.096/Cij,1)
                                dij=x[0]
                                p=sys.getsizeof(blk1)/Cij
                                Lij=global_data.pij+p+dij
                                
                                ti=time+Lij
                                ev=Event(self.id1,i,'BLK_REC',ti,blk1,blk1.parent_bkid)
                                temp_event_list.append(ev)
                    self.public_chain=list(self.private_chain) # as the private chain becomes public chain now
                    self.private_chain.clear()
                    self.lead=0
                    for j in self.public_chain:
                        print(j.bkid)
                    print("public  chain is finished and lead becomes 0")
                else:
                    print("lead is greater than 2 , there is private chain and public chain is ")
                    released_block=self.private_chain[-self.lead]
                    self.public_chain=list(self.private_chain[:1+len(self.private_chain)-self.lead])
                    self.lead=self.lead-1
                    for j in self.public_chain:
                        print(j.bkid)
                    print("public chain finished and private chain is now :")
                    for j in self.private_chain:
                        print(j.bkid)
                    print("private chain finsished and lead becomes ",self.lead)        
                    # broadcast this whole public list
                    for j in self.public_chain:
                        blk1=j
                        for i in self.adja:
                            if i!=sender and blk1.bkid not in global_data.block_id_list[i]:
                                 

                                Cij=100000
                                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                    Cij=5000
                                x=x=numpy.random.exponential(0.096/Cij,1)
                                dij=x[0]
                                p=sys.getsizeof(blk1)/Cij
                                Lij=global_data.pij+p+dij
                                
                                ti=time+Lij
                                ev=Event(self.id1,i,'BLK_REC',ti,blk1,blk1.parent_bkid)
                                temp_event_list.append(ev)

     
        #code for storing this block blk into blockchain of node self.id1
        temp_list=[]
        temp_list.append(blk)
        leng=self.Block_tree_dict[blk.parent_bkid][1]+1
        temp_list.append(leng)
        modified_coins_list=x1
        temp_list.append(modified_coins_list)
        temp_list.append(time)
        self.Block_tree_dict.update({blk.bkid:temp_list})   # now i have added this blk into chain this block is received from another node
        # CODE TO ADD: RECURSIVELY :DO SEARCH IN THE LIST OF BLOCK NOT ADDED IN TREE_CHAIN i.e pending block list SUCH THAT  if RECENTLY ADDED BLOCK IS PARENT OF THE BLOCK PRESENT IN THIS LIST then we have to add child block in blockchian tree UPTO WHEN LIST BECOMES EMPTY OR NO CHILD IS PRESENT IN THE pending block list
            # add this block in the block chain of node id
        y1=blk.bkid
        # below code is to add all pending blocks from pending block list into blocks tree such that when parent is their in tree then add block into tree recursively
        flag=0
        broadcast_block_list=[]
        flag=1
        while flag==1:
            flag=0
            for j in self.pending_block_list:
                if j.parent_bkid in self.Block_tree_dict.keys():
                    z=node.validate_block(self,j)  # validate block before adding into tree
                    if len(z)==0:
                        self.pending_block_id_list.remove(j.bkid) 
                        self.pending_block_list.remove(j)
                    else:# block is valid then add block into tree
                        flag=1
                        #print(" i am inside recursion of node ",self.id1)
                        y1=j.parent_bkid
                        temp_list=[]
                        temp_list.append(j)
                        leng=self.Block_tree_dict[y1][1]+1
                        temp_list.append(leng)
                        temp_list.append(z)
                        temp_list.append(time)
                        self.Block_tree_dict.update({j.bkid:temp_list})
                        #y1=j.bkid
                        broadcast_block_list.append(j)
                        #flag=1
                        self.pending_block_id_list.remove(j.bkid) 
                        self.pending_block_list.remove(j)
        



        
        #print("added into block in receive block")   
        # forward this recieve block to neighbours 
        if self.id1!=0:
            for i in self.adja:
                if i!=sender and blk.bkid not in global_data.block_id_list[i]:
                     

                    Cij=100000
                    if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                        Cij=5000
                    x=x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(blk)/Cij
                    Lij=global_data.pij+p+dij
                    ti=time+Lij
                    ev=Event(self.id1,i,'BLK_REC',ti,blk,blk.parent_bkid)
                    temp_event_list.append(ev)
        #code for broadcasting remaining recently added blocks in the chain
        while len(broadcast_block_list)>0:
            block1=broadcast_block_list.pop(0)
            for i in self.adja:
                if block1.bkid not in global_data.block_id_list[i]:
                     

                    Cij=100000
                    if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                        Cij=5000
                    x=x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(block1)/Cij
                    Lij=global_data.pij+p+dij
                    ti=time+Lij
                    ev=Event(self.id1,i,'BLK_REC',ti,block1,block1.parent_bkid)
                    temp_event_list.append(ev)


            

        # code for checking longest chain         
        flag=1
        test_height=self.Block_tree_dict[blk.bkid][1]
        for i in self.Block_tree_dict.keys():
            if test_height<self.Block_tree_dict[i][1]:
                flag=0
                break
        if flag==0: # means received block does not form longest chain then stop the event
            return temp_event_list
        #code for mining pow process
        # forming new block 
        #code to form selecting transaction 
        tran_list=[]
        k=0
        while k<10 and len(self.pending_transaction_list)>0:
            tran_list.append(self.pending_transaction_list.pop(0)) # removing from pending transaction and adding transaction into list
            k=k+1
        global_data.blockId=global_data.blockId+1 # creating block id for new block to be created 
        self.created_block_list_id.append(global_data.blockId)    
        
        temp_height=0
        #code for adding finding height of the maximum distant leaf from genesis block
        pa=0 #represent block which has highest length from root block in tree
        for i in self.Block_tree_dict.keys():
            if temp_height<self.Block_tree_dict[i][1]:
                temp_height=self.Block_tree_dict[i][1]
                pa=i
        # create valid code remaining
        # create new block object at time time taking parent id as above one 
        bx=block(global_data.blockId,self.id1,tran_list,pa,blk.coins_list,time) #    formation of block
        
        #Tk=20  # Tk is to be calculated  by EXPO(I/hashing power)
        # calculating time for next block generation process to occure or to validate this block after mining time 
        # this is just to calculate mining time required for above block 

        if self.id1==0:
            if self.lead==0:
                pa=self.public_chain[-1].bkid
                bx.parent_bkid=pa
            elif self.lead==-1:
                pa=self.public_chain[-1].bkid
                bx.parent_bkid=pa
            else:
                pa=self.private_chain[-1].bkid 
                bx.parent_bkid=pa   

        if self.id1==0:
            Tk=numpy.random.exponential(10/global_data.selfish_power,1)
        elif self.id1 in global_data.low_cpu:
            Tk=numpy.random.exponential(10/global_data.slow_rate,1)
        else:    
            Tk=numpy.random.exponential(10/(global_data.slow_rate*10),1)
        Tk=Tk[0]

        ek=Event(self.id1,self.id1,'BLK_GEN',time+Tk,bx,pa)  # this event is to verify the block just created on which node mined is valid and has maximum height after mining time so in between no new longest chian is created or not
        temp_event_list.append(ek)
        return temp_event_list

    def Block_generation(self,block1,parent_blk_id,time):
        temp_event_list=[]
        test_height=self.Block_tree_dict[parent_blk_id][1]
        flag=1
        # checking wether the block created before mining time is making same height maximum or not 
        for i in self.Block_tree_dict.keys():
            if test_height<self.Block_tree_dict[i][1]:
                flag=0
                break
        #if flag is 0 means that current block mining is not to be done  as new greater chain is formed
        # otherwise this block will have new mining award transaction and this block will be added into chain and broadcasted into the netwoerk
        if flag==1:
            global_data.transaction_id=global_data.transaction_id+1 # this is for coin_base transaction
            txn_object=transaction(self.id1,self.id1,50,'coin_base',global_data.transaction_id) # coinbase transaction
            #print("beflore clakdflaksdjfl;jlfjd",txn_object.sender1)
            block1.txn_list.append(txn_object) # adding transaction in block transaction list
            x=node.validate_block(self,block1)  #verify block
            # 
            if len(x)>0:
                broadcast_block_list=[]
                if block1 not in global_data.block_list[self.id1]:
                    global_data.block_list[self.id1].append(block1)
                    if block1.bkid not in global_data.block_id_list[self.id1]:
                        global_data.block_id_list[self.id1].append(block1.bkid)
                        #global_data.very_wrong=global_data.very_wrong+1


         
                
               
                #taking action on mining on which chain private or public 
                if self.id1==0:
                    print("new block is minned ",block1.bkid)
                    if self.lead==-1:
                        pa=self.public_chain[-1].bkid
                        block1.parent_bkid=pa
                        self.public_chain.append(block1)
                        self.lead=0
                        blk1=block1
                        for i in self.adja:
                            if blk1.bkid not in global_data.block_id_list[i]:
                                Cij=100000
                                if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                    Cij=5000
                                x=x=numpy.random.exponential(0.096/Cij,1)
                                dij=x[0]
                                p=sys.getsizeof(blk1)/Cij
                                Lij=global_data.pij+p+dij
                                #Lij=100
                                ti=time+Lij
                                ev=Event(self.id1,i,'BLK_REC',ti,blk1,blk1.parent_bkid)
                                temp_event_list.append(ev)
                   


                    elif self.lead==0:
                        pa=self.public_chain[-1].bkid
                        block1.parent_bkid=pa
                        self.private_chain=list(self.public_chain)
                        self.private_chain.append(block1)
                        self.lead=1
                    else:
                        pa=self.private_chain[-1].bkid 
                        block1.parent_bkid=pa
                        self.private_chain.append(block1)
                        self.lead=self.lead+1
                    print("lead is ",self.lead)
                    print("updated private chain is")
                    for j in self.private_chain:
                        print(j.bkid)
                    print("private chain printing finished") 
                    print("print public chain after mining block is added in private chain")
                    for j in self.public_chain:
                        print(j.bkid)
                    print("public chain printed")           


                #storing in the blockchain this block

                temp_list=[]
                temp_list.append(block1)
                leng=self.Block_tree_dict[block1.parent_bkid][1]+1
                temp_list.append(leng)
                modified_coins_list=self.Block_tree_dict[parent_blk_id][2]
                temp_list.append(modified_coins_list)
                temp_list.append(time)
                self.Block_tree_dict.update({block1.bkid:temp_list})
                # code to recursively add block in blockchain tree from pending list
                x=block1.bkid
                # code to store all remaining blocks into the chain from pending list recursievley
                flag=0
                while len(self.pending_block_id_list)>0:
                    #print(" i am in recursion loop")
                    flag=0
                    for j in self.pending_block_list:
                        if j.parent_bkid in self.Block_tree_dict.keys():
                            # add this block into tree and remove from pending lists
                            z=node.validate_block(self,j)
                            if len(z)==0:
                                self.pending_block_id_list.remove(j.bkid) 
                                self.pending_block_list.remove(j)
                            else:    
                                temp_list=[]
                                temp_list.append(j)
                                leng=self.Block_tree_dict[x][1]+1
                                temp_list.append(leng)
                                temp_list.append(z)
                                temp_list.append(time)
                                self.Block_tree_dict.update({j.bkid:temp_list})
                                x=j.bkid
                                broadcast_block_list.append(j)
                                flag=1
                                self.pending_block_id_list.remove(j.bkid) 
                                self.pending_block_list.remove(j)
                                break
                    if flag==0:
                        break
                #print("block added into tree in generator")
                #broadcast block 
                if self.id1!=0:
                    for i in self.adja:
                        if i!=self.id1 and block1.bkid not in global_data.block_id_list[i]:
                            
                            Cij=100000
                            if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                Cij=5000
                            q1=numpy.random.exponential(0.096/Cij,1)
                            dij=q1[0]
                            p=sys.getsizeof(block1)/Cij
                            Lij=global_data.pij+p+dij
                            ti=time+Lij
                            ev=Event(self.id1,i,'BLK_REC',ti,block1,block1.parent_bkid)
                            temp_event_list.append(ev)

                #broadcast remaining blocks
                while len(broadcast_block_list)>0:
                    block12=broadcast_block_list.pop(0)
                    for i in self.adja:
                        if block12.bkid not in global_data.block_id_list[i]:
                             

                            Cij=100000
                            if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                                Cij=5000
                            q1=numpy.random.exponential(0.096/Cij,1)
                            dij=q1[0]
                            p=sys.getsizeof(block12)/Cij
                            Lij=global_data.pij+p+dij
                            ti=time+Lij
                            ev=Event(self.id1,i,'BLK_REC',ti,block12,block12.parent_bkid)
                            temp_event_list.append(ev)

        # forming new block 
    #code to form selecting transaction 
  # code for finding new transactions to be added into new block which will be mined and mining process is started for new block
        k=0
        tran_list=[]
        while k<10 and len(self.pending_transaction_list)>0:
            tran_list.append(self.pending_transaction_list.pop(0))
            k=k+1
        global_data.blockId=global_data.blockId+1  # taking new blockid for block to be created for mining
        #code to current maximum height block finding
        pa=0
        temp_height=0
        for i in self.Block_tree_dict.keys():
            if temp_height<self.Block_tree_dict[i][1]:
                temp_height=self.Block_tree_dict[i][1]
                pa=i
         #validat transaction list
         # create new block object on which node will be mining now
        bx=block(global_data.blockId,self.id1,tran_list,pa,self.Block_tree_dict[pa][2],time) # here 20 is the Tk   
        
        self.created_block_list_id.append(global_data.blockId)


        if self.id1==0:
                    if self.lead==0 or self.lead==-1:
                        pa=self.public_chain[-1].bkid
                        bx.parent_bkid=pa
                    else:
                        pa=self.private_chain[-1].bkid 
                        bx.parent_bkid=pa
        # calculate the mining time
        if self.id1==0:
            Tk=numpy.random.exponential(10/global_data.selfish_power,1)
        elif self.id1 in global_data.low_cpu:
            Tk=numpy.random.exponential(10/global_data.slow_rate,1)
        else:    
            Tk=numpy.random.exponential(10/(global_data.slow_rate*10),1)
        Tk=Tk[0]
         # Tk is to be calculated 
        # create event to verify mining process and also start mining process on new block
        ek=Event(self.id1,self.id1,'BLK_GEN',time+Tk,bx,pa) # blkgen event is from here where pa is block id whose height is maximum
        temp_event_list.append(ek)
        return temp_event_list                   

    def special_event(self,sender,receiver,time,n,blk):
        #print("sender ",sender," send the block ",blk.bkid," to the reciever ",receiver)
        temp_event_list=[]
        x=blk.bkid
        if  x in global_data.block_id_list[self.id1]:  # already block receicved so return or stop here
            #print("already present in the ")
            return temp_event_list    
 # first time received block blk
        global_data.block_list[receiver].append(blk)     # store block blk in list of received block
        global_data.block_id_list[receiver].append(x)
        if blk.parent_bkid not in self.Block_tree_dict.keys():  # adding block into pending blocks if its parent is not their in blockchain tree we are not checking wether block is valid or not this we will check at block to be added in blockchain
            self.pending_block_list.append(blk)
            self.pending_block_id_list.append(blk.bkid)
            return temp_event_list
        
        x1=node.validate_block(self,blk)  # validating wether block is valid or not and it return modified coin_list that is to be present with this block in the chain


        if len(x1)==0:  # if block is invalid 
            #print("recieved block is invalid")
            return temp_event_list
        #code for storing this block blk into blockchain of node self.id1
        temp_list=[]
        temp_list.append(blk)
        leng=self.Block_tree_dict[blk.parent_bkid][1]+1
        temp_list.append(leng)
        modified_coins_list=x1
        temp_list.append(modified_coins_list)
        #temp_list.append(time)
        largest_time=0
        for k in self.Block_tree_dict.keys():
            if largest_time<self.Block_tree_dict[k][3]:
                largest_time=self.Block_tree_dict[k][3]
        temp_list.append(largest_time+1)
        self.Block_tree_dict.update({blk.bkid:temp_list})   # now i have added this blk into chain this block is received from another node
        # CODE TO ADD: RECURSIVELY :DO SEARCH IN THE LIST OF BLOCK NOT ADDED IN TREE_CHAIN i.e pending block list SUCH THAT  if RECENTLY ADDED BLOCK IS PARENT OF THE BLOCK PRESENT IN THIS LIST then we have to add child block in blockchian tree UPTO WHEN LIST BECOMES EMPTY OR NO CHILD IS PRESENT IN THE pending block list
            # add this block in the block chain of node id
        y1=blk.bkid
        # below code is to add all pending blocks from pending block list into blocks tree such that when parent is their in tree then add block into tree recursively
        flag=0
        broadcast_block_list=[]
        flag=1
        while flag==1:
            flag=0
            for j in self.pending_block_list:
                if j.parent_bkid in self.Block_tree_dict.keys():
                    z=node.validate_block(self,j)  # validate block before adding into tree
                    if len(z)==0:
                        self.pending_block_id_list.remove(j.bkid) 
                        self.pending_block_list.remove(j)
                    else:# block is valid then add block into tree
                        flag=1
                        #print(" i am inside recursion of node ",self.id1)
                        y1=j.parent_bkid
                        temp_list=[]
                        temp_list.append(j)
                        leng=self.Block_tree_dict[y1][1]+1
                        temp_list.append(leng)
                        temp_list.append(z)
                        largest_time=0
                        for k in self.Block_tree_dict.keys():
                            if largest_time<self.Block_tree_dict[k][3]:
                                largest_time=self.Block_tree_dict[k][3]
                        temp_list.append(largest_time+1)
                        self.Block_tree_dict.update({j.bkid:temp_list})
                        #y1=j.bkid
                        broadcast_block_list.append(j)
                        #flag=1
                        self.pending_block_id_list.remove(j.bkid) 
                        self.pending_block_list.remove(j)
        



        
        #print("added into block in receive block")   
        # forward this recieve block to neighbours 
        if self.id1!=0 or self.id1==0:
            for i in self.adja:
                if i!=sender and blk.bkid not in global_data.block_id_list[i]:
                    Cij=100000
                    if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                        Cij=5000
                    x=x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(blk)/Cij
                    Lij=global_data.pij+p+dij
                    ti=time+Lij
                    ev=Event(self.id1,i,'special',ti,blk,blk.parent_bkid)
                    temp_event_list.append(ev)
        #code for broadcasting remaining recently added blocks in the chain
        while len(broadcast_block_list)>0:
            block1=broadcast_block_list.pop(0)
            for i in self.adja:
                if block1.bkid not in global_data.block_id_list[i]:
                     

                    Cij=100000
                    if  i in global_data.slow_node or self.id1 in global_data.slow_node:
                        Cij=5000
                    x=x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(block1)/Cij
                    Lij=global_data.pij+p+dij
                    ti=time+Lij
                    ev=Event(self.id1,i,'special',ti,block1,block1.parent_bkid)
                    temp_event_list.append(ev)
        return temp_event_list
    

