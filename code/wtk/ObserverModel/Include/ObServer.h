#ifndef __OBSERVER_H__
#define __OBSERVER_H__

#include <iostream>

/*
 * 抽象观察者
 * 为所有的具体观察者定义一个接口,在得到主题的通知时更新自己
 */
class CObserver
{
public:
    virtual ~CObserver() {};

    // 用以更新当前类的抽象函数
    virtual void Update(const std::string &msg) = 0;

    virtual std::string getName() = 0;

};

#endif
