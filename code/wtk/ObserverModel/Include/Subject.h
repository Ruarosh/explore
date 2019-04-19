#ifndef __SUBJECT_H__
#define __SUBJECT_H__

#include "Observer.h"

/*
 * 抽象主题类
 * 把所有的观察者对象的引用保存在一个聚集里,每个主题都可以有任意数量
 * 的观察者,抽象主题提供一个接口,可以增加和删除观察者对象
 */
class CSubject
{
public:
    virtual ~CSubject() {}

    // 添加观察者抽象函数
    virtual void RegisterObserver(CObserver *observer) = 0;

    // 移除观察者抽象函数
    virtual void RemoveObserver(CObserver *observer) = 0;

    // 通知所有的观察者
    virtual void NotifyObserver(const std::string& msg) = 0;
};

#endif
