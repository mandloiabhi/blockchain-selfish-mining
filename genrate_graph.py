import random
def generate_graph(n):
    k=0
    while(1):
        k=k+1
        adjacency=[]
        adjacency=generate_graph1(n)
        visited=[]
        for i in range(n):
            visited.append(0)
        queue=[]   
        queue.append(0)
        while len(queue)>0:
            x=queue.pop(0)
            visited[x]=1
            for i in range(n):
                if i!=x and adjacency[x][i]==1:
                    if visited[i]==0:
                        queue.append(i)
        flag=1
        for i in range(n):
            if visited[i]==0:
                flag=0  
        if flag==1:
            # print(adjacency)
            # print(k)
            
            return adjacency

def generate_graph1(n):
    degree=[]
    adjacency=[]
    choices=[]
    for i in range(n):
        temp1=[]
        temp2=[]
        for j in range(n):
            temp1.append(0)
            if i!=j:
                temp2.append(j)
        adjacency.append(temp1)
        choices.append(temp2)
        degree.append(0)
    for i in range(n):
        if degree[i]<7:
            if degree[i]>=4:
                x=len(choices[i])
                y=7-degree[i]
                if x<y:
                    z=x
                else:
                    z=y
                k=random.randint(0,z)
                p=random.sample(choices[i],k) 
                for m in p:
                    adjacency[m][i]=1
                    adjacency[i][m]=1
                    degree[m]=degree[m]+1
                    degree[i]=degree[i]+1 
                    choices[i].remove(m)
                    choices[m].remove(i)
                    if degree[m]==7:
                        for j in range(n):
                            if m in choices[j]:
                                choices[j].remove(m)
                    if degree[i]==7:
                        for j in range(n):
                            if i in choices[j]:
                                choices[j].remove(i)

            else:
                x=len(choices[i])
                y=7-degree[i]
                if x<y:
                    z=x
                else:
                    z=y
                k=random.randint(4-degree[i],z)
                temp=[]
                for q in choices[i]:
                    temp.append(q)
                temp.sort()    
                p=random.sample(choices[i],k)
                for m in p:
                    adjacency[m][i]=1
                    adjacency[i][m]=1
                    degree[m]=degree[m]+1
                    degree[i]=degree[i]+1
                    choices[i].remove(m)
                    choices[m].remove(i)
                    if degree[m]==7:
                        for j in range(n):
                            if m in choices[j]:
                                choices[j].remove(m)
                    if degree[i]==7:
                        for j in range(n):
                            if i in choices[j]:
                                choices[j].remove(i)
    #print(adjacency)
    return adjacency                                
 