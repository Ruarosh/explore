/*
* 信号量原理
https://blog.csdn.net/u014495460/article/details/82883282
http://www.cnblogs.com/lenmom/p/7998969.html

使用P操作=试图使用资源，若无资源则等待。
使用V操作=释放资源，若有进程排队则将其出队并唤醒。
负数的绝对值为等待的进程数

* PV操作原理
http://www.cnblogs.com/litaoyang/p/6606499.html
*/

#include <stdint.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

sem_t sem;

void *testfunc(void *arg)
{
    while(1)
    {
        // 若sem>0，那么它减1并立即返回。 
        // 若sem==0，则睡眠直到sem>0，此时立即减1，然后返回;
        sem_wait(&sem); // 阻塞等待
        //do something....
        printf("hello world...\n");
    }
}

int main()
{
    pthread_t ps;
    sem_init(&sem, 0, 0);
    pthread_create(&ps,NULL,testfunc,NULL);
    while(1)
    {
        // 每隔一秒sem_post 信号量sem加1 子线程sem_wait解除阻塞 打印hello world
        // 把指定的信号量sem的值加1; 
        sem_post(&sem);  // 解除阻塞
        sleep(1);
    }
    pthread_join(ps,NULL); 
    return 0;
}
