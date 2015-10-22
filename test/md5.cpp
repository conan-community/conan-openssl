#include <stdio.h>
#include <string.h>
#include "openssl/md5.h"
#include "openssl/crypto.h"
#include "zlib.h"
 
int main()
{
    unsigned char digest[MD5_DIGEST_LENGTH];
    char string[] = "happy";
    
    MD5((unsigned char*)&string, strlen(string), (unsigned char*)&digest);    
 
    char mdString[33];
 
    for(int i = 0; i < 16; i++)
         sprintf(&mdString[i*2], "%02x", (unsigned int)digest[i]);
 
    printf("md5 digest: %s\n", mdString);
    printf("SSL library version: %s\n", SSLeay_version(SSLEAY_VERSION));
    printf("ZLIB version: %s\n", ZLIB_VERSION);
 
    return 0;
}
