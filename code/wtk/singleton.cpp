/*
单例模式
懒汉版（Lazy Singleton）：单例实例在第一次被使用时才进行初始化，这叫做延迟初始化。
饿汉版（Eager Singleton）：指单例实例在程序运行时被立即执行初始化

https://segmentfault.com/a/1190000015950693
https://www.cnblogs.com/liyuan989/p/4264889.html
https://songlee24.github.io/2014/03/11/singleton-pattern/
http://blog.jobbole.com/96754/
*/

// 懒汉模式
// ==========静态成员实例===========
class Singleton
{
private:
        static Singleton* m_instance;
        Singleton(){}
public:
        static Singleton* getInstance();
};
 
Singleton* Singleton::getInstance()
{
        if(NULL == m_instance)
        {
                Lock();//借用其它类来实现，如boost
                if(NULL == m_instance)
                {
                        m_instance = new Singleton;
                }
                UnLock();
        }
        return m_instance;
}


// ==========内部静态成员实例===========
class SingletonInside
{
private:
        SingletonInside(){}
public:
        static SingletonInside* getInstance()
        {
                Lock(); // not needed after C++0x
                static SingletonInside instance;
                UnLock(); // not needed after C++0x
                return instance; 
        }
};


//饿汉模式
class SingletonStatic
{
private:
        static const SingletonStatic* m_instance;
        SingletonStatic(){}
public:
        static const SingletonStatic* getInstance()
        {
                return m_instance;
        }
};

//外部初始化 before invoke main
const SingletonStatic* SingletonStatic::m_instance = new SingletonStatic;
