#include <iostream>

using namespace std;

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
SingletonStatic* SingletonStatic::m_instance = NULL;

int main(int argc ,char* argv[])
{
    SingletonStatic::m_instance = 


  return 0;
}
