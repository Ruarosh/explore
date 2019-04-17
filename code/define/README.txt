== compile ==
g++ -pthread exa.cpp  -std=c++11 -o exa

== file list ==
Semaphore(信号量)       Semaphore.cpp
mutex互斥锁             mutex.cpp
条件锁                  condition_lock.cpp condition_lock2.cpp
explicit使用            explicit.cpp
lock_guard              lock_guard.cpp
unique_lock             unique_lock.cpp //相对lock_guard，有更多更灵活的接口可使用
lock                    lock介绍，可以同时锁住多个对象，内部避免死锁
atomic                  atomic.cpp
promise_future          promise_future.cpp
async                   async.cpp


