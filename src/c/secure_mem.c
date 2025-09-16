// secure_mem/secure_mem.c
// last updated: 16/09/2025 <d/m/y>
// p-y-l-i
// win32: gcc -shared -o secure_mem.dll secure_mem.c -O2 -Wall -static-libgcc -static-libstdc++ -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic
// linux / linux2: gcc -shared -fPIC -o secure_mem.so secure_mem.c -O2 -Wall
#include <string.h>
#if defined(_WIN32)
#include <windows.h>
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void zero_memory(void *buffer, size_t len)
{
    if (buffer == NULL || len == 0)
    {
        return;
    }
#if defined(_WIN32)
    SecureZeroMemory(buffer, len);
#elif defined(__OpenBSD__)
    explicit_bzero(buffer, len);
#elif defined(__GLIBC__) && __GLIBC__ >= 2 && __GLIBC_MINOR__ >= 25
    explicit_bzero(buffer, len);
#else
    volatile unsigned char *p = (volatile unsigned char *)buffer;
    while (len--)
    {
        *p++ = 0;
    }
    __asm__ __volatile__("" ::: "memory");
#endif
}