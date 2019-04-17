/*
https://blog.csdn.net/qq_34199383/article/details/79990986
https://www.cnblogs.com/haippy/p/3301408.html
functions:
    store
    load
    exchange
    compare_exchange_weak
    compare_exchange_strong
*/

#include <iostream>
#include <ctime>
#include <vector>
#include <thread>
#include <atomic>
 
 
std::atomic<size_t> count(0);
 
void threadFun()
{
        for (int i = 0; i < 10000; i++)
                count++;
}
 
int main(void)
{
        clock_t start_time = clock();
 
        // 启动多个线程
        std::vector<std::thread> threads;
        for (int i = 0; i < 10; i++)
                threads.push_back(std::thread(threadFun));
        for (auto&thad : threads)
                thad.join();
 
        // 检测count是否正确 10000*10 = 100000
        std::cout << "count number:" << count << std::endl;
 
        clock_t end_time = clock();
        std::cout << "耗时：" << end_time - start_time << "ms" << std::endl;
 
        return 0;
}
