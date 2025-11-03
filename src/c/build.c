// build.c
// last updated: 03/11/2025 <d/m/y>
// win32: gcc -o build.exe build.c -static -static-libgcc -static-libstdc++ -O2 -s
// linux / linux2: gcc o- build build.c -static -O2 -s
// the result file (.exe) / (elf) must be ran in the root dir where gui.py lives; elsewhere it will fail
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#ifdef _WIN32
#include <windows.h>
#define SLEEP(ms) Sleep(ms)
#else
#include <unistd.h>
#define SLEEP(ms) usleep((ms) * 1000)
#endif
#define MAX_CMD 8192
void clear_screen()
{
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}
void press_enter()
{
    printf("\nPress enter to continue...");
    int c;
    while ((c = getchar()) != '\n' && c != EOF)
        getchar();
}
int main()
{
    char os[16] = {0};
    char console[16] = {0};
    char jobs[16] = {0};
    char cmd[MAX_CMD] = {0};
    const char *icon = "pykryptor_icon.ico";
    const char *gui_file = "gui.py";
    clear_screen();
    printf("PyKryptor build script - v1.4\n\n");
    SLEEP(1000);
    printf("This script requries Python and pip3 in your systems PATH.\n\n");
    SLEEP(1000);
    printf("PyKryptor is free, open source, MIT and easy to use :o\n\n");
    printf("If you haven't check it out at;");
    printf("https://github.com/Commonwealthrocks/PyKryptor/");
    SLEEP(4000);
    clear_screen();
    printf("Your kumpjuter:\n");
    printf("  [1] Windows (.exe)\n");
    printf("  [2] Linux (ELF)\n");
    printf("Choice (1-2): ");
    int choice;
    if (scanf("%d", &choice) != 1 || choice < 1 || choice > 2)
    {
        printf("Invalid input. Defaulting to Windows.\n");
        choice = 1;
    }
    getchar();
    strcpy(os, (choice == 1) ? "win" : "linux");
    printf("\nKeep console window? (for debugging)\n");
    printf("  [1] No (GUI only)\n");
    printf("  [2] Yes (with console)\n");
    printf("Choice (1-2): ");
    if (scanf("%d", &choice) != 1 || choice < 1 || choice > 2)
    {
        printf("Invalid. Defaulting to GUI only.\n");
        choice = 1;
    }
    getchar();
    strcpy(console, (choice == 2) ? "enable" : "disable");
    printf("\nParallel jobs (1-16, 0 = auto): ");
    if (scanf("%d", &choice) != 1 || choice < 0 || choice > 16)
    {
        printf("You just won't listen? Using auto.\n");
        choice = 0;
    }
    getchar();
    snprintf(jobs, sizeof(jobs), "%d", choice);
    if (strcmp(os, "win") == 0)
    {
        snprintf(cmd, MAX_CMD,
                 "nuitka --onefile --standalone --assume-yes-for-downloads "
                 "--mingw64 --windows-console-mode=%s "
                 "--windows-icon-from-ico=%s "
                 "--jobs=%s "
                 "--enable-plugin=pyside6 "
                 "--include-data-dir=txts=txts "
                 "--include-data-dir=sfx=sfx "
                 "--include-data-dir=img=img "
                 "--include-data-files=c/win32/secure_mem.dll=c/win32/secure_mem.dll "
                 "--include-data-files=c/penguin/secure_mem.so=c/penguin/secure_mem.so "
                 "--include-data-files=c/win32/chc_aes_ni.dll=c/win32/chc_aes_ni.dll "
                 "--include-data-files=c/penguin/chc_aes_ni.so=c/penguin/chc_aes_ni.so "
                 "--output-dir=dist %s",
                 console,
                 icon,
                 (choice == 0) ? "" : jobs,
                 gui_file);
    }
    else
    {
        snprintf(cmd, MAX_CMD,
                 "nuitka --onefile --standalone "
                 "--jobs=%s "
                 "--enable-plugin=pyside6 "
                 "--include-data-dir=txts=txts "
                 "--include-data-dir=sfx=sfx "
                 "--include-data-dir=img=img "
                 "--include-data-files=c/penguin/secure_mem.so=c/penguin/secure_mem.so "
                 "--include-data-files=c/penguin/chc_aes_ni.so=c/penguin/chc_aes_ni.so "
                 "--output-dir=dist %s",
                 (choice == 0) ? "" : jobs,
                 gui_file);
    }
    clear_screen();
    printf("BUILD COMMAND:\n\n");
    printf("%s\n\n", cmd);
    printf("Ready to build PyKryptor? [y/n]: ");
    char confirm = getchar();
    getchar();
    if (tolower(confirm) == 'n')
    {
        printf("Build canceled.\n");
        press_enter();
        return 0;
    }
    printf("\nBuilding PyKryptor... (2-10 minutes)\n\n");
    int result = system(cmd);

    if (result == 0)
    {
        printf("\nBuild success; dist/gui.exe (Windows) or dist/gui (Linux)\n");
        printf("Rename to: PyKryptor.exe / PyKryptor\n");
    }
    else
    {
        printf("\nBuild failed; check errors above.\n");
    }
    press_enter();
    return result;
}

// end