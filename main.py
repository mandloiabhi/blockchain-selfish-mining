import random
import numpy
import sys
import genrate_graph
from transaction_object import transaction
import global_data as gd
from Node import node
from event import Event
from Block import block 
import time

from graphviz import Source

import networkx as nx
import matplotlib.pyplot as plt
class GraphVisualization:
   
    def __init__(self):
          
        self.visual = []
          
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)
          
    def visualize(self,dict,string1):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        nx.draw_networkx(G,with_labels=True,labels=dict)
        plt.savefig(string1)
        # plt.show()


n = int(sys.argv[1]) # number of nodes in a network
gd.n=n
ttx = int(sys.argv[2])
ttx=ttx/100 # mean time for interarrival between transactions for a node
z = int(sys.argv[3]) # percentage of slow nodes
z=int(((n-1)*z)/100)
low_cpu = int(sys.argv[4]) # percentage of low cpu
gd.selfish_power=int(sys.argv[5])  # percentage of power hold by selfish miner
gd.selfish_power=gd.selfish_power/100
tk=time.time()+20   # after this much time simulation process will stop
low_cpu=int(((n-1)*low_cpu)/100)
li_n=[]
l_cpu=[]
for i in range(1,n):
    li_n.append(i)
for i in range(1,n):
    l_cpu.append(i)
gd.pij=random.uniform(0.001,0.05)    
gd.slow_node=random.sample(li_n,z)   # randomly selecting z nodes for slow node  gd.slow_node store nodes index which are slow
gd.low_cpu=random.sample(l_cpu,low_cpu) #randomly selecting nodes for slow cpu gd.low_cpu stores nodes which has low cpu
#gd.slow_rate=1/(10*n-9*low_cpu)   # gd.slow_rate is fraction hk ie hashing power for low cpu
#gd.slow_rate=1/(low_cpu+(n-1-low_cpu)*10+gd.selfish_power)
gd.slow_rate=(1-gd.selfish_power)/(10*n-9*low_cpu-10)
#print(gd.slow_node)
ttx=ttx
adjacency=[]  # adjacency matrix store  network of nodes graph
adjacency=genrate_graph.generate_graph(n)  # generate graph method creates graph of n nodes which connected and each node has degree between 4 and 8

count=0
for i in range(0,n):
    if(adjacency[0][i]==1):
        count+=1
listOfNumbers=[]
connection_count=int(sys.argv[6])
connection_count=connection_count/100
while(count<connection_count*n):
    for i in range(0,n-1):
        temp=random.randint(1, n-1)
        while(adjacency[0][temp]!=1 and listOfNumbers.count(temp)!=0):
            temp=random.randint(1, n-1)
        adjacency[0][temp]=1
        adjacency[temp][0]=1
        listOfNumbers.append(temp)
        count+=1
#print(listOfNumbers)
print("\n\n\n")  
print(adjacency[0])  
Node_list=[]  # this list stores the Node objects
init_coins_list=[]  # this is intial coin list where ith entry is the number of conins the node have intailly
for i in range(n):
    init_coins_list.append(50)
for i in range(n):     # appending empty lists into various lists of node object
    gd.block_id_list.append([])
    gd.block_list.append([])
    gd.transaction_list.append([])
    gd.transaction_id_list.append([])
    gd.invalid_blocks_id.append([])
    #print(type(gd.invalid_blocks_id))
    temp=[] #temproary list for storeing neighbours of node i
    for j in range(n):
        if adjacency[i][j]==1:
            temp.append(j)
    Node_list.append(node(i,ttx,temp,init_coins_list))  # creating node object and storing in Node_list where i is the node id
print("nodes created")    # ttx is average mean time for transaction generation 
k=1   
txid=1
init_transaction_list=[]  
#creating the intial transaction_list each node is creating or generating  transaction 
for i in range(n):           
    li=[]
    rec=random.randint(0,n-1)
    gd.transaction_id=gd.transaction_id+1

    li=Node_list[i].transaction_generate(gd.time,'intial',5,gd.transaction_id,n)  #calling transaction generate function which will start creating events of generating transaction
    for j in li:
        gd.event_queue_list.append(j)  # gd.vevent_queue is global queue which store all pending events
