using System;
using System.IO;
using DotNetEnv;

class Program
{
    static void Main(string[] args)
    {
        Env.Load();
        
        string note = string.Join(" ", args);
        
    }
}