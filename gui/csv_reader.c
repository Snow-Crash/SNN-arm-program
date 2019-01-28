#include <stdio.h>
#include <string.h>
#include <time.h>
 
#define bufSize 1024

void delay(int number_of_seconds) 
{ 
    // Converting time into milli_seconds 
    int milli_seconds = 1000 * number_of_seconds; 
  
    // Stroing start time 
    clock_t start_time = clock(); 
  
    // looping till required time is not acheived 
    while (clock() < start_time + milli_seconds) ; 
} 
 
int classify(int num)
{
  FILE* fp;
  char buf[bufSize];
  char buf2[32];

//  if (num != 2)
//  {
//    fprintf(stderr,
//            "Usage: %d <soure-file>\n", num);
//    return 1;
//  }

//  int tmp = (rand() % (2-0+1)) + 0 ;
  int tmp = 0;
  sprintf(buf2, "layer_2_class_%d_sample_%d.csv", num, tmp);

  if ((fp = fopen(buf2, "r")) == NULL)
  { /* Open source file. */
    perror("fopen source-file");
    return 1;
  }
 
  while (fgets(buf, sizeof(buf), fp) != NULL)
  {
    buf[strlen(buf) - 1] = '\0'; // eat the newline fgets() stores
    printf("%s\n", buf);
    delay(10);
  }
  fclose(fp);
  return 0;
}