# code for generating block by each node manually not by making an event of block generating
#print(len(gd.event_queue_list))
gd.blockId=gd.blockId+1
gd.time=gd.time+1
j=0
tran_list=[]
    #choosing pending transaction from pending transaction list
while j<10 and len(Node_list[0].pending_transaction_list)>0:
        tran_list.append(Node_list[0].pending_transaction_list.pop(0))
        j=j+1
        for i in range(n):
            if i!=0:
                Node_list[i].pending_transaction_list.append(tran_list[-1])
bx=block(gd.blockId,i,tran_list,0,init_coins_list,gd.time)
pij=random.uniform(0.01,0.5)
Cij=100000
if  i in gd.slow_node or j in gd.slow_node:
    Cij=5000
x=x=numpy.random.exponential(0.096/Cij,1)
dij=x[0]
p=sys.getsizeof(bx)/Cij
Lij=pij+p+dij
ti=gd.time+Lij
li=[]
for i in range(n):
    ev=Event(0,i,'BLK_REC',ti,bx,0)  # this event is for reciveing block by node j
    li.append(ev)
for j in li:
    gd.event_queue_list.append(j)

    
while(len(gd.event_queue_list)>0):
    #print("length of event queue at start is ",len(gd.event_queue_list))
    gd.event_queue_list=sorted(gd.event_queue_list,key=lambda x: x.time)  # sorting event_queue before poping of event
    #print(gd.blockId)
    if gd.blockId>300:
        break
    # if time.time()>tk:
    #     break 
    ev=gd.event_queue_list.pop(0)
    if ev.type=='TXN_REC':  # this event is for receiving transaction
        #print("i am in TXN_REC")
        ev_list=Node_list[ev.receiver].receive_transaction(ev.receiver,ev.sender,ev.time,n,ev.message)
        for i in ev_list:
            gd.event_queue_list.append(i)
    #print(len(gd.event_queue_list))
    if ev.type=='TXN_GEN':   # this is event is for generating new transaction 
        #print("i am in TXN_GEN")
        coins=random.randint(1,2)
        txid1=txid
        txid=txid+1
        ev_list= Node_list[ev.receiver].transaction_generate(ev.time,ev.type,coins,txid1,n)       
        for i in ev_list:
            gd.event_queue_list.append(i)
    if ev.type=='BLK_REC':  # this event is for receiveing block
        #print("Now i am running event of block recieving the block id ",ev.message.bkid," on the node ", ev.receiver)
        #time.sleep(10)
        if ev.message.bkid not in gd.block_id_list[ev.receiver]:
            ev_list= Node_list[ev.receiver].receive_block(ev.sender,ev.receiver,ev.time,n,ev.message)
            for i in ev_list:
                gd.event_queue_list.append(i)
     
    if ev.type=='BLK_GEN':  # this event is for mining and for generating blocksS
        #print("i am in  blk genration event of node ",ev.receiver," for the block ",ev.message.bkid)

        ev_list=Node_list[ev.receiver].Block_generation(ev.message,ev.parent_id,ev.time)  
        for i in ev_list:
            gd.event_queue_list.append(i)

    # if gd.blockId>800:
    #     print("Total blocks before break : ", gd.blockId)
    #     break


#code for making releasing all public chain to every one
recieved_from_selfish=[]
for i in range(1,n):
    tot=0
    for j in gd.block_list[i]:
        if j.bkid in Node_list[0].created_block_list_id:
            tot=tot+1  
    #print("for node ",i," received block from ",tot)                  
largest_time=0
for i in range(n):
    for j in Node_list[i].Block_tree_dict.keys():
        if largest_time<Node_list[i].Block_tree_dict[j][3]:
            largest_time=Node_list[i].Block_tree_dict[j][3]
gd.time=largest_time 
print("largest time",largest_time)  
templist=[]  
print("size of event_queue before empty",len(gd.event_queue_list))     
for x in gd.event_queue_list:
    if x.type=='BLK_REC' or x.type=='BLK_GEN':
        if x.message.bkid not in templist:
            templist.append(x.message.bkid)

