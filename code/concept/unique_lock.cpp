/*
https://zh.cppreference.com/w/cpp/thread/unique_lock
http://www.cnblogs.com/haippy/p/3346477.html

大部分情况下，两者的功能是一样的，不过unique_lock 比lock_guard 更灵活.
*/
#ifdef TEST1
#include <mutex>
#include <thread>
#include <chrono>
 
struct Box {
    explicit Box(int num) : num_things{num} {}
 
    int num_things;
    std::mutex m;
};
 
void transfer(Box &from, Box &to, int num)
{
    // 仍未实际取锁
    std::unique_lock<std::mutex> lock1(from.m, std::defer_lock); // 注意这里是defer_lock
    std::unique_lock<std::mutex> lock2(to.m, std::defer_lock);
 
    // 锁两个 unique_lock 而不死锁
    std::lock(lock1, lock2);
 
    from.num_things -= num;
    to.num_things += num;
 
    // 'from.m' 与 'to.m' 互斥解锁于 'unique_lock' 析构函数
}
 
int main()
{
    Box acc1(100);
    Box acc2(50);
 
    std::thread t1(transfer, std::ref(acc1), std::ref(acc2), 10);
    std::thread t2(transfer, std::ref(acc2), std::ref(acc1), 5);
 
    t1.join();
    t2.join();
}

#else

#include <iostream>       // std::cout
#include <thread>         // std::thread
#include <mutex>          // std::mutex, std::lock, std::unique_lock
                          // std::adopt_lock, std::defer_lock
std::mutex foo,bar;

void task_a () {
  std::lock (foo,bar);         // simultaneous lock (prevents deadlock)
  std::unique_lock<std::mutex> lck1 (foo,std::adopt_lock); //注意这里是adopt_lock
  std::unique_lock<std::mutex> lck2 (bar,std::adopt_lock);
  std::cout << "task a\n";
  // (unlocked automatically on destruction of lck1 and lck2)
}

void task_b () {
  // foo.lock(); bar.lock(); // replaced by:
  std::unique_lock<std::mutex> lck1, lck2;
  lck1 = std::unique_lock<std::mutex>(bar,std::defer_lock);
  lck2 = std::unique_lock<std::mutex>(foo,std::defer_lock);
  std::lock (lck1,lck2);       // simultaneous lock (prevents deadlock)
  std::cout << "task b\n";
  // (unlocked automatically on destruction of lck1 and lck2)
}


int main ()
{
  std::thread th1 (task_a);
  std::thread th2 (task_b);

  th1.join();
  th2.join();

  return 0;
}

#endif
