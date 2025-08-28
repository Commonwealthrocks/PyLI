// secure_mem/secure_mem.c
// last updated: 28/8/2025 <d/m/y>
// p-y-l-i
#include <string.h>
#if defined(_WIN32)
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void zero_memory(volatile char *buffer, size_t len)
{
    if (buffer == NULL)
    {
        return;
    }
    for (size_t i = 0; i < len; ++i)
    {
        buffer[i] = 0;
    }
}

// end