print("number of blocks not added in blockchains= ",len(templist))
gd.event_queue_list.clear()
print("finally after simulation private chain of sielmaldmflakdf")
for j in Node_list[0].private_chain:
    print(j.bkid)
for i in range(n):
    if i==0:    
        for j in Node_list[i].private_chain:
            li=[]
            for k in range(n):
                if i!=k and j.bkid not in gd.block_id_list[k]:
                    Cij=100000
                    if  i in gd.slow_node or i in gd.slow_node:
                        Cij=5000
                    x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(j)/Cij
                    Lij=gd.pij+p+dij
                    gd.time += 1
                    ti=gd.time+Lij
                    ev=Event(i,k,'special',ti,j,j.parent_bkid)
                    # print(" selfish has added in the event queue")
                    gd.event_queue_list.append(ev)

    else:
        public_chain=[]
        max_height=1
        x=Node_list[i].genesis_block
        for j in Node_list[i].Block_tree_dict.keys():
            if max_height<Node_list[i].Block_tree_dict[j][1]:
                max_height=Node_list[i].Block_tree_dict[j][1]
                x=Node_list[i].Block_tree_dict[j][0]
        k=x.bkid
        while k!=0:
            public_chain.append(x)
            k=x.parent_bkid
            x=Node_list[i].Block_tree_dict[k][0]
        public_chain.append(Node_list[i].genesis_block)    
        public_chain.reverse()
        for j in public_chain:
            li=[]
            for k in Node_list[i].adja:
                if i!=k and j.bkid not in gd.block_id_list[k]:
                    Cij=100000
                    if  i in gd.slow_node or i in gd.slow_node:
                        Cij=5000
                    x=numpy.random.exponential(0.096/Cij,1)
                    dij=x[0]
                    p=sys.getsizeof(j)/Cij
                    Lij=gd.pij+p+dij
                    ti=gd.time+Lij
                    ev=Event(i,k,'special',ti,j,j.parent_bkid)
                    gd.event_queue_list.append(ev)

# i=0
# for j in Node_list[i].private_chain:
            
#             li=[]
#             for k in Node_list[i].adja:
#                 if i!=k and j.bkid not in gd.block_id_list[k]:
#                     Cij=100000
#                     if  i in gd.slow_node or i in gd.slow_node:
#                         Cij=5000
#                     x=numpy.random.exponential(0.096/Cij,1)
#                     dij=x[0]
#                     p=sys.getsizeof(j)/Cij
#                     Lij=gd.pij+p+dij
#                     Lij=1
#                     ti=gd.time+Lij
                    # print("private block event is added in queue the block ",j.bkid," and receiver is ",k)
                    # ev=Event(i,k,'special',ti,j,j.parent_bkid)
                    # gd.event_queue_list.append(ev)

while(len(gd.event_queue_list)>0):
    #print("length of event queue at start is ",len(gd.event_queue_list))
    gd.event_queue_list=sorted(gd.event_queue_list,key=lambda x: x.time) 
    ev=gd.event_queue_list.pop(0)
    if ev.type=='special':  # this event is for receiving transaction
        #print("i am in TXN_REC")
        ev_list=Node_list[ev.receiver].special_event(ev.receiver,ev.sender,ev.time,n,ev.message)
        for i in ev_list:
            gd.event_queue_list.append(i)



#code for adding blocks from pending list:

for i in range(n):
    flag=0
    while(1):
        for j in Node_list[i].pending_block_list:
            if j.parent_bkid in Node_list[i].Block_tree_dict.keys():
                flag=1
                temp_li=[]
                temp_li.append(j)
                temp_li.append(1+Node_list[i].Block_tree_dict[j.parent_bkid][1])
                temp_li.append(Node_list[i].Block_tree_dict[j.parent_bkid][2])
                #tk=Node_list[i].Block_tree_dict[j.parent_bkid][3]+1
                for k in Node_list[i].Block_tree_dict.keys():
                    if largest_time<Node_list[i].Block_tree_dict[k][3]:
                        largest_time=Node_list[i].Block_tree_dict[k][3]
                temp_li.append(largest_time)
                Node_list[i].Block_tree_dict.update({j:temp_li})
                Node_list[i].pending_block_list.remove(j)
                flag=1
        if flag==0:
            break
        else:
            flag=0
            continue    

