#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "openssl/evp.h"
#include "openssl/md5.h"
#include "openssl/sha.h"
#include "openssl/crypto.h"
#include "zlib.h"
#include <openssl/ssl.h>


void digest_message(const EVP_MD *(*digest_func)(void), const unsigned char *message, size_t message_len, unsigned char **digest, unsigned int *digest_len)
{
	EVP_MD_CTX *mdctx;

	if((mdctx = EVP_MD_CTX_create()) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestInit_ex(mdctx, digest_func(), NULL))
		printf("Error!\n");

	if(1 != EVP_DigestUpdate(mdctx, message, message_len))
		printf("Error!\n");

	if((*digest = (unsigned char *)OPENSSL_malloc(EVP_MD_size(digest_func()))) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestFinal_ex(mdctx, *digest, digest_len))
		printf("Error!\n");

	EVP_MD_CTX_destroy(mdctx);
}

void SHA3_256(const unsigned char *message, size_t message_len, unsigned char **digest, unsigned int *digest_len)
{
	EVP_MD_CTX *mdctx;

	if((mdctx = EVP_MD_CTX_create()) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestInit_ex(mdctx, EVP_sha3_256(), NULL))
		printf("Error!\n");

	if(1 != EVP_DigestUpdate(mdctx, message, message_len))
		printf("Error!\n");

	if((*digest = (unsigned char *)OPENSSL_malloc(EVP_MD_size(EVP_sha3_256()))) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestFinal_ex(mdctx, *digest, digest_len))
		printf("Error!\n");

	EVP_MD_CTX_destroy(mdctx);
}

void SHA3_512(const unsigned char *message, size_t message_len, unsigned char **digest, unsigned int *digest_len) {
	EVP_MD_CTX *mdctx;

	if((mdctx = EVP_MD_CTX_create()) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestInit_ex(mdctx, EVP_sha3_512(), NULL))
		printf("Error!\n");

	if(1 != EVP_DigestUpdate(mdctx, message, message_len))
		printf("Error!\n");

	if((*digest = (unsigned char *)OPENSSL_malloc(EVP_MD_size(EVP_sha3_512()))) == NULL)
		printf("Error!\n");

	if(1 != EVP_DigestFinal_ex(mdctx, *digest, digest_len))
		printf("Error!\n");

	EVP_MD_CTX_destroy(mdctx);
}

int main()
{
	unsigned char md5_digest[MD5_DIGEST_LENGTH];
	unsigned char sha1_digest[SHA_DIGEST_LENGTH];
	unsigned char sha256_digest[SHA256_DIGEST_LENGTH];
	unsigned char sha512_digest[SHA512_DIGEST_LENGTH];
	unsigned char *sha3_256_digest, *sha3_512_digest;
	unsigned int sha3_256_digest_len = 0, sha3_512_digest_len = 0;
	char string[] = "happy";

	sha3_256_digest = (unsigned char *) calloc(SHA256_DIGEST_LENGTH, sizeof(unsigned char));
	sha3_512_digest = (unsigned char *) calloc(SHA512_DIGEST_LENGTH, sizeof(unsigned char));

	if (!sha3_256_digest || !sha3_512_digest) {
		printf("Error!\n");
		return 0;
	}

	SSL_library_init();

	MD5((unsigned char*)&string, strlen(string), (unsigned char*)&md5_digest);
	SHA1((unsigned char*)&string, strlen(string), (unsigned char*)&sha1_digest);
	SHA256((unsigned char*)&string, strlen(string), (unsigned char*)&sha256_digest);
	SHA512((unsigned char*)&string, strlen(string), (unsigned char*)&sha512_digest);
	SHA3_256((unsigned char*)&string, strlen(string), &sha3_256_digest, &sha3_256_digest_len);
	SHA3_512((unsigned char*)&string, strlen(string), &sha3_512_digest, &sha3_512_digest_len);
 
	char md5_string[33] = {0}, sha1_string[41] ={0},
	sha256_string[65] = {0}, sha512_string[129] = {0},
	sha3_256_string[65] = {0}, sha3_512_string[129] = {0};
 
	for(int i = 0; i < MD5_DIGEST_LENGTH; i++)
		 sprintf(&md5_string[i*2], "%02x", (unsigned int)md5_digest[i]);
 
	for(int i = 0; i < SHA_DIGEST_LENGTH; i++)
		 sprintf(&sha1_string[i*2], "%02x", (unsigned int)sha1_digest[i]);
 
	for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
		 sprintf(&sha256_string[i*2], "%02x", (unsigned int)sha256_digest[i]);
		 sprintf(&sha3_256_string[i*2], "%02x", (unsigned int)sha3_256_digest[i]);
	}

	for(int i = 0; i < SHA512_DIGEST_LENGTH; i++) {
		 sprintf(&sha512_string[i*2], "%02x", (unsigned int)sha512_digest[i]);
		 sprintf(&sha3_512_string[i*2], "%02x", (unsigned int)sha3_512_digest[i]);
	}

	printf("md5 digest: %s\n", md5_string);
	printf("sha1 digest: %s\n", sha1_string);
	printf("sha256 digest: %s\n", sha256_string);
	printf("sha512 digest: %s\n", sha512_string);
	printf("sha3 256 digest: %s\n", sha3_256_string);
	printf("sha3 512 digest: %s\n", sha3_512_string);
	printf("SSL library version: %s\n", SSLeay_version(SSLEAY_VERSION));
	printf("ZLIB version: %s\n", ZLIB_VERSION);

	free(sha3_256_digest);
	free(sha3_512_digest);

	return 0;
}
