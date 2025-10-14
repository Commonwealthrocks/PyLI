// chc_aes_ni.c
// last updated: 14/10/2025 <d/m/y>
// p-y-l-i
// win32: gcc -shared -o chc_aes_ni.dll chc_aes_ni.c -O2 -Wall
// linux / linux2: gcc -shared -fPIC -o chc_aes_ni.so chc_aes_ni.c -O2 -Wall
#if defined(_WIN32)
#include <windows.h>
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT __attribute__((visibility("default")))
#endif
#if (defined(__GNUC__) || defined(__clang__)) && (defined(__x86_64__) || defined(__i386__))
#include <cpuid.h>
#endif
DLLEXPORT int has_aes_ni()
{
#if (defined(__GNUC__) || defined(__clang__)) && (defined(__x86_64__) || defined(__i386__))
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx))
    {
        return (ecx & (1 << 25)) != 0;
    }
    return 0;
#elif defined(_MSC_VER)
    int cpuInfo[4];
    __cpuid(cpuInfo, 1);
    return (cpuInfo[2] & (1 << 25)) != 0;
#else
    return 0;
#endif
}

// end