print("-------------------ratio information----------------")
blocks_mined_by_adversary_in_mainchain=0
y_list=list( Node_list[0].private_chain)
if  Node_list[0].private_chain< Node_list[0].public_chain:
    y_list=list( Node_list[0].public_chain)
for j in y_list:
    if j.bkid in Node_list[0].created_block_list_id:
        print(j.bkid)
        blocks_mined_by_adversary_in_mainchain=blocks_mined_by_adversary_in_mainchain+1
Total_number_of_blocks_mined_by_an_adversary=0  
#print("afj;lasjsj")
for j in Node_list[0].Block_tree_dict.keys():
    if j in Node_list[0].created_block_list_id:
        #print(j)
        Total_number_of_blocks_mined_by_an_adversary=Total_number_of_blocks_mined_by_an_adversary+1
if Total_number_of_blocks_mined_by_an_adversary!=0:
  MPU_RATIO_adversiory=blocks_mined_by_adversary_in_mainchain/Total_number_of_blocks_mined_by_an_adversary
  print(blocks_mined_by_adversary_in_mainchain,Total_number_of_blocks_mined_by_an_adversary)
  print("MPU RATIO FOR ADERSIORY IN SELFISH MINING = ",MPU_RATIO_adversiory) 
else:
    print("Total_number_of_blocks_mined_by_an_adversary is zero")




Number_of_block_in_the_main_chain=len(Node_list[0].public_chain)
Total_number_of_blocks_generated_across_all_the_nodes=0
x_list=[]
for i in range(n):
    for j in Node_list[i].Block_tree_dict.keys():
        if j not in x_list:
            x_list.append(j)
    # for j in Node_list[i].created_block_list_id:
    #     if j in Node_list[i].Block_tree_dict.keys():
    #         Total_number_of_blocks_generated_across_all_the_nodes=Total_number_of_blocks_generated_across_all_the_nodes+1
Total_number_of_blocks_generated_across_all_the_nodes=len(x_list)    
if Total_number_of_blocks_generated_across_all_the_nodes != 0:
    MPU_RATIO_OVERALL=Number_of_block_in_the_main_chain/Total_number_of_blocks_generated_across_all_the_nodes
    print("MPU ratio for overall in selfish mining = ",MPU_RATIO_OVERALL)            
else:
    print("Total_number_of_blocks_generated_across_all_the_nodes is zero.")

lg_chain=[]
lg_chain=list(Node_list[0].private_chain)
if len(Node_list[0].public_chain)>len(Node_list[0].private_chain):
    lg_chain=list(Node_list[0].public_chain)
ad_in_mainchain=0
for i in lg_chain:
    if i.bkid in Node_list[0].created_block_list_id:
        ad_in_mainchain=ad_in_mainchain+1

if len(lg_chain) != 0:
    selfish_proportion=ad_in_mainchain/len(lg_chain)
    print("selfish_proportion=",selfish_proportion)
else:
    print("len(lg_chain) is zero.")

print("-------------------------------------------------------------------------")


print("blocks that are created or mined by selfish miner:")
for i in Node_list[0].created_block_list_id:
    if i in Node_list[0].Block_tree_dict.keys():
        print(i)

# 

   

# print("number of blocks in dictinary in given node") 
# list_1=[]     
# for i in range(n):
#     list_1.append(len(Node_list[i].Block_tree_dict))
# print(list_1)
   
print("all finished")
print("Total blocks after break : ", gd.blockId)
print(gd.blockId)
print("number of invalid blocks seen by each node=",gd.total_invalid)
print("slow nodes list")
print(gd.slow_node)
print("slow cpu nodes list")
print(gd.low_cpu)
print("selfish power= ",gd.selfish_power)
print("low cpu hashing power= ",gd.slow_rate)

# i=0
# for j in gd.block_id_list:
#     print(j)
#     print("pending list")
#     print(Node_list[i].pending_block_id_list)
#     # print("invalid received blockid")
#     # print(gd.invalid_blocks_id[j])
#     i=i+1
# for j in range(n):
#     print(Node_list[j].Block_tree_dict[0][2])    
    

