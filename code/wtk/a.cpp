#include <iostream>

using namespace std;

class A
{
public:
  A ():m_iVal(0){test();}
  virtual void func() { std::cout<<"base\t" << m_iVal<<endl;}
  void test(){func();}
public:
int m_iVal;
};

class B : public A
{
public:
  B(){test();}
  virtual void func()
  {
    ++m_iVal;
    std::cout<<"derived\t" << m_iVal<<endl;
  }
};

int main(int argc ,char* argv[])
{
  A*p = new B;
  p->test();
  return 0;
}
