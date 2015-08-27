#include<iostream>
#include<fstream>
using namespace std;

int main()
{
	ifstream fp1;
	ofstream fp2;
	string line;
	int flag = 0, i;
	fp1.open("add32.asm", ios::in);
	fp2.open("add64_new.asm", ios::out);
	if(fp1.is_open())
	{
		while(getline(fp1, line))
		{
			if (line.find("section .data") != string::npos) 
				flag = 1;
			else if (line.find("section .bss") != string::npos)
				flag = 2;
			else if (line.find("section .text") != string::npos) 
				flag = 3;
			if(flag == 1)
			{
				if (line.find("dd") != string::npos)
				{
					for (string::iterator it= line.begin(); it!= line.end(); ++it)
					{
						if(*it == 'd' && *(it + 1) == 'd')
						{
							*(it + 1) = 'q';
						}
					}
				}
				fp2 << line << '\n';
			}
			else if(flag == 2)
			{
				if (line.find("resd") != string::npos)
				{
					for (string::iterator it= line.begin(); it!= line.end(); ++it)
					{
						if(*it == 'r' && *(it + 1) == 'e' && *(it + 2) == 's' && *(it + 3) == 'd')
						{
							*(it + 3) = 'q';
						}
					}
				}
				fp2 << line << '\n';
			}
			else if(flag == 3)
			{
				if (line.find("mov") != string::npos || line.find("add") != string::npos)
				{
					for (string::iterator it= line.begin(); it!= line.end(); ++it)
					{
						if(*it == 'e' &&  'a' <= *(it + 1) <= 'd' && *(it + 2) == 'x')
						{
							*it = 'r';
						}
					}
				}
				if (line.find("main:") != string::npos )
				{
					fp2 << line << '\n';
					fp2 << "	push	rbp\n";
				}
				else if (line.find("ret") != string::npos )
				{
					fp2 << "	pop	rbp\n";
					fp2 << line << '\n';	
				}
				else
				{
					fp2 << line << '\n';
				}
			}
		}
		fp1.close();
		fp2.close();
	}
	else cout << "Not possible";
	return 0;
}