# below code is for visiluzation and printing results in files
for i in range(n):
    #dict1={}
    file_name="block_tree_details_file"+str(i)+".txt"  #file name creation
    f = open(file_name, "a") # creating file 
    f.truncate(0)
    for j in  Node_list[i].Block_tree_dict.keys():  # storing all blocks in a file from blockchain of node i
        f.write(f"Node id={ Node_list[i].Block_tree_dict[j][0].bkid} , arrival_time={int(Node_list[i].Block_tree_dict[j][3])}  \n")
    f.close()
    l=len(Node_list[i].Block_tree_dict)
    #below code is visualize for block chain of node i
    labeldict = {}
    for k in Node_list[i].Block_tree_dict.keys():

        if(k==0):
            labeldict[k] = 'G'
        else:
            labeldict[k] = (k,int(Node_list[i].Block_tree_dict[k][3]))

    fname = "Blockchain_node_"+str(i)+".gv"
    f = open(fname, "a")
    f.truncate(0)
    f.write("digraph { ")
    f.write("\nrankdir=\"LR\"")
    for m in Node_list[i].Block_tree_dict.keys():
        if m != 0:
            if m in Node_list[i].created_block_list_id:
                f.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=green]")
            else:
             f.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=yellow]")
            #f.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\"]")
        else:
            f.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=red]")

    # G = GraphVisualization()
    for j in Node_list[i].Block_tree_dict.keys():
        if j!=0:
            # G.addEdge(Node_list[i].Block_tree_dict[j][0].parent_bkid,j)
            f.write("\n" + str(Node_list[i].Block_tree_dict[j][0].parent_bkid) + " -> " + str(j))
    string1="Blockchain_node_"+str(i)+".png"
    # G.visualize(labeldict,string1)

    f.write("\n}")
    f.close()
    #below code is for visualize longest chain in blockchain of node i

    ma=0
    node_id=0
    for j in Node_list[i].Block_tree_dict.keys():
        if ma<Node_list[i].Block_tree_dict[j][1]:
            ma=Node_list[i].Block_tree_dict[j][1]
            node_id=j
    max_chain=[]
    max_chain.append(node_id)
    k=node_id
    while(k!=0):
        max_chain.append(Node_list[i].Block_tree_dict[k][0].parent_bkid)
        k=Node_list[i].Block_tree_dict[k][0].parent_bkid
    
    labeldict1 = {}
    for k in max_chain:

        if(k==0):
            labeldict1[k] = 'G'
        else:
            labeldict1[k] = (k,int(Node_list[i].Block_tree_dict[k][3]))

    fname2 = "Longest_Chain_"+str(i)+".gv"
    f2 = open(fname2, "a")
    f2.truncate(0)
    f2.write("digraph { ")
    f2.write("\nrankdir=\"LR\"")
    # if i==0:
    #     max_chain=Node_list[0].public_chain
    for m in max_chain:
        if m != 0:
            if m in Node_list[i].created_block_list_id:
                f2.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=green]")
            else:
             f2.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=yellow]")
        else:
            f2.write("\n" + str(m) +" [label=\"(" + str(m) + "," + str(int(Node_list[i].Block_tree_dict[m][3])) + ")\",style=filled, fillcolor=red]")


    # G1 = GraphVisualization()
    for j in max_chain:
        if j!=0:
            # G1.addEdge(Node_list[i].Block_tree_dict[j][0].parent_bkid,j)
            f2.write("\n" + str(Node_list[i].Block_tree_dict[j][0].parent_bkid) + " -> " + str(j))
    string1="longest_chain_node_"+str(i)+".png"
    # G1.visualize(labeldict1,string1)   
    f2.write("\n}")
    f2.close()

   

for i in range(n):
    string_blockchain = "Blockchain_node_"+str(i)+".gv"
    blockchain_graph = Source.from_file(string_blockchain)
    # blockchain_graph.view()
    # output_file_name = "Blockchain_node_"+str(i)+".png"
    blockchain_graph.render(string_blockchain, format="png")
    string_longest_chain = "Longest_Chain_"+str(i)+".gv"
    longest_chain_graph = Source.from_file(string_longest_chain)
    # longest_chain_graph.view()   
    longest_chain_graph.render(string_longest_chain, format="png")